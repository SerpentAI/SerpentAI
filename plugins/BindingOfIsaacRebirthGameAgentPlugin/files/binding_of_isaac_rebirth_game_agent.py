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

import numpy as np

import skimage.io
import skimage.filters
import skimage.morphology
import skimage.measure
import skimage.draw
import skimage.segmentation


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

        self.game_frame_ssim = None
        self.previous_game_frame_difference = None

        self.game_state = None
        self._reset_game_state()

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
        if self.game_frame_buffer.previous_game_frame:
            self.game_frame_ssim = game_frame.compare_ssim(self.game_frame_buffer.previous_game_frame)
        else:
            self.game_frame_ssim = 0.0

        if self.game_context is None or self.game_frame_ssim <= 0.75:
            previous_context = self.game_context
            self.game_context = self.machine_learning_models["context_classifier"].predict(game_frame.frame)

            if self.game_context == "character_select_screen":
                self.game_state["character_select_generator"] = itertools.cycle(self.characters)
            elif self.game_context == "game":
                if self.game_context != previous_context:
                    self.flag = "ENTERING_GAME"
                    print("setting ENTERING_GAME")
                    time.sleep(3)
                    return None

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
        self._reset_game_state()

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
        #subprocess.call(["clear"])

        # Initialize GameFloor if needed...
        if not self.game_state["game_floor"]:
            self.game_state["game_floor"] = GameFloor()

        # Create / Update GameMinimap...
        minimap_image = get_map_grid_image_data(game_frame.grayscale_frame, self.game)

        if not self.game_state["minimap"]:
            self.game_state["minimap"] = GameMinimap(minimap_image=minimap_image)
        else:
            self.game_state["minimap"].update(minimap_image)

        minimap_ssim = self.game_state["minimap"].get_ssim()

        if minimap_ssim < 0.95:
            print(minimap_ssim)

        room_layout = get_room_layout_type(game_frame.grayscale_frame, self.game)

        if self.flag == "ENTERING_GAME":
            self.flag = None

            self._discover_rooms(room_layout)

        if self.flag == "CHANGING_ROOM":
            self.flag = None

            self._update_current_room(game_frame)
            self._discover_rooms(room_layout)

        # Check for room changes...
        if minimap_ssim < 0.75:
            print("ROOM HAS CHANGED...")

            if len(self.game_state["game_floor"].rooms) > 1:
                self.flag = "CHANGING_ROOM"
                time.sleep(0.2)

                return None
            else:
                self._discover_rooms(room_layout)

        if self.game_frame_ssim < 0.6 and minimap_ssim < 0.88:
            print("ROOM HAS POTENTIALLY CHANGED...")

            if len(self.game_state["game_floor"].rooms) > 1:
                self.flag = "CHANGING_ROOM"
                time.sleep(0.2)

                return None
            else:
                self._discover_rooms(room_layout)

    def handle_context_death_screen(self, game_frame):
        self._reset_game_state()
        self.input_controller.tap_key(" ")

        time.sleep(1)

    def _reset_game_state(self):
        self.game_state = {
            "character_select_generator": itertools.cycle(self.characters),
            "seed_entered": False,
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

    def _update_current_room(self, game_frame):
        door_image_data = get_door_image_data(game_frame.grayscale_frame, self.game, debug=True)
        door_white_pixel_counts = [(image[image >= 1].size, label) for label, image in door_image_data.items()]
        door_label = max(door_white_pixel_counts, key=lambda t: t[0])[1]

        # TODO: Add support for irregular room layouts... Assuming Normal Room layout
        if door_label == "GAME_ISAAC_DOOR_TOP":
            self.game_state["game_floor"].current_room = (
                self.game_state["game_floor"].current_room[0],
                self.game_state["game_floor"].current_room[1] - 1
            )
        elif door_label == "GAME_ISAAC_DOOR_RIGHT":
            self.game_state["game_floor"].current_room = (
                self.game_state["game_floor"].current_room[0] - 1,
                self.game_state["game_floor"].current_room[1]
            )
        elif door_label == "GAME_ISAAC_DOOR_BOTTOM":
            self.game_state["game_floor"].current_room = (
                self.game_state["game_floor"].current_room[0],
                self.game_state["game_floor"].current_room[1] + 1
            )
        elif door_label == "GAME_ISAAC_DOOR_LEFT":
            self.game_state["game_floor"].current_room = (
                self.game_state["game_floor"].current_room[0] + 1,
                self.game_state["game_floor"].current_room[1]
            )

    def _discover_rooms(self, room_layout):
        adjacent_cells = self.game_state["minimap"].get_adjacent_cells(room_layout)

        for coordinates, minimap_cell in adjacent_cells.items():
            room_type = minimap_cell.identify()

            if room_type == "empty":
                continue

            self.game_state["game_floor"].register_room(coordinates, minimap_cell)

        print(self.game_state["game_floor"].rooms)

