import lib.cv

import skimage.color
import skimage.filters
import skimage.segmentation
import skimage.exposure
import skimage.morphology

from lib.visual_debugger.visual_debugger import VisualDebugger

import numpy as np

visual_debugger = VisualDebugger()


def get_map_grid_image_data(gray_frame, game):
    """
        gray_frame: Grayscale Game Frame (np.ndarray)
        game: Game instance
    """

    room_layout_type = get_room_layout_type(gray_frame, game)
    map_gray_frame = lib.cv.extract_region_from_image(gray_frame, game.screen_regions["HUD_MAP"])

    if room_layout_type == "NORMAL_ROOM":
        map_gray_frame = map_gray_frame[10:81, 12:93]
    elif room_layout_type == "BIG_SQUARE_ROOM":
        map_gray_frame = map_gray_frame[3:74, 4:85]
    elif room_layout_type == "BIG_HORIZONTAL_RECTANGLE_ROOM":
        map_gray_frame = map_gray_frame[10:81, 4:85]
    elif room_layout_type == "BIG_VERTICAL_RECTANGLE_ROOM":
        map_gray_frame = map_gray_frame[3:74, 12:93]
    else:
        map_gray_frame = map_gray_frame[10:81, 12:93]

    map_gradient_frame = skimage.filters.rank.gradient(map_gray_frame, skimage.morphology.square(5))

    try:
        threshold = 20
    except ValueError:
        threshold = -1

    map_bw_frame = map_gray_frame > threshold
    map_clear_frame = skimage.segmentation.clear_border(map_bw_frame)

    return map_clear_frame


def get_room_layout_type(gray_frame, game):
    """
        gray_frame: Grayscale Game Frame (np.ndarray)
        game: Game instance
    """
    room_layouts = {
        (0, 0, 0, 0): "NORMAL_ROOM",
        (1, 1, 1, 1): "BIG_SQUARE_ROOM",
        (0, 1, 0, 1): "BIG_HORIZONTAL_RECTANGLE_ROOM",
        (1, 0, 1, 0): "BIG_VERTICAL_RECTANGLE_ROOM"
    }

    map_center_frame = lib.cv.extract_region_from_image(gray_frame, game.screen_regions["HUD_MAP_CENTER"])

    try:
        threshold = skimage.filters.threshold_otsu(map_center_frame)
    except ValueError:
        threshold = -1

    bw_map_center_frame = map_center_frame > threshold

    room_layout = (
        bw_map_center_frame[0, 7],
        bw_map_center_frame[7, 15],
        bw_map_center_frame[13, 7],
        bw_map_center_frame[7, 0]
    )

    return room_layouts.get(room_layout, "UNKNOWN")

