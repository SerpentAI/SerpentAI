import skimage.io
import skimage.transform
import skimage.exposure
import skimage.filters
import skimage.measure
import skimage.color
import skimage.segmentation

import numpy as np


def image_data_for_screen_region(frame, screen_region):
    return frame[screen_region[0]:screen_region[2], screen_region[1]:screen_region[3]]


def grayscale_frame(frame):
    return np.array(skimage.color.rgb2gray(frame) * 255, dtype="uint8")


def process_frame_for_context(frame):
    """Assumes a grayscale frame"""
    threshold = skimage.filters.threshold_local(frame, 21)
    bw_frame = frame > threshold

    return skimage.transform.resize(bw_frame, (30, 48), mode="reflect", order=0).astype("bool").flatten()


def process_frame_for_game_play(frame):
    """Assumes a grayscale frame"""
    histogram = skimage.exposure.histogram(frame[40:])

    if np.unique(histogram[0]).size < 3:
        return None

    max_indices = np.argpartition(histogram[0], -3)[-3:]

    for index in sorted(max_indices)[:2]:
        frame[frame == index] = 0

    threshold = skimage.filters.threshold_otsu(frame[40:])
    bw_frame = frame > threshold

    return bw_frame


def get_player_character_bounding_box(frame, screen_region):
    player_area_frame = image_data_for_screen_region(frame, screen_region)
    cleared_player_area_frame = skimage.segmentation.clear_border(player_area_frame)

    label_image = skimage.measure.label(cleared_player_area_frame)

    player_character_bounding_box = None

    for region in skimage.measure.regionprops(label_image):
        if region.area < 200:
            if region.bbox[0] > 50:
                player_character_bounding_box = [c + screen_region[i % 2] for i, c in enumerate(list(region.bbox))]

    return player_character_bounding_box
