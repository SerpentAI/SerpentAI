from lib.game_agent import GameAgent

import lib.ocr
import lib.trigonometry
import lib.raycasting

import offshoot

import time
import json
from pprint import pprint

from .helpers.frame_processing import *


class SuperHexagonGameAgent(GameAgent):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        plugin_path = offshoot.config["file_paths"]["plugins"]

        ocr_classifier_path = f"{plugin_path}/SuperHexagonGameAgentPlugin/files/ml_models/super_hexagon_ocr.model"
        self.machine_learning_models["ocr_classifier"] = self.load_machine_learning_model(ocr_classifier_path)

        context_classifier_path = f"{plugin_path}/SuperHexagonGameAgentPlugin/files/ml_models/super_hexagon_context.model"
        self.machine_learning_models["context_classifier"] = self.load_machine_learning_model(context_classifier_path)

        self.frame_handlers["PLAY"] = self.handle_play

        self.frame_shape = (self.game.window_geometry["height"], self.game.window_geometry["width"])

        self.frame_angles_to_center = lib.trigonometry.angles_to_center(self.frame_shape)
        self.frame_distances_to_center = lib.trigonometry.distances_to_center(self.frame_shape)

        self.key_direction_mapping = {
            "+": self.input_controller.keyboard.left_key,
            "-": self.input_controller.keyboard.right_key
        }

        self.game_state = {
            "scores": {},
            "keypress_duration_index": 0,
            "keypress_durations": [0.0300],
            "collision_threshold": 240,
            "max_run": 10,
            "total_runs": 1,
            "frame_count": 0,
            "previous_context": None,
            "ray_configurations": {
                15: [17, 19, 21, 23, 24],
            },
            "current_ray_angle": 15,
            "current_ray_angle_quantity_index": 0
        }

    @property
    def game_contexts(self):
        return dict(
            s="Splash Screen",
            l="Level Select Screen",
            g="Game Screen",
            d="Death Screen"
        )

    def handle_play(self, frame):
        gray_frame = grayscale_frame(frame.frame)

        if self.game_state["previous_context"] == "Game Screen" and self.game_state["frame_count"] % 15 != 0:
            context = self.game_state["previous_context"]
        else:
            processed_context_frame = process_frame_for_context(gray_frame)

            context_prediction = self.machine_learning_models["context_classifier"].predict([processed_context_frame])[0]
            context = self.game_contexts.get(context_prediction, "Unknown")
            self.game_state["previous_context"] = context

        if context == "Splash Screen":
            splash_action = " ".join(lib.ocr.words_in_image_region(
                frame.frame,
                self.game.screen_regions["SPLASH_ACTIONS"],
                self.machine_learning_models["ocr_classifier"],
                word_window_size=(1, 8)
            ))

            if "start game" in splash_action:
                self.input_controller.tap_key(self.input_controller.keyboard.enter_key)
            else:
                self.input_controller.tap_key(self.input_controller.keyboard.right_key)

            time.sleep(5 / 60)
        elif context == "Level Select Screen":
            #self.input_controller.tap_key(self.input_controller.keyboard.right_key, duration=random.uniform(0.0, 1.0))
            self.input_controller.tap_key(self.input_controller.keyboard.enter_key)
            time.sleep(10 / 60)
        elif context == "Game Screen":
            # Preprocess
            processed_frame_for_game_play = process_frame_for_game_play(gray_frame)

            if processed_frame_for_game_play is None:
                self.game_state["frame_count"] += 1
                return None

            # Detect Player Character
            player_bounding_box = get_player_character_bounding_box(processed_frame_for_game_play, self.game.screen_regions["GAME_PLAYER_AREA"])

            if player_bounding_box:
                player_bounding_box_center = (
                    (player_bounding_box[0] + player_bounding_box[2]) // 2,
                    (player_bounding_box[1] + player_bounding_box[3]) // 2,
                )

                player_to_center_angle = self.frame_angles_to_center[player_bounding_box_center]
                player_to_center_distance = self.frame_distances_to_center[player_bounding_box_center]

                # Mask out center & player
                processed_frame_for_game_play[self.frame_distances_to_center < (player_to_center_distance + (player_bounding_box[3] - player_bounding_box[1]))] = 0

                rays = lib.raycasting.generate_rays(player_to_center_angle, mode="UNIFORM", quantity=self.game_state["ray_configurations"][self.game_state["current_ray_angle"]][self.game_state["current_ray_angle_quantity_index"]], starting_angle=self.game_state["current_ray_angle"])
                ray_collision_distances = lib.raycasting.calculate_minimum_collision_distances(
                    rays,
                    processed_frame_for_game_play,
                    self.frame_angles_to_center,
                    self.frame_distances_to_center
                )

                if ray_collision_distances["Ray Player"] <= self.game_state["collision_threshold"]:
                    best_ray = max(ray_collision_distances.items(), key=lambda i: i[1])[0]

                    if best_ray == "Ray Player":
                        self.game_state["frame_count"] += 1
                        return None

                    direction, magnitude = best_ray.split(" ")[2:]

                    self.input_controller.tap_key(
                        self.key_direction_mapping[direction],
                        duration=(int(magnitude) / 15) * self.game_state["keypress_durations"][self.game_state["keypress_duration_index"]]
                    )
        elif context == "Death Screen":
            death_time_last = " ".join(lib.ocr.words_in_image_region(
                frame.frame,
                self.game.screen_regions["DEATH_TIME_LAST"],
                self.machine_learning_models["ocr_classifier"],
                word_window_size=(1, 8)
            ))

            try:
                score = float(death_time_last.replace(":", ".").replace("o", "0").replace("b", "8").replace("s", "5").replace("g", "6"))
            except ValueError:
                score = None

            print(death_time_last)
            print(score)

            if "%.4f" % self.game_state["keypress_durations"][self.game_state["keypress_duration_index"]] not in self.game_state["scores"]:
                self.game_state["scores"]["%.4f" % self.game_state["keypress_durations"][self.game_state["keypress_duration_index"]]] = list()

            if score is not None:
                self.game_state["scores"]["%.4f" % self.game_state["keypress_durations"][self.game_state["keypress_duration_index"]]].append(score)

            score_averages = {duration: (np.max(scores or [0.0]), np.mean(scores or [0.0])) for duration, scores in self.game_state["scores"].items()}

            print("\033c")

            pprint(score_averages)

            print("")
            print("Total Runs: " + str(self.game_state["total_runs"]))
            print("Current Keypress Duration: " + str(self.game_state["keypress_durations"][self.game_state["keypress_duration_index"]]))
            print("Current Collision Threshold: " + str(self.game_state["collision_threshold"]))
            print("Current Ray Angle: " + str(self.game_state["current_ray_angle"]))
            print("Current Ray Quantity: " + str(self.game_state["ray_configurations"][self.game_state["current_ray_angle"]][self.game_state["current_ray_angle_quantity_index"]]))

            with open(f"scores_{self.game_state['current_ray_angle']}_{self.game_state['ray_configurations'][self.game_state['current_ray_angle']][self.game_state['current_ray_angle_quantity_index']]}_hexagon.json", "w") as f:
                f.write(json.dumps(score_averages))

            if len(self.game_state["scores"]["%.4f" % self.game_state["keypress_durations"][self.game_state["keypress_duration_index"]]]) >= self.game_state["max_run"]:
                self.game_state["keypress_duration_index"] += 1

                if self.game_state["keypress_duration_index"] >= len(self.game_state["keypress_durations"]):
                    self.game_state["keypress_duration_index"] = 0

                    self.game_state["current_ray_angle_quantity_index"] += 1

                    if self.game_state["current_ray_angle_quantity_index"] == len(self.game_state["ray_configurations"][self.game_state["current_ray_angle"]]):
                        self.game_state["current_ray_angle_quantity_index"] = 0
                        self.game_state["current_ray_angle"] += 15

                    self.game_state["scores"] = {}

            self.input_controller.tap_key(self.input_controller.keyboard.enter_key)
            self.game_state["total_runs"] += 1
            time.sleep(10 / 60)

        self.game_state["frame_count"] += 1
