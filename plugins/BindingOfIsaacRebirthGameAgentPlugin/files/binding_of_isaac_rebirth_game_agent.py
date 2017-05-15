from lib.game_agent import GameAgent

import lib.cv

from lib.machine_learning.context_classification.context_classifiers import *

from .helpers.frame_processing import *

from .helpers.game_floor import GameFloor
from .helpers.game_minimap import GameMinimap

import offshoot

import time
import uuid
import subprocess
import itertools

import skimage.io


class BindingOfIsaacRebirthGameAgent(GameAgent):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        plugin_path = offshoot.config["file_paths"]["plugins"]

        ocr_classifier_path = f"{plugin_path}/BindingOfIsaacRebirthGameAgentPlugin/files/ml_models/binding_of_isaac_rebirth_ocr.model"
        self.machine_learning_models["ocr_classifier"] = self.load_machine_learning_model(ocr_classifier_path)

        context_classifier_path = f"{plugin_path}/BindingOfIsaacRebirthGameAgentPlugin/files/ml_models/binding_of_isaac_rebirth_context.model"

        context_classifier = CNNInceptionV3ContextClassifier(input_shape=(270, 480, 3))
        context_classifier.prepare_generators()
        context_classifier.load_classifier(context_classifier_path)

        self.machine_learning_models["context_classifier"] = context_classifier

        self.frame_handlers["PLAY"] = self.handle_play

        self.game_state = {
            "character_select_generator": itertools.cycle(self.characters),
            "seed_entered": False,
            "navigation": {
                "previous_map_image_data": None
            },
            "health": None,
            "inventory": {
                "pickups": {
                    "coins": 0,
                    "bombs": 0,
                    "keys": 0
                },
                "items": [],
                "trinkets": [],
                "single_use_item": None,
                "charge_item": None
            },
            "game_floor": None,
            "minimap": None
        }

    @property
    def characters(self):
        return ["ISAAC", "MAGDALENE", "CAIN", "JUDAS", "EVE", "SAMSON", "AZAZEL", "LAZARUS", "EDEN", "RANDOM"]

    @property
    def difficulties(self):
        return ["NORMAL", "HARD"]

    @property
    def game_contexts(self):
        return dict(

        )

    @property
    def game_context_handlers(self):
        return dict(
            intro=self.handle_context_intro,
            splash_screen=self.handle_context_splash_screen,
            file_select_screen=self.handle_context_file_select_screen,
            menu=self.handle_context_menu,
            character_select_screen=self.handle_context_character_select_screen,
            game=self.handle_context_game,
            death_screen=self.handle_context_death_screen
        )

    def handle_play(self, game_frame):
        if self.game_context is None or game_frame.compare_ssim(self.previous_game_frame) <= 0.75:
            self.game_context = self.machine_learning_models["context_classifier"].predict(game_frame.frame)

            if self.game_context == "character_select_screen":
                self.game_state["character_select_generator"] = itertools.cycle(self.characters)

        self.game_context_handlers.get(self.game_context, lambda gf: True)(game_frame)

    def handle_context_intro(self, game_frame):
        self.input_controller.tap_key(self.input_controller.keyboard.enter_key)
        time.sleep(1)

    def handle_context_splash_screen(self, game_frame):
        self.input_controller.tap_key(self.input_controller.keyboard.enter_key)
        time.sleep(1)

    def handle_context_file_select_screen(self, game_frame):
        self.input_controller.tap_key(self.input_controller.keyboard.enter_key)
        time.sleep(1)

    def handle_context_menu(self, game_frame):
        new_game_image = lib.cv.extract_region_from_image(
            game_frame.grayscale_frame,
            self.game.screen_regions["MENU_NEW_GAME"]
        )

        if 400 < new_game_image[new_game_image <= 128].size < 500:
            self.input_controller.tap_key(self.input_controller.keyboard.enter_key)
        else:
            self.input_controller.tap_key(self.input_controller.keyboard.up_key)

        self.game_state["seed_entered"] = False

        time.sleep(1)

    def handle_context_character_select_screen(self, game_frame):
        # Difficulty
        if "difficulty" in self.config:
            normal_difficulty_image = lib.cv.extract_region_from_image(
                game_frame.grayscale_frame,
                self.game.screen_regions["CHARACTER_SELECT_DIFFICULTY_NORMAL"]
            )

            hard_difficulty_image = lib.cv.extract_region_from_image(
                game_frame.grayscale_frame,
                self.game.screen_regions["CHARACTER_SELECT_DIFFICULTY_HARD"]
            )

            difficulty_images = [normal_difficulty_image, hard_difficulty_image]
            difficulty_is_selected = [image[image <= 128].size > 100 for image in difficulty_images]

            current_difficulty = self.difficulties[difficulty_is_selected.index(True)]

            if current_difficulty != self.config["difficulty"]:
                self.input_controller.tap_key(self.input_controller.keyboard.down_key)

        # Seed
        if "seed" in self.config and not self.game_state["seed_entered"]:
            self.input_controller.tap_key(self.input_controller.keyboard.tab_key)
            time.sleep(1)

            for character in self.config["seed"].lower():
                self.input_controller.tap_key(character)

            time.sleep(1)
            self.input_controller.tap_key(self.input_controller.keyboard.enter_key)
            time.sleep(1)
            self.game_state["seed_entered"] = True

        current_character = next(self.game_state["character_select_generator"])

        if current_character == self.config.get("character", "ISAAC"):
            self.input_controller.tap_key(self.input_controller.keyboard.enter_key)
        else:
            self.input_controller.tap_key(self.input_controller.keyboard.right_key)

        time.sleep(1)

    def handle_context_game(self, game_frame):
        if not self.game_state["game_floor"]:
            self.game_state["game_floor"] = GameFloor()

        minimap_image = get_map_grid_image_data(game_frame.grayscale_frame, self.game)

        if not self.game_state["minimap"]:
            self.game_state["minimap"] = GameMinimap(minimap_image=minimap_image)
        else:
            self.game_state["minimap"].update(minimap_image)

        room_layout = get_room_layout_type(game_frame.grayscale_frame, self.game)

        center = self.game_state["minimap"].center
        adjacent_cells = self.game_state["minimap"].get_adjacent_cells(room_layout)

        top_cell = adjacent_cells.get((0, 1))
        right_cell = adjacent_cells.get((1, 0))
        bottom_cell = adjacent_cells.get((0, -1))
        left_cell = adjacent_cells.get((-1, 0))

        # skimage.io.imsave(f"datasets/tmp/{str(uuid.uuid4())}.png", np.array(center.image_data * 255), dtype="uint8")
        # skimage.io.imsave(f"datasets/tmp/{str(uuid.uuid4())}.png", np.array(top_cell.image_data * 255), dtype="uint8")
        # skimage.io.imsave(f"datasets/tmp/{str(uuid.uuid4())}.png", np.array(right_cell.image_data * 255), dtype="uint8")
        # skimage.io.imsave(f"datasets/tmp/{str(uuid.uuid4())}.png", np.array(bottom_cell.image_data * 255), dtype="uint8")
        # skimage.io.imsave(f"datasets/tmp/{str(uuid.uuid4())}.png", np.array(left_cell.image_data * 255), dtype="uint8")

        subprocess.call(["clear"])
        print(f"I'm in a: {center.identify(self.game_state['minimap'].minimap_room_types)} ({room_layout})")

        print(f"On top of me: {top_cell.identify(self.game_state['minimap'].minimap_room_types) or 'NOTHING'}")
        print(f"On my right: {right_cell.identify(self.game_state['minimap'].minimap_room_types) or 'NOTHING'}")
        print(f"Under me: {bottom_cell.identify(self.game_state['minimap'].minimap_room_types) or 'NOTHING'}")
        print(f"On my left: {left_cell.identify(self.game_state['minimap'].minimap_room_types) or 'NOTHING'}")

        time.sleep(0.5)

    def handle_context_death_screen(self, game_frame):
        self.input_controller.tap_key(" ")

        time.sleep(1)


