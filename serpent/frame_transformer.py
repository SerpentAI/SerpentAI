import skimage.transform
import skimage.color
import skimage.util


class FrameTransformer:

    def __init__(self):
        pass

    @staticmethod
    def resize(frame, size_string=None):
        width, height = size_string.lower().split("x")
        return skimage.util.img_as_ubyte(skimage.transform.resize(frame, (int(height), int(width))))

    @staticmethod
    def rescale(frame, scale=None):
        return skimage.util.img_as_ubyte(skimage.transform.rescale(frame, float(scale)))

    @staticmethod
    def grayscale(frame):
        return skimage.util.img_as_ubyte(skimage.color.rgb2gray(frame))

    @staticmethod
    def to_float(frame):
        return skimage.util.img_as_float(frame)
