from lib.game_agent import GameAgent

from lib.machine_learning.context_classification.context_classifiers import CNNInceptionV3ContextClassifier

import lib.cv

import numpy as np

import skimage.feature

import offshoot

import time


class YouMustBuildABoatGameAgent(GameAgent):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.frame_handlers["PLAY"] = self.handle_play

        self.frame_handler_setups["PLAY"] = self.setup_play

        self.analytics_client = None

    @property
    def game_contexts(self):
        return dict(

        )

    def setup_play(self):
        plugin_path = offshoot.config["file_paths"]["plugins"]

        context_classifier_path = f"{plugin_path}/YouMustBuildABoatGameAgentPlugin/files/ml_models/you_must_build_a_boat_context.model"

        context_classifier = CNNInceptionV3ContextClassifier(input_shape=(270, 480, 3))
        context_classifier.prepare_generators()
        context_classifier.load_classifier(context_classifier_path)

        self.machine_learning_models["context_classifier"] = context_classifier

    def handle_play(self, game_frame):
        context = self.machine_learning_models["context_classifier"].predict(game_frame.frame)

        if context == "menu":
            self.input_controller.click_screen_region(screen_region="MENU_CONTINUE", game=self.game)
            time.sleep(10)
        elif context == "boat":
            print("I'M ON A BOAT!!!!")

            sprite = self.game.sprites["SPRITE_SKELETON_ZOMBIE_GRAYSCALE"]
            grayscale_frame = game_frame.grayscale_frame

            sprite_matching = skimage.feature.match_template(grayscale_frame, sprite, pad_input=True)
            print(sprite_matching.max())

            if sprite_matching.max() >= 0.8:
                sprite_best_match = np.unravel_index(sprite_matching.argmax(), sprite_matching.shape)
                self.input_controller.click(button="LEFT", x=sprite_best_match[1], y=sprite_best_match[0])
            else:
                print("Cannot find the skelyzombie :(")

            time.sleep(1)








