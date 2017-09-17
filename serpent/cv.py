import numpy as np

import skimage.io
import skimage.util

import os


def extract_region_from_image(image, region_bounding_box):
    return image[region_bounding_box[0]:region_bounding_box[2], region_bounding_box[1]:region_bounding_box[3]]


def isolate_sprite(image_region_path, output_file_path):
    result_image = None

    for root, directories, files in os.walk(image_region_path):
        for file in files:
            if not file.endswith(".png"):
                continue

            image = skimage.io.imread(f"{root}/{file}")
            image = np.concatenate((image, np.full((image.shape[0], image.shape[1], 1), 255, dtype="uint8")), axis=2)

            if result_image is None:
                result_image = image
            else:
                height, width, rgba = image.shape

                for i in range(height):
                    for ii in range(width):
                        if not np.array_equal(image[i, ii, :2], result_image[i, ii, :2]):
                            result_image[i, ii, 3] = 0

    skimage.io.imsave(output_file_path, result_image)


def scale_range(n, minimum, maximum):
    n += -(np.min(n))
    n /= np.max(n) / (maximum - minimum)
    n += minimum

    return n
