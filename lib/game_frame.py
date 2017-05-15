import skimage.color
import skimage.measure
import skimage.transform

import numpy as np


class GameFrameError(BaseException):
    pass


class GameFrame:

    def __init__(self, frame_array):
        self.frame_array = frame_array
        self.frame_variants = dict()

    @property
    def frame(self):
        return self.frame_array

    @property
    def grayscale_frame(self):
        """ A full-size grayscale version of the frame"""

        if "grayscale" not in self.frame_variants:
            self.frame_variants["grayscale"] = self._to_grayscale()

        return self.frame_variants["grayscale"]

    @property
    def ssim_frame(self):
        """ A 100x100 grayscale frame to be used for SSIM"""

        if "ssim" not in self.frame_variants:
            self.frame_variants["ssim"] = self._to_ssim()

        return self.frame_variants["ssim"]

    def compare_ssim(self, previous_game_frame):
        return skimage.measure.compare_ssim(previous_game_frame.ssim_frame, self.ssim_frame)

    def _to_grayscale(self):
        return np.array(skimage.color.rgb2gray(self.frame_array) * 255, dtype="uint8")

    def _to_ssim(self):
        grayscale = self.grayscale_frame
        return skimage.transform.resize(grayscale, (100, 100), mode="reflect", order=0)
