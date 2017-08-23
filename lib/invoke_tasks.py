from invoke import task

from lib.frame_grabber import FrameGrabber
from lib.games import *

import lib.datasets

from lib.machine_learning.context_classification.context_classifiers import SVMContextClassifier
from lib.machine_learning.context_classification.context_classifiers import CNNInceptionV3ContextClassifier

import numpy as np

import skimage.io
import skimage.transform

from lib.config import config


@task
def start_frame_grabber(ctx, width=640, height=480, x_offset=0, y_offset=0):
    frame_grabber = FrameGrabber(
        width=width,
        height=height,
        x_offset=x_offset,
        y_offset=y_offset
    )

    frame_grabber.start()

# Shortcut Tasks

@task
def hexagon(ctx):
    game = SuperHexagonGame()
    game.launch()
    game.play(game_agent_class_name="SuperHexagonGameAgent")


@task
def isaac(ctx):
    game = BindingOfIsaacRebirthGame()
    game.launch()
    game.play(game_agent_class_name="BindingOfIsaacRebirthGameAgent")


@task
def isaac_launch(ctx):
    game = BindingOfIsaacRebirthGame()
    game.launch()


@task
def isaac_play(ctx):
    game = BindingOfIsaacRebirthGame()
    game.launch(dry_run=True)
    game.play(game_agent_class_name="BindingOfIsaacRebirthGameAgent")


@task
def boat_launch(ctx):
    game = YouMustBuildABoatGame()
    game.launch()


@task
def boat_play(ctx):
    game = YouMustBuildABoatGame()
    game.launch(dry_run=True)
    game.play(game_agent_class_name="YouMustBuildABoatGameAgent")

@task
def capture_context(ctx, game='', context='unnamed', interval=1):
    game_class = offshoot.discover("Game").get(game)

    if game_class is None:
        raise Exception("The provided Game Agent class name does not map to an existing class...")

    game = game_class()
    game.launch(dry_run=True)
    config["frame_handlers"]["COLLECT_FRAMES_FOR_CONTEXT"]["context"] = context
    config["frame_handlers"]["COLLECT_FRAMES_FOR_CONTEXT"]["interval"] = interval
    game.play(game_agent_class_name="GenericFrameGrabberAgent")

@task
def boat_context_train(ctx):
    lib.datasets.create_training_and_validation_sets(
        [
            "datasets/collect_frames_for_context/game_over",
            "datasets/collect_frames_for_context/level_gallery",
            "datasets/collect_frames_for_context/level_hell",
            "datasets/collect_frames_for_context/level_jail",
            "datasets/collect_frames_for_context/level_pagoda",
            "datasets/collect_frames_for_context/level_pyramid",
            "datasets/collect_frames_for_context/level_ruins",
            "datasets/collect_frames_for_context/level_sewers",
            "datasets/collect_frames_for_context/level_thicket",
            "datasets/collect_frames_for_context/level_tower",
            "datasets/collect_frames_for_context/level_vault",
        ]
    )

    context_classifier = CNNInceptionV3ContextClassifier(input_shape=(384, 512, 3))

    context_classifier.train()

    # context_classifier = SVMContextClassifier()

    # context_classifier.train(preprocessing_func=boat_context_preprocess)
    # context_classifier.validate(preprocessing_func=boat_context_preprocess)

    context_classifier.save_classifier("datasets/you_must_build_a_boat_context.model")


def boat_context_preprocess(frame):
    return skimage.transform.resize(frame,(frame.shape[0] // 32, frame.shape[1] // 32))
