import numpy as np

import skimage.feature
import skimage.io
import skimage.measure
import skimage.morphology
import skimage.segmentation
import skimage.color
import skimage.util
import skimage.exposure
import skimage.filters


def preprocess(frame, **preprocessing_options):
    grayscale_frame = np.array(skimage.color.rgb2gray(frame) * 255, dtype="uint8")

    # lower, higher = np.percentile(grayscale_frame, preprocessing_options["contrast_stretch_percentiles"])
    # grayscale_frame = skimage.exposure.rescale_intensity(grayscale_frame, in_range=(lower, higher))

    try:
        threshold = skimage.filters.threshold_local(grayscale_frame, 999)
        preprocessed_frame = grayscale_frame > threshold
    except ValueError:
        preprocessed_frame = grayscale_frame > -1

    cleared_preprocessed_frame = skimage.segmentation.clear_border(preprocessed_frame)

    return cleared_preprocessed_frame
