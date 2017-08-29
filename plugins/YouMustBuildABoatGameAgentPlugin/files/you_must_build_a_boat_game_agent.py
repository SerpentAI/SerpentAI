from lib.game_agent import GameAgent

from lib.machine_learning.context_classification.context_classifiers import CNNInceptionV3ContextClassifier

from .helpers.game import *

import offshoot

import numpy as np

import sklearn
import skimage.io

import h5py

import xtermcolor

import time
import random
import collections
import pickle
import os
import subprocess
import shlex

from datetime import datetime


class YouMustBuildABoatGameAgent(GameAgent):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.frame_handlers["PLAY"] = self.handle_play
        self.frame_handlers["PLAY_BOT"] = self.handle_play_bot
        self.frame_handlers["PLAY_RANDOM"] = self.handle_play_random

        self.frame_handler_setups["PLAY"] = self.setup_play
        self.frame_handler_setups["PLAY_BOT"] = self.setup_play_bot
        self.frame_handler_setups["PLAY_RANDOM"] = self.setup_play_bot

        self.analytics_client = None

    @property
    def rows(self):
        return ["A", "B", "C", "D", "E", "F"]

    @property
    def columns(self):
        return [1, 2, 3, 4, 5, 6, 7, 8]

    @property
    def match_milestone_sfx_mapping(self):
        return {
            10: f"{self.config.get('sfx_path')}/first_blood.wav",
            20: f"{self.config.get('sfx_path')}/Double_Kill.wav",
            30: f"{self.config.get('sfx_path')}/Killing_Spree.wav",
            40: f"{self.config.get('sfx_path')}/Dominating.wav",
            50: f"{self.config.get('sfx_path')}/MegaKill.wav",
            60: f"{self.config.get('sfx_path')}/Unstoppable.wav",
            70: f"{self.config.get('sfx_path')}/WhickedSick.wav",
            80: f"{self.config.get('sfx_path')}/MonsterKill.wav",
            90: f"{self.config.get('sfx_path')}/GodLike.wav",
            100: f"{self.config.get('sfx_path')}/Combowhore.wav"
        }

    def setup_play(self):
        plugin_path = offshoot.config["file_paths"]["plugins"]

        context_classifier_path = f"{plugin_path}/YouMustBuildABoatGameAgentPlugin/files/ml_models/you_must_build_a_boat_context.model"

        context_classifier = CNNInceptionV3ContextClassifier(input_shape=(384, 512, 3))
        context_classifier.prepare_generators()
        context_classifier.load_classifier(context_classifier_path)

        self.machine_learning_models["context_classifier"] = context_classifier

        self._load_model(plugin_path)

        # Game Agent State
        self.game_board = np.zeros((6, 8))
        self.previous_game_board = np.zeros((6, 8))

        self.mode = "PREDICT"  # "RANDOM"

        self.current_run = 0
        self.current_run_started_at = None

        self.current_attempts = 0
        self.current_matches = 0

        self.last_run_duration = 0

        self.last_attempts = 0
        self.last_matches = 0

        self.record_random_duration = 0
        self.record_random_duration_run = 0
        self.record_random_matches = 0
        self.record_random_matches_run = 0

        self.record_random_duration_values = collections.deque(maxlen=1000)
        self.record_random_matches_values = collections.deque(maxlen=1000)

        self.record_predict_duration = 0
        self.record_predict_duration_run = 0
        self.record_predict_matches = 0
        self.record_predict_matches_run = 0

        self.record_predict_duration_values = collections.deque(maxlen=10)
        self.record_predict_matches_values = collections.deque(maxlen=10)

        self.game_boards = list()

        self.validation_game_boards = list()
        self.validation_optimal_score = 0

        self.model_validation_score = 0

        self._load_validation_game_boards()

    def setup_play_bot(self):
        plugin_path = offshoot.config["file_paths"]["plugins"]

        context_classifier_path = f"{plugin_path}/YouMustBuildABoatGameAgentPlugin/files/ml_models/you_must_build_a_boat_context.model"

        context_classifier = CNNInceptionV3ContextClassifier(input_shape=(384, 512, 3))
        context_classifier.prepare_generators()
        context_classifier.load_classifier(context_classifier_path)

        self.machine_learning_models["context_classifier"] = context_classifier

        self.game_board = np.zeros((6, 8))
        self.previous_game_board = np.zeros((6, 8))

    def handle_play(self, game_frame):
        context = self.machine_learning_models["context_classifier"].predict(game_frame.frame)

        if context is None:
            return

        if context.startswith("level_"):
            self.handle_play_context_level(game_frame)
        elif context == "game_over":
            self.handle_play_context_game_over(game_frame)

    def handle_play_bot(self, game_frame):
        #context = self.machine_learning_models["context_classifier"].predict(game_frame.frame)
        context = "level_"

        if context is None:
            return

        if context.startswith("level_"):
            self.previous_game_board = self.game_board
            self.game_board = parse_game_board(game_frame.frame)

            print("\033c")
            print("BOARD STATE:\n")

            display_game_board(self.game_board)

            self.click_unknown_tile()

            game_board_deltas = generate_game_board_deltas(self.game_board)

            best_game_move_score = 0
            best_game_move = None

            for game_board_delta in game_board_deltas:
                score = score_game_board(game_board_delta[1])

                if score > best_game_move_score:
                    best_game_move_score = score
                    best_game_move = game_board_delta[0]

            if best_game_move is None:
                return

            game_move_start_cell, game_move_end_cell = best_game_move.split(" to ")

            start_screen_region = f"GAME_BOARD_{game_move_start_cell}"
            end_screen_region = f"GAME_BOARD_{game_move_end_cell}"

            game_move_distance = calculate_game_move_distance(game_move_start_cell, game_move_end_cell)

            print(xtermcolor.colorize(f" Moving {best_game_move}... ", ansi=0, ansi_bg=39))

            self.input_controller.drag_screen_region_to_screen_region(
                start_screen_region=start_screen_region,
                end_screen_region=end_screen_region,
                duration=(0.1 + (game_move_distance * 0.05)),
                game=self.game
            )
        elif context == "game_over":
            self.input_controller.click_screen_region(screen_region="GAME_OVER_RUN_AGAIN", game=self.game)
            time.sleep(2)

    def handle_play_random(self, game_frame):
        context = self.machine_learning_models["context_classifier"].predict(game_frame.frame)

        if context is None:
            return

        if context == "game_over":
            self.input_controller.click_screen_region(screen_region="GAME_OVER_RUN_AGAIN", game=self.game)
            time.sleep(2)
        elif context.startswith("level_"):
            start_screen_region, end_screen_region = self.handle_play_random_mode()

            start_coordinate = start_screen_region.split('_')[-1]
            end_coordinate = end_screen_region.split('_')[-1]

            game_board_key = f"{start_coordinate} to {end_coordinate}"

            print(f"\nMoving {game_board_key}...")

            game_move_distance = calculate_game_move_distance(start_coordinate, end_coordinate)

            self.input_controller.drag_screen_region_to_screen_region(
                start_screen_region=start_screen_region,
                end_screen_region=end_screen_region,
                duration=(0.1 + (game_move_distance * 0.05)),
                game=self.game
            )

    def handle_play_context_level(self, game_frame):
        # Update the Game Agent State
        self.previous_game_board = self.game_board
        self.game_board = parse_game_board(game_frame.frame)

        # Click an unknown game board tile. Power-ups are not parsed and need
        # to eventually be cleared out / activated.
        self.click_unknown_tile()

        # Bump up the attempt count for statistics
        self.current_attempts += 1

        # Generate the game boards resulting from the 82 possible unique moves
        game_board_deltas = generate_game_board_deltas(self.game_board)

        # Collect the game board for dataset generation
        if self.game_board[self.game_board == 0].size < 3:
            self.game_boards.append(self.game_board)

        # Generate game move screen regions
        if self.mode == "PREDICT":
            start_screen_region, end_screen_region = self.handle_play_predict_mode(game_board_deltas)
        elif self.mode == "RANDOM":
            start_screen_region, end_screen_region = self.handle_play_random_mode()

        # Generate game move coordinates
        start_coordinate = start_screen_region.split('_')[-1]
        end_coordinate = end_screen_region.split('_')[-1]

        game_board_key = f"{start_coordinate} to {end_coordinate}"

        # Detect post-move game board matches
        game_board_delta = None

        for board_delta in game_board_deltas:
            if board_delta[0] == game_board_key:
                game_board_delta = board_delta[1]
                break

        # Handle game board match
        if score_game_board(game_board_delta) > 0:
            self.current_matches += 1

            if self.current_matches in self.match_milestone_sfx_mapping:
                subprocess.Popen(shlex.split(f"play -v 0.45 {self.match_milestone_sfx_mapping[self.current_matches]}"))

        # Print the game agent state to the terminal
        self.display_game_agent_state(game_board_key)

        # Calculate the game move distance
        game_move_distance = calculate_game_move_distance(start_coordinate, end_coordinate)

        # Send the input to perform the game move
        self.input_controller.drag_screen_region_to_screen_region(
            start_screen_region=start_screen_region,
            end_screen_region=end_screen_region,
            duration=(0.1 + (game_move_distance * 0.05)),
            game=self.game
        )

    def handle_play_predict_mode(self, game_board_deltas):
        boolean_game_board_deltas = generate_boolean_game_board_deltas(game_board_deltas)

        start_coordinate, end_coordinate = predict_game_move(
            self.model,
            boolean_game_board_deltas,
            distribution=[0, 0, 0, 0, 0, 1, 1, 1, 2, 2, 3, 4]
        )

        start_screen_region = f"GAME_BOARD_{start_coordinate}"
        end_screen_region = f"GAME_BOARD_{end_coordinate}"

        return start_screen_region, end_screen_region

    def handle_play_random_mode(self):
        axis = random.choice(["ROW", "COLUMN"])

        if axis == "ROW":
            row = random.choice(self.rows)

            column = 1
            end_column = 1 + (random.choice(range(7)) + 1)

            start_screen_region = f"GAME_BOARD_{row}{column}"
            end_screen_region = f"GAME_BOARD_{row}{end_column}"
        else:
            column = random.choice(self.columns)

            row = "A"
            end_row = self.rows[random.choice(range(5)) + 1]

            start_screen_region = f"GAME_BOARD_{row}{column}"
            end_screen_region = f"GAME_BOARD_{end_row}{column}"

        return start_screen_region, end_screen_region

    def handle_play_context_game_over(self, game_frame):
        # Update the Game Agent State
        self.last_run_duration = (datetime.utcnow() - self.current_run_started_at).seconds if self.current_run_started_at else 0

        self.last_attempts = self.current_attempts if self.current_attempts > 0 else 1
        self.last_matches = self.current_matches

        # Detect new records
        if self.current_run > 0:
            self.detect_records()

        # Detect humiliating defeat :D
        if self.last_matches < 10:
            subprocess.Popen(shlex.split(f"play -v 0.45 /home/serpent/SFX/Humiliating_defeat.wav"))

        # Create a new HDF5 file with the last game board's data
        self.generate_game_board_dataset()

        # Update the Game Agent State
        self.game_boards = list()
        self.current_run += 1

        if self.current_run > 1:
            # Update the model with the latest data
            self.update_model()

            # Run the updated model against the validation set
            self.model_validation_score = self.validate_model()

        print("\033c")

        # Send the input to start a new run
        self.input_controller.click_screen_region(screen_region="GAME_OVER_RUN_AGAIN", game=self.game)

        time.sleep(2)

        self.current_run_started_at = datetime.utcnow()

        self.current_attempts = 0
        self.current_matches = 0

    def validate_model(self):
        model_score = 0

        for game_board in self.validation_game_boards:
            game_board_deltas = generate_game_board_deltas(game_board)

            boolean_game_board_deltas = generate_boolean_game_board_deltas(game_board_deltas)

            start_coordinate, end_coordinate = predict_game_move(self.model, boolean_game_board_deltas, distribution=[0])

            game_move_game_board_delta = None

            for game_board_delta in game_board_deltas:
                if game_board_delta[0] == f"{start_coordinate} to {end_coordinate}":
                    game_move_game_board_delta = game_board_delta[1]
                    break

            model_score += score_game_board(game_move_game_board_delta)

        return model_score

    def update_model(self):
        print("\033c")

        print("UPDATING MODEL WITH LATEST COLLECTED DATA...")
        print(f"NEXT RUN: {self.current_run}")

        data_file_path = f"datasets/ymbab/ymbab_run_{self.current_run - 1}.h5"

        data = list()
        scores = list()

        with h5py.File(data_file_path, "r") as f:
            count = len(f.items()) // 2

            for ii in range(count):
                data.append(f[f"{ii}"][:])
                scores.append(f[f"{ii}_score"].value)

        if len(data):
            self.model.partial_fit(data, scores)

        serialized_model = pickle.dumps(self.model)

        matching_model_path = f"{offshoot.config['file_paths']['plugins']}/YouMustBuildABoatGameAgentPlugin/files/ml_models/you_must_build_a_boat_matching.model"

        with open(matching_model_path, "wb") as f:
            f.write(serialized_model)

    def generate_game_board_dataset(self):
        print("\033c")

        game_board_vector_data = list()
        scores = list()

        if len(self.game_boards):
            print(f"GENERATING TRAINING DATASETS: 0 / 1")
            print(f"NEXT RUN: {self.current_run + 1}")

            game_board_vector_data, scores = generate_game_board_vector_data(self.game_boards[-1])

            print("\033c")
            print(f"GENERATING TRAINING DATASETS: 1 / 1")
            print(f"NEXT RUN: {self.current_run + 1}")

        with h5py.File(f"datasets/ymbab/ymbab_run_{self.current_run}.h5", "w") as f:
            for index, data in enumerate(game_board_vector_data):
                f.create_dataset(f"{index}", data=data)

            for index, data in enumerate(scores):
                f.create_dataset(f"{index}_score", data=data)

    def detect_records(self):
        if self.mode == "RANDOM":
            self.record_random_duration_values.appendleft(self.last_run_duration)
            self.record_random_matches_values.appendleft(self.last_matches)

            if self.last_run_duration > self.record_random_duration:
                self.record_random_duration = self.last_run_duration
                self.record_random_duration_run = self.current_run

            if self.last_matches > self.record_random_matches:
                self.record_random_matches = self.last_matches
                self.record_random_matches_run = self.current_run
        elif self.mode == "PREDICT":
            self.record_predict_duration_values.appendleft(self.last_run_duration)
            self.record_predict_matches_values.appendleft(self.last_matches)

            record = False

            if self.last_run_duration > self.record_predict_duration:
                record = True

                self.record_predict_duration = self.last_run_duration
                self.record_predict_duration_run = self.current_run

            if self.last_matches > self.record_predict_matches:
                record = True

                self.record_predict_matches = self.last_matches
                self.record_predict_matches_run = self.current_run

            if record:
                subprocess.Popen(shlex.split(f"play -v 0.45 /home/serpent/SFX/HolyShit_F.wav"))

    def display_game_agent_state(self, game_board_key):
        print("\033c")

        print(f"CURRENT RUN: {self.current_run}")
        print(f"CURRENT MODE: {self.mode}\n")

        print(f"CURRENT MODEL VALIDATION SCORE: {self.model_validation_score}\n")

        print("BOARD STATE:\n")
        display_game_board(self.game_board)

        print("")

        print(xtermcolor.colorize(f" Moving {game_board_key}... ", ansi=0, ansi_bg=39))

        print(f"\nCurrent Run Duration: {(datetime.utcnow() - self.current_run_started_at).seconds} seconds")
        print(f"Current Run Matches (Approximate): {self.current_matches}/{self.current_attempts}")

        print(f"\nLast Run Duration: {self.last_run_duration} seconds")
        print(f"Last Run Matches (Approximate): {self.last_matches}/{self.last_attempts}")

        print("")

        print(xtermcolor.colorize(" RECORDS ", ansi=29, ansi_bg=15))
        print("")

        print(f"Duration (PREDICT): {self.record_predict_duration} seconds (Run #{self.record_predict_duration_run})")
        print(f"Matches (PREDICT - Approximate): {self.record_predict_matches}  (Run #{self.record_predict_matches_run})")

        print("")

        print(xtermcolor.colorize(" PREDICT AVERAGES (Last 10 runs)", ansi=29, ansi_bg=15))
        print("")
        print(f"Duration: {round(np.mean(self.record_predict_duration_values), 2)} seconds")
        print(f"{', '.join([str(v) for v in list(self.record_predict_duration_values)])}")

        print(f"\nMatches (Approximate): {np.mean(self.record_predict_matches_values)}")
        print(f"{', '.join([str(int(v)) for v in list(self.record_predict_matches_values)])}")

    def click_unknown_tile(self):
        unknown_tile_coordinates = np.argwhere(self.game_board == 0)

        if 0 < len(unknown_tile_coordinates) <= 10:
            coordinates = random.choice(unknown_tile_coordinates)
            tile_screen_region = f"GAME_BOARD_{self.rows[coordinates[0]]}{self.columns[coordinates[1]]}"

            self.input_controller.click_screen_region(screen_region=tile_screen_region, game=self.game)

    def _load_model(self, plugin_path):
        matching_model_path = f"{plugin_path}/YouMustBuildABoatGameAgentPlugin/files/ml_models/you_must_build_a_boat_matching.model"

        if os.path.isfile(matching_model_path):
            with open(matching_model_path, "rb") as f:
                self.model = pickle.loads(f.read())
        else:
            self.model = sklearn.linear_model.SGDRegressor(
                loss="squared_loss",
                penalty="elasticnet",
                alpha=1e-7,
                l1_ratio=0.45,
                learning_rate="invscaling",
                eta0=0.0065
            )

    def _load_validation_game_boards(self):
        for root, dirs, files in os.walk("datasets/ymbab-validation"):
            for file in files:
                if not file.endswith(".png"):
                    continue

                frame = skimage.io.imread(f"datasets/ymbab-validation/{file}")

                game_board = parse_game_board(frame)
                self.validation_game_boards.append(game_board)
