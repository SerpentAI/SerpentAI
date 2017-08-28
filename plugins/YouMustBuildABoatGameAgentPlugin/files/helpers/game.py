__all__ = [
    "parse_game_board",
    "generate_game_board_deltas",
    "generate_boolean_game_board_deltas",
    "score_game_board_vector",
    "score_game_board",
    "display_game_board",
    "locate_player"
]

import numpy as np

import lib.cv

from lib.sprite import Sprite
from lib.sprite_identifier import SpriteIdentifier

from lib.games import YouMustBuildABoatGame

import xtermcolor
import random

import skimage.color
import skimage.filters
import skimage.morphology
import skimage.measure


game = YouMustBuildABoatGame()
sprite_identifier = SpriteIdentifier(pixel_quantity=10, iterations=3)

for sprite_name, sprite in game.sprites.items():
    sprite_identifier.register(sprite)


rows = ["A", "B", "C", "D", "E", "F"]
columns = [1, 2, 3, 4, 5, 6, 7, 8]

cell_sprite_mapping = {
    "UNKNOWN": 0,
    "BRAIN": 1,
    "SWORD": 2,
    "WAND": 3,
    "SHIELD": 4,
    "CRATE": 5,
    "KEY": 6,
    "FLEX": 7,
    "BOW": 10,
    "DRUMSTICK": 11,
    "TNT": 12,
    "FROST": 13,
    "FIRE": 14,
    "SHOCK": 15
}

ansi_background_mapping = {
    0: 0,
    1: 60,
    2: 19,
    3: 52,
    4: 23,
    5: 94,
    6: 28,
    7: 54
}

display_mapping = {
    0: "--",
    1: "Th",
    2: "Sw",
    3: "St",
    4: "Sh",
    5: "Cr",
    6: "Ke",
    7: "Po"
}


def parse_game_board(frame):
    parsed_rows = list()

    for row in rows:
        row_cells = list()

        for column in columns:
            screen_region = f"GAME_BOARD_{row}{column}"

            cell = lib.cv.extract_region_from_image(frame, game.screen_regions.get(screen_region))
            cell_sprite = Sprite(screen_region, image_data=cell[:, :, :, np.newaxis])

            cell_label = sprite_identifier.identify(cell_sprite)
            row_cells.append(cell_sprite_mapping.get(cell_label.split("_")[-1], 0))

        parsed_rows.append(row_cells)

    return np.array(parsed_rows)


def generate_game_board_deltas(game_board):
    game_board_deltas = list()

    # Rows
    for i in range(6):
        row = game_board[i, :]

        for ii in range(7):
            label = f"{rows[i]}1 to {rows[i]}{columns[ii + 1]}"

            row_delta = np.roll(row, ii + 1, axis=0)

            board_delta = np.copy(game_board)
            board_delta[i, :] = row_delta

            game_board_deltas.append((label, board_delta, "ROW", i))

    # Columns
    for i in range(8):
        column = game_board[:, i]

        for ii in range(5):
            label = f"A{columns[i]} to {rows[ii + 1]}{columns[i]}"
            column_delta = np.roll(column, ii + 1, axis=0)

            board_delta = np.copy(game_board)
            board_delta[:, i] = column_delta

            game_board_deltas.append((label, board_delta, "COLUMN", i))

    return game_board_deltas


def generate_boolean_game_board_deltas(game_board_deltas, obfuscate=False):
    boolean_game_boards = dict()

    for game_board_delta in game_board_deltas:
        for i in range(7):
            boolean_game_board = np.copy(game_board_delta[1])

            boolean_game_board[boolean_game_board != (i + 1)] = 0
            boolean_game_board[boolean_game_board == (i + 1)] = 1

            boolean_game_board = boolean_game_board.astype("bool")

            if game_board_delta[0] not in boolean_game_boards:
                boolean_game_boards[game_board_delta[0]] = list()

            if obfuscate:
                try:
                    obfuscate_coordinates = random.choice(list(np.argwhere(boolean_game_board)))
                    boolean_game_board[obfuscate_coordinates[0], obfuscate_coordinates[1]] = False
                except IndexError:
                    pass

            boolean_game_boards[game_board_delta[0]].append(boolean_game_board)

    return boolean_game_boards


def score_game_board_vector(game_board_vector):
    score = 0

    for i in range(len(game_board_vector) - 2):
        game_board_vector_window = game_board_vector[i:i + 3]

        if np.unique(game_board_vector_window).size == 1 and 0 not in game_board_vector_window:
            score += 1

    return score


def score_game_board(game_board):
    score = 0

    for i in range(6):
        row = game_board[i, :]
        score += score_game_board_vector(row)

    for i in range(8):
        column = game_board[:, i]
        score += score_game_board_vector(column)

    return score


def display_game_board(game_board):
    for i in range(6):
        row = list()

        for ii in range(8):
            row.append(
                xtermcolor.colorize(
                    f" {display_mapping.get(game_board[i, ii], '--')} ",
                    ansi=15,
                    ansi_bg=ansi_background_mapping.get(game_board[i, ii], 0))
            )

        print("  ".join(row))
        print("")


def locate_player(above_game_board):
    gray_above_board_frame = np.array(skimage.color.rgb2gray(above_game_board) * 255, dtype="uint8")
    bw_above_board_frame = gray_above_board_frame > 180

    closed_bw_above_board_frame = skimage.morphology.closing(
        bw_above_board_frame,
        skimage.morphology.rectangle(4, 8)
    )

    max_height = 0
    player_bounding_box = None

    for region in skimage.measure.regionprops(skimage.measure.label(closed_bw_above_board_frame)):
        if region.area < 150:
            continue

        y0, x0, y1, x1 = region.bbox

        if y1 - y0 > max_height:
            max_height = y1 - y0
            player_bounding_box = region.bbox

    return player_bounding_box