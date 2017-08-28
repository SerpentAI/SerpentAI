from invoke import task

from lib.frame_grabber import FrameGrabber
from lib.games import *

import lib.datasets

from plugins.YouMustBuildABoatGameAgentPlugin.files.helpers.game import *
from lib.machine_learning.context_classification.context_classifiers import SVMContextClassifier
from lib.machine_learning.context_classification.context_classifiers import CNNInceptionV3ContextClassifier

import numpy as np

import skimage.io
import skimage.transform

import sklearn.linear_model

import sklearn
import os
import h5py
import pickle
import itertools
import math


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

@task
def boat_grid_search_model(ctx):
    rows = ["A", "B", "C", "D", "E", "F"]
    columns = [1, 2, 3, 4, 5, 6, 7, 8]

    grid_template = {
        "loss": ["squared_loss", "huber", "epsilon_insensitive", "squared_epsilon_insensitive"],
        "penalty": ["none", "l1", "l2", "elasticnet"],
        "alpha": [0.1, 0.01, 0.001, 0.0001, 0.00001, 0.000001, 0.0000001],
        "l1_ratio": [round(float(f), 2) for f in np.linspace(0, 1, 21)],
        "epsilon": [round(float(f), 2) for f in np.linspace(0.001, 0.1, 11)],
        "learning_rate": ["constant", "optimal", "invscaling"],
        "eta0": [pow(10, -(i + 2)) for i in range(7)]
    }

    grid_key_mapping = {
        0: "loss",
        1: "penalty",
        2: "alpha",
        3: "l1_ratio",
        4: "learning_rate",
        5: "eta0"
    }

    grid = {
        "loss": ["squared_loss"],
        "penalty": ["elasticnet"],
        "alpha": [1e-07],
        "l1_ratio": [0.45],
        "learning_rate": ["invscaling"],
        "eta0": np.exp(np.linspace(0.0, math.log(1e-1 / 1e-10), 50)) * 1e-10
    }

    datasets = list()

    # Calculate the optimal scores
    optimal_score = 0

    for root, dirs, files in os.walk("datasets/ymbab-good"):
        for file in files:
            if not file.endswith(".png"):
                continue

            frame = skimage.io.imread(f"datasets/ymbab-good/{file}")

            game_board = parse_game_board(frame)
            game_board_deltas = generate_game_board_deltas(game_board)

            top_score = 0

            for game_board_delta in game_board_deltas:
                score = score_game_board(game_board_delta[1])

                if score > top_score:
                    top_score = score

            optimal_score += top_score

    # Load the training data from the HDF5 files
    for root, dirs, files in os.walk("datasets/ymbab-bk"):
        for index, file in enumerate(files):
            if not file.endswith(".h5"):
                continue

            print(f"Loading training data from {file}... {index + 1}/{len(files)}")

            data = list()
            scores = list()

            with h5py.File(f"datasets/ymbab-bk/{file}", "r") as f:
                count = len(f.items()) // 2

                for i in range(count):
                    data.append(f[f"{i}"][:])
                    scores.append(f[f"{i}_score"].value)

            if len(data):
                datasets.append((data, scores))

    # Generate product of grid search arguments
    grid_search_args = itertools.product(*grid.values())

    model_scores = dict()

    for model_args in list(grid_search_args):
        model_kwargs = dict()

        for index, model_arg in enumerate(model_args):
            model_kwargs[grid_key_mapping[index]] = model_arg

        model = sklearn.linear_model.SGDRegressor(**model_kwargs)

        print(f"Training model: {str(model_kwargs)}...")

        for data, scores in datasets:
            model.partial_fit(data, scores)

        model_board_score = 0

        for root, dirs, files in os.walk("datasets/ymbab-good"):
            for index, file in enumerate(files):
                if not file.endswith(".png"):
                    continue

                print(f"Training model: {str(model_kwargs)}... Board {index + 1}/{len(files)}")

                frame = skimage.io.imread(f"datasets/ymbab-good/{file}")

                game_board = parse_game_board(frame)
                game_board_deltas = generate_game_board_deltas(game_board)

                boolean_game_board_deltas = generate_boolean_game_board_deltas(game_board_deltas)

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
                            row_index = rows.index(split_game_move[0][0])
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

                            column_index = columns.index(int(split_game_move[0][1]))
                            column = boolean_game_board[:, column_index]
                            column = np.append(column, [False, False])

                            input_vectors.append(column)

                        prediction = model.predict(input_vectors)
                        total_score += max(prediction)

                    game_move_scores[game_move] = total_score

                    if total_score > top_game_move_score:
                        top_game_move_score = total_score
                        top_game_move = game_move

                top_game_move_game_board_delta = None

                for game_board_delta in game_board_deltas:
                    if game_board_delta[0] == top_game_move:
                        top_game_move_game_board_delta = game_board_delta[1]
                        break

                model_board_score += score_game_board(top_game_move_game_board_delta)

        model_scores[str(model_kwargs)] = model_board_score

    print(f"Maximum achievable score: {optimal_score}")

    for model_name, model_score in model_scores.items():
        print(model_name, model_score)

    print("")
    print(f"Top model score: {str(max(model_scores, key=model_scores.values()))}")
    print(f"Maximum achievable score: {optimal_score}\n")
