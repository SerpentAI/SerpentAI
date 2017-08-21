import numpy as np


def extract_region_from_image(image, region_bounding_box):
    return image[region_bounding_box[0]:region_bounding_box[2], region_bounding_box[1]:region_bounding_box[3]]


def scale_range(n, minimum, maximum):
    n += -(np.min(n))
    n /= np.max(n) / (maximum - minimum)
    n += minimum

    return n
