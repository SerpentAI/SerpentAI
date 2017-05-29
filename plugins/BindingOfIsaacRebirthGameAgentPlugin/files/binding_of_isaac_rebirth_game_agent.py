from lib.game_agent import GameAgent

import lib.cv

from lib.machine_learning.context_classification.context_classifiers import *
from lib.machine_learning.reinforcement_learning.keyboard_mouse_input_space import KeyboardMouseInputSpace

from .helpers.frame_processing import *

from .helpers.game_floor import GameFloor
from .helpers.game_minimap import GameMinimap

import offshoot

import time
import uuid
import subprocess
import itertools
import json

import numpy as np

import skimage.io
import skimage.filters
import skimage.morphology
import skimage.measure
import skimage.draw
import skimage.segmentation

from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten, Convolution2D, Permute
from keras.optimizers import Adam
from keras.callbacks import History

from collections import deque

import random


class BindingOfIsaacRebirthGameAgent(GameAgent):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.frame_handlers["PLAY"] = self.handle_play
        self.frame_handlers["GAME_TRAIN"] = self.handle_game_train

        self.frame_handler_setups["PLAY"] = self.setup_play
        self.frame_handler_setups["GAME_TRAIN"] = self.setup_game_train

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

    def setup_play(self):
        plugin_path = offshoot.config["file_paths"]["plugins"]

        ocr_classifier_path = f"{plugin_path}/BindingOfIsaacRebirthGameAgentPlugin/files/ml_models/binding_of_isaac_rebirth_ocr.model"
        self.machine_learning_models["ocr_classifier"] = self.load_machine_learning_model(ocr_classifier_path)

        context_classifier_path = f"{plugin_path}/BindingOfIsaacRebirthGameAgentPlugin/files/ml_models/binding_of_isaac_rebirth_context.model"

        context_classifier = CNNInceptionV3ContextClassifier(input_shape=(270, 480, 3))
        context_classifier.prepare_generators()
        context_classifier.load_classifier(context_classifier_path)

        self.machine_learning_models["context_classifier"] = context_classifier

    def setup_game_train(self):
        self.input_shape = (3, 135, 240, 4)

        self.input_space = KeyboardMouseInputSpace(
            directional_keys=["W", "A", "S", "D", "WA", "WD", "SA", "SD"],
            projectile_keys=["UP", "LEFT", "DOWN", "RIGHT"]
        )

        self.input_mapping = {
            "W": ["w"],
            "A": ["a"],
            "S": ["s"],
            "D": ["d"],
            "WA": ["w", "a"],
            "WD": ["w", "d"],
            "SA": ["s", "a"],
            "SD": ["s", "d"],
            "UP": [self.input_controller.keyboard.up_key],
            "LEFT": [self.input_controller.keyboard.left_key],
            "DOWN": [self.input_controller.keyboard.down_key],
            "RIGHT": [self.input_controller.keyboard.right_key]
        }

        model = Sequential()

        # Broken...
        model.add(Permute((4, 2, 3, 1), input_shape=self.input_shape))
        model.add(Convolution2D(32, 8, 8, subsample=(4, 4)))
        model.add(Activation("relu"))
        model.add(Convolution2D(64, 4, 4, subsample=(2, 2)))
        model.add(Activation("relu"))
        model.add(Convolution2D(64, 3, 3, subsample=(1, 1)))
        model.add(Activation("relu"))
        model.add(Flatten())
        model.add(Dense(512))
        model.add(Activation("relu"))
        model.add(Dense(len(self.input_space.permutations)))
        model.add(Activation("linear"))

        self.machine_learning_models["isaac_dqn"] = model

        self.dqn_state = dict(
            memory=deque(),
            replay_memory=50000,
            batch_size=32,
            action_count=len(self.input_space.permutations),
            frame_stack=None,
            observe_steps=3200,
            epsilon=1.0,
            epsilon_initial=1.0,
            epsilon_final=0.1,
            gamma=0.99,
            current_step=0,
            max_steps=3000000,
            action_index=None
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

    def handle_game_train(self, game_frame):
        if self.dqn_state.get("frame_stack") is None:
            frame_stack = np.stack((
                game_frame.quarter_resolution_frame,
                game_frame.quarter_resolution_frame,
                game_frame.quarter_resolution_frame,
                game_frame.quarter_resolution_frame
            ), axis=2)

            self.dqn_state["frame_stack"] = frame_stack.reshape(
                3,
                frame_stack.shape[0],
                frame_stack.shape[1],
                frame_stack.shape[2]
            )
        else:
            # Reward Calculation ...
            reward = random.random()

            observation = game_frame.quarter_resolution_frame.reshape(
                3,
                game_frame.quarter_resolution_frame.shape[0],
                game_frame.quarter_resolution_frame.shape[1],
                1
            )

            frame_stack = np.append(observation, self.dqn_state["frame_stack"][:, :, :, :3], axis=3)

            self.dqn_state["memory"].append((
                self.dqn_state["frame_stack"],
                self.dqn_state["action_index"],
                reward,
                frame_stack,
                False
            ))

            if len(self.dqn_state["memory"]) > self.dqn_state["replay_memory"]:
                self.dqn_state["memory"].popleft()

            loss = 0
            projected_future_rewards = [0]

            if self.dqn_state["current_step"] > self.dqn_state["observe_steps"]:
                mini_batch = random.sample(self.dqn_state["memory"], self.dqn_state["batch_size"])

                inputs = np.zeros((
                    self.dqn_state["batch_size"],
                    3,
                    self.dqn_state["frame_stack"].shape[1],
                    self.dqn_state["frame_stack"].shape[2],
                    self.dqn_state["frame_stack"].shape[3]
                ))

                targets = np.zeros((inputs.shape[0], len(self.input_space.permutations)))  # 32, 2

                for i in range(0, len(mini_batch)):
                    previous_frame_stack = mini_batch[i][0]
                    action_index = mini_batch[i][1]
                    reward = mini_batch[i][2]
                    frame_stack = mini_batch[i][3]
                    terminal = mini_batch[i][4]

                    inputs[i:i + 1] = previous_frame_stack

                    targets[i] = self.machine_learning_models["isaac_dqn"].predict(previous_frame_stack)
                    projected_future_rewards = self.machine_learning_models["isaac_dqn"].predict(frame_stack)

                    if terminal:
                        targets[i, action_index] = reward
                    else:
                        targets[i, action_index] = reward + self.dqn_state["gamma"] * np.max(projected_future_rewards)

                loss = self.machine_learning_models["isaac_dqn"].train_on_batch(inputs, targets)

            self.dqn_state["frame_stack"] = frame_stack

            if self.dqn_state["current_step"] % 1000 == 0:
                self.machine_learning_models["isaac_dqn"].save_weights(
                    "datasets/binding_of_isaac_rebirth_dqn.h5",
                    overwrite=True
                )

                with open("datasets/binding_of_isaac_rebirth_dqn.json", "w") as f:
                    json.dump(self.machine_learning_models["isaac_dqn"].to_json(), f)

            subprocess.call(["clear"])

            print(f"CURRENT STEP: {self.dqn_state['current_step']}")
            print(f"CURRENT EPSILON: {self.dqn_state['epsilon']}")

            action = self.input_space.permutations[self.dqn_state["action_index"]]
            input_value_collections = [self.input_mapping[input_label] for input_label in self.input_space.values_for_permutation(action) if input_label is not None]
            input_values = list(itertools.chain.from_iterable(input_value_collections))

            print(f"ACTION: {input_values}")
            print(f"REWARD: {reward}")
            print(f"MAXIMUM PROJECTED FUTURE REWARD: {np.max(projected_future_rewards)}")
            print(f"LOSS: {loss}")

        # Epsilon Greedy Q-Policy
        if random.random() <= self.dqn_state.get("epsilon"):
            action_index = random.randrange(self.dqn_state.get("action_count"))
            action = self.input_space.permutations[action_index]
        else:
            q = self.machine_learning_models["isaac_dqn"].predict(self.dqn_state["frame_stack"])
            action_index = np.argmax(q)
            action = self.input_space.permutations[action_index]

        if self.dqn_state["epsilon"] > self.dqn_state["epsilon_final"] and self.dqn_state["current_step"] > self.dqn_state["observe_steps"]:
            self.dqn_state["epsilon"] -= (self.dqn_state["epsilon_initial"] - self.dqn_state["epsilon_final"]) / self.dqn_state["max_steps"]

        input_value_collections = [self.input_mapping[input_label] for input_label in self.input_space.values_for_permutation(action) if input_label is not None]
        input_values = list(itertools.chain.from_iterable(input_value_collections))

        print(input_values)
        self.input_controller.tap_keys(input_values)

        self.dqn_state["action_index"] = action_index
        self.dqn_state["current_step"] += 1

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
        self.visual_debugger.store_image_data(
            game_frame.quarter_resolution_frame,
            game_frame.quarter_resolution_frame.shape,
            "quarter_frame"
        )

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

