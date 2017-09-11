from invoke import task

from lib.frame_grabber import FrameGrabber
from lib.games import *

import lib.datasets

from lib.machine_learning.context_classification.context_classifiers import SVMContextClassifier
from lib.machine_learning.context_classification.context_classifiers import CNNInceptionV3ContextClassifier

import skimage.io
import skimage.transform

import sklearn.linear_model

import sklearn
import os
import h5py
import pickle


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
def boat_context_train(ctx):
    lib.datasets.create_training_and_validation_sets(
        [
            "datasets/collect_frames_for_context/game_over",
            "datasets/collect_frames_for_context/level_gallery",
            "datasets/collect_frames_for_context/level_hell",
            "datasets/collect_frames_for_context/level_jail"
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


@task
def boat_train_model(ctx):
    model = sklearn.linear_model.SGDRegressor(
        loss="squared_loss",
        penalty="elasticnet",
        alpha=1e-7,
        l1_ratio=0.45,
        learning_rate="invscaling",
        eta0=0.0065
    )

    data_path = f"datasets/ymbab-bk"

    if os.path.isdir(data_path):
        files = os.scandir(data_path)

        for index, file in enumerate(files):
            print(f"Loading data from {file.name}... #{index + 1}")

            if file.name.endswith(".h5"):
                data = list()
                scores = list()

                with h5py.File(f"datasets/ymbab-bk/{file.name}", "r") as f:
                    count = len(f.items()) // 2

                    for i in range(count):
                        data.append(f[f"{i}"][:])
                        scores.append(f[f"{i}_score"].value)

                model.partial_fit(data, scores)

    serialized_model = pickle.dumps(model)

    with open("datasets/ymbab_matching.model", "wb") as f:
        f.write(serialized_model)
