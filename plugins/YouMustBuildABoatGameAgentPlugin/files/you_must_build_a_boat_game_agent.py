from lib.game_agent import GameAgent

from lib.machine_learning.context_classification.context_classifiers import CNNInceptionV3ContextClassifier

from lib.sprite import Sprite

import lib.cv
import lib.ocr

from .helpers.ocr import preprocess as ocr_preprocess
from .helpers.game import parse_game_board, generate_game_board_deltas, score_game_board, score_game_board_vector, generate_boolean_game_board_deltas, display_game_board

import offshoot

import numpy as np
import h5py

import xtermcolor

import skimage.io

import sklearn

from datetime import datetime, timedelta

import time
import uuid
import random
import collections
import pickle
import os
import subprocess
import shlex


class YouMustBuildABoatGameAgent(GameAgent):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.frame_handlers["PLAY"] = self.handle_play
        self.frame_handlers["PLAY_BOT"] = self.handle_play_bot
        self.frame_handlers["PLAY_RANDOM"] = self.handle_play_random

        self.frame_handler_setups["PLAY"] = self.setup_play
        self.frame_handler_setups["PLAY_BOT"] = self.setup_play_bot

        self.analytics_client = None

    @property
    def game_contexts(self):
        return dict(

        )

    @property
    def rows(self):
        return ["A", "B", "C", "D", "E", "F"]

    @property
    def columns(self):
        return [1, 2, 3, 4, 5, 6, 7, 8]

    @property
    def match_milestone_sfx_mapping(self):
        return {
            10: "/home/serpent/SFX/first_blood.wav",
            20: "/home/serpent/SFX/Double_Kill.wav",
            30: "/home/serpent/SFX/Killing_Spree.wav",
            40: "/home/serpent/SFX/Dominating.wav",
            50: "/home/serpent/SFX/MegaKill.wav",
            60: "/home/serpent/SFX/Unstoppable.wav",
            70: "/home/serpent/SFX/WhickedSick.wav",
            80: "/home/serpent/SFX/MonsterKill.wav",
            90: "/home/serpent/SFX/GodLike.wav",
            100: "/home/serpent/SFX/Combowhore.wav"
        }

    def setup_play(self):
        plugin_path = offshoot.config["file_paths"]["plugins"]

        ocr_classifier_path = f"{plugin_path}/YouMustBuildABoatGameAgentPlugin/files/ml_models/you_must_build_a_boat_ocr.model"
        self.machine_learning_models["ocr_classifier"] = self.load_machine_learning_model(ocr_classifier_path)

        context_classifier_path = f"{plugin_path}/YouMustBuildABoatGameAgentPlugin/files/ml_models/you_must_build_a_boat_context.model"

        context_classifier = CNNInceptionV3ContextClassifier(input_shape=(384, 512, 3))
        context_classifier.prepare_generators()
        context_classifier.load_classifier(context_classifier_path)

        self.machine_learning_models["context_classifier"] = context_classifier

        self.ocr_policy = lib.ocr.OCRPolicy(
            ocr_classifier=self.machine_learning_models["ocr_classifier"],
            character_window_shape="rectangle",
            character_window_size=(7, 2),
            word_window_shape="rectangle",
            word_window_size=(1, 10),
            preprocessing_function=ocr_preprocess,
            preprocessing_options=dict(
                contrast_stretch_percentiles=(80, 100)
            )
        )

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

        if os.path.isfile("datasets/ymbab_matching.model"):
            with open("datasets/ymbab_matching.model", "rb") as f:
                self.model = pickle.loads(f.read())
        else:
            self.model = sklearn.linear_model.SGDRegressor()

    def setup_play_bot(self):
        plugin_path = offshoot.config["file_paths"]["plugins"]

        ocr_classifier_path = f"{plugin_path}/YouMustBuildABoatGameAgentPlugin/files/ml_models/you_must_build_a_boat_ocr.model"
        self.machine_learning_models["ocr_classifier"] = self.load_machine_learning_model(ocr_classifier_path)

        context_classifier_path = f"{plugin_path}/YouMustBuildABoatGameAgentPlugin/files/ml_models/you_must_build_a_boat_context.model"

        context_classifier = CNNInceptionV3ContextClassifier(input_shape=(384, 512, 3))
        context_classifier.prepare_generators()
        context_classifier.load_classifier(context_classifier_path)

        self.machine_learning_models["context_classifier"] = context_classifier

        self.ocr_policy = lib.ocr.OCRPolicy(
            ocr_classifier=self.machine_learning_models["ocr_classifier"],
            character_window_shape="rectangle",
            character_window_size=(7, 2),
            word_window_shape="rectangle",
            word_window_size=(1, 10),
            preprocessing_function=ocr_preprocess,
            preprocessing_options=dict(
                contrast_stretch_percentiles=(80, 100)
            )
        )

        self.game_board = np.zeros((6, 8))
        self.previous_game_board = np.zeros((6, 8))

    def handle_play(self, game_frame):
        context = self.machine_learning_models["context_classifier"].predict(game_frame.frame)

        if context is None:
            return

        if context == "game_over":
            self.last_run_duration = (datetime.utcnow() - self.current_run_started_at).seconds if self.current_run_started_at else 0

            self.last_attempts = self.current_attempts if self.current_attempts > 0 else 1
            self.last_matches = self.current_matches

            if self.current_run > 0:
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

            if self.last_matches < 10:
                subprocess.Popen(shlex.split(f"play -v 0.45 /home/serpent/SFX/Humiliating_defeat.wav"))

            print("\033c")

            game_board_vector_data = list()
            scores = list()

            if len(self.game_boards):
                print(f"GENERATING TRAINING DATASETS: 0 / 1")
                print(f"NEXT RUN: {self.current_run + 1}")

                game_board_deltas = generate_game_board_deltas(self.game_boards[-1])
                boolean_game_board_deltas = generate_boolean_game_board_deltas(game_board_deltas)

                for game_move, boolean_game_boards in boolean_game_board_deltas.items():
                    for boolean_game_board in boolean_game_boards:
                        for i in range(6):
                            row = boolean_game_board[i, :]

                            game_board_vector_data.append(row)
                            scores.append(score_game_board_vector(row))

                        for i in range(8):
                            column = boolean_game_board[:, i]
                            column = np.append(column, [0, 0])

                            game_board_vector_data.append(column)
                            scores.append(score_game_board_vector(column))

                print("\033c")
                print(f"GENERATING TRAINING DATASETS: 1 / 1")
                print(f"NEXT RUN: {self.current_run + 1}")

            with h5py.File(f"datasets/ymbab/ymbab_run_{self.current_run}.h5", "w") as f:
                for index, data in enumerate(game_board_vector_data):
                    f.create_dataset(f"{index}", data=data)

                for index, data in enumerate(scores):
                    f.create_dataset(f"{index}_score", data=data)

            self.game_boards = list()
            self.current_run += 1

            if self.current_run % 10 == 0:
                self.mode = "PREDICT"

                print("\033c")
                print("UPDATING MODEL WITH LATEST COLLECTED DATA...")
                print(f"NEXT RUN: {self.current_run}")

                for i in range(9 if self.current_run <= 10 else 10):
                    data_file_path = f"datasets/ymbab/ymbab_run_{self.current_run - (i + 1)}.h5"

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

                with open("datasets/ymbab_matching.model", "wb") as f:
                    f.write(serialized_model)
            else:
                self.mode = "PREDICT"

            print("\033c")
            self.input_controller.click_screen_region(screen_region="GAME_OVER_RUN_AGAIN", game=self.game)

            time.sleep(2)

            self.current_run_started_at = datetime.utcnow()

            self.current_attempts = 0
            self.current_matches = 0

        elif context.startswith("level_"):
            self.previous_game_board = self.game_board
            self.game_board = parse_game_board(game_frame.frame)

            unknown_tile_coordinates = np.argwhere(self.game_board == 0)

            if 0 < unknown_tile_coordinates.size <= 10:
                coordinates = random.choice(unknown_tile_coordinates)
                tile_screen_region = f"GAME_BOARD_{self.rows[coordinates[0]]}{self.columns[coordinates[1]]}"

                self.input_controller.click_screen_region(screen_region=tile_screen_region, game=self.game)

            self.current_attempts += 1

            game_board_deltas = generate_game_board_deltas(self.game_board)

            if self.game_board[self.game_board == 0].size < 3:
                self.game_boards.append(self.game_board)

            if self.mode == "PREDICT":
                boolean_game_board_deltas = generate_boolean_game_board_deltas(game_board_deltas, obfuscate=False)

                top_game_move_score = -10
                top_game_move = None

                game_move_scores = dict()

                for game_move, boolean_game_boards in boolean_game_board_deltas.items():
                    split_game_move = game_move.split(" to ")
                    axis = "ROW" if split_game_move[0][0] == split_game_move[1][0] else "COLUMN"

                    total_score = 0

                    for boolean_game_board in boolean_game_boards:
                        input_vectors = list()

                        if axis == "ROW":
                            row_index = self.rows.index(split_game_move[0][0])
                            row = boolean_game_board[row_index, :]

                            input_vectors.append(row)

                            for ii in range(8):
                                column = boolean_game_board[:, ii]
                                column = np.append(column, [False, False])

                                input_vectors.append(column)
                        elif axis == "COLUMN":
                            for ii in range(6):
                                row = boolean_game_board[ii, :]
                                input_vectors.append(row)

                            column_index = self.columns.index(int(split_game_move[0][1]))
                            column = boolean_game_board[:, column_index]
                            column = np.append(column, [False, False])

                            input_vectors.append(column)

                        prediction = self.model.predict(input_vectors)
                        total_score += max(prediction)

                    game_move_scores[game_move] = total_score

                    if total_score > top_game_move_score:
                        top_game_move_score = total_score
                        top_game_move = game_move

                if top_game_move is None:
                    return False

                start_coordinate, end_coordinate = top_game_move.split(" to ")

                start_screen_region = f"GAME_BOARD_{start_coordinate}"
                end_screen_region = f"GAME_BOARD_{end_coordinate}"
            elif self.mode == "RANDOM":
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

            start_coordinate = start_screen_region.split('_')[-1]
            end_coordinate = end_screen_region.split('_')[-1]

            game_board_key = f"{start_coordinate} to {end_coordinate}"
            game_board_delta = None

            for board_delta in game_board_deltas:
                if board_delta[0] == game_board_key:
                    game_board_delta = board_delta[1]
                    break

            if score_game_board(game_board_delta) > 0:
                self.current_matches += 1

                if self.current_matches in self.match_milestone_sfx_mapping:
                    subprocess.Popen(shlex.split(f"play -v 0.45 {self.match_milestone_sfx_mapping[self.current_matches]}"))

            print("\033c")

            print(f"CURRENT RUN: {self.current_run}")
            print(f"CURRENT MODE: {self.mode}\n")

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

            # print(f"Duration (RANDOM): {self.record_random_duration} seconds  (Run #{self.record_random_duration_run})")
            print(f"Duration (PREDICT): {self.record_predict_duration} seconds (Run #{self.record_predict_duration_run})")

            # print(f"Matches (RANDOM - Approximate): {self.record_random_matches}  (Run #{self.record_random_matches_run})")
            print(f"Matches (PREDICT - Approximate): {self.record_predict_matches}  (Run #{self.record_predict_matches_run})")

            print("")
            print(xtermcolor.colorize(" PREDICT AVERAGES (Last 10 runs)", ansi=29, ansi_bg=15))
            print("")

            print(f"Duration: {round(np.mean(self.record_predict_duration_values), 2)} seconds")
            print(f"{', '.join([str(v) for v in list(self.record_predict_duration_values)])}")

            print(f"\nMatches (Approximate): {np.mean(self.record_predict_matches_values)}")
            print(f"{', '.join([str(int(v)) for v in list(self.record_predict_matches_values)])}")

            game_move_direction = "ROW" if self.game.screen_regions[start_screen_region][0] == self.game.screen_regions[end_screen_region][0] else "COLUMN"

            if game_move_direction == "ROW":
                game_move_distance = int(end_coordinate[1]) - int(start_coordinate[1])
            else:
                game_move_distance = self.rows.index(end_coordinate[0]) - self.rows.index(start_coordinate[0])

            self.input_controller.drag_screen_region_to_screen_region(
                start_screen_region=start_screen_region,
                end_screen_region=end_screen_region,
                duration=(0.1 + (game_move_distance * 0.05)),
                game=self.game
            )

    def handle_play_bot(self, game_frame):
        context = self.machine_learning_models["context_classifier"].predict(game_frame.frame)

        if context is None:
            return

        # if context == "game_over":
        #     self.input_controller.click_screen_region(screen_region="GAME_OVER_RUN_AGAIN", game=self.game)
        #     time.sleep(2)
        # elif context.startswith("level_"):
        #     print("\033c")
        #     print(context)
        #     print("BOARD STATE:\n")
        #
        #     self.previous_game_board = self.game_board
        #     self.game_board = parse_game_board(game_frame.frame)
        #     print(self.game_board)
        #
        #     # Click the Unknown Tiles
        #     unknown_tile_coordinates = np.argwhere(self.game_board == 0)
        #
        #     if 0 < unknown_tile_coordinates.size <= 10:
        #         coordinates = random.choice(unknown_tile_coordinates)
        #         tile_screen_region = f"GAME_BOARD_{self.rows[coordinates[0]]}{self.columns[coordinates[1]]}"
        #
        #         self.input_controller.click_screen_region(screen_region=tile_screen_region, game=self.game)
        #
        #     if not np.array_equal(self.game_board, self.previous_game_board):
        #         return
        #
        #     game_board_deltas = generate_game_board_deltas(self.game_board)
        #     game_board_delta_matches = detect_game_board_delta_matches(game_board_deltas)
        #
        #     game_move = None
        #
        #     for i in [5, 4, 3]:
        #         if not len(game_board_delta_matches[i]):
        #             continue
        #
        #         game_move = random.choice(game_board_delta_matches[i])
        #         break
        #
        #     if game_move is None:
        #         time.sleep(0.1)
        #         return
        #
        #     game_move_start_cell, game_move_end_cell = game_move.split(" to ")
        #
        #     start_screen_region = f"GAME_BOARD_{game_move_start_cell}"
        #     end_screen_region = f"GAME_BOARD_{game_move_end_cell}"
        #
        #     game_move_direction = "ROW" if self.game.screen_regions[start_screen_region][0] == self.game.screen_regions[end_screen_region][0] else "COLUMN"
        #
        #     if game_move_direction == "ROW":
        #         game_move_distance = int(game_move_end_cell[1]) - int(game_move_start_cell[1])
        #     else:
        #         game_move_distance = self.rows.index(game_move_end_cell[0]) - self.rows.index(game_move_start_cell[0])
        #
        #     print(f"\nMoving {game_move_start_cell} to {game_move_end_cell}...")
        #
        #     print(game_board_delta_matches)
        #
        #     self.input_controller.drag_screen_region_to_screen_region(
        #         start_screen_region=start_screen_region,
        #         end_screen_region=end_screen_region,
        #         duration=(0.1 + (game_move_distance * 0.05)),
        #         game=self.game
        #     )

    def handle_play_random(self, game_frame):
        rows = ["A", "B", "C", "D", "E", "F"]
        columns = [1, 2, 3, 4, 5, 6, 7, 8]

        row = random.choice(rows)
        column = random.choice(columns)

        start_screen_region = f"GAME_BOARD_{row}{column}"

        axis = "row" if random.randint(0, 1) else "column"

        if axis == "row":
            end_column = random.choice(columns)

            while end_column == column:
                end_column = random.choice(columns)

            end_screen_region = f"GAME_BOARD_{row}{end_column}"
        else:
            end_row = random.choice(rows)

            while end_row == row:
                end_row = random.choice(rows)

            end_screen_region = f"GAME_BOARD_{end_row}{column}"

        print(f"\nMoving {start_screen_region.split('_')[-1]} to {end_screen_region.split('_')[-1]}...")

        self.input_controller.drag_screen_region_to_screen_region(
            start_screen_region=start_screen_region,
            end_screen_region=end_screen_region,
            duration=0.3,
            game=self.game
        )

        time.sleep(1)

    def handle_collect_characters(self, game_frame):
        frame_uuid = str(uuid.uuid4())

        skimage.io.imsave(f"datasets/ocr/frames/frame_{frame_uuid}.png", game_frame.frame)

        preprocessed_frame = ocr_preprocess(game_frame.frame, **self.ocr_policy.preprocessing_options)

        objects = lib.ocr.detect_image_objects_closing(preprocessed_frame, window_shape="rectangle", window_size=(7, 2))
        normalized_objects = lib.ocr.normalize_objects(preprocessed_frame, objects)

        lib.ocr.save_objects("datasets/ocr/characters", objects, normalized_objects, frame_uuid)

        time.sleep(self.config.get("collect_character_interval") or 1)

