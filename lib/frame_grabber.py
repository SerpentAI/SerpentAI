import numpy as np

from PIL import Image

import gi
gi.require_version('Gdk', '3.0')

from gi.repository import Gdk

from redis import StrictRedis

from lib.config import config


class FrameGrabber:

    def __init__(self, width=640, height=480, x_offset=0, y_offset=0):
        self.width = width
        self.height = height

        self.x_offset = x_offset
        self.y_offset = y_offset

        self.redis_client = StrictRedis(**config["redis"])

        # Clear any previously stored frames
        self.redis_client.delete(config["frame_grabber"]["redis_key"])

    def start(self):
        while True:
            self.redis_client.set(config["frame_grabber"]["redis_key"], self.grab_frame().tobytes())

    def grab_frame(self):
        window = Gdk.get_default_root_window()

        frame_buffer = Gdk.pixbuf_get_from_window(window, self.x_offset, self.y_offset, self.width, self.height)
        frame_buffer_data = frame_buffer.get_pixels()

        stride = frame_buffer.props.rowstride
        mode = "RGB"

        if frame_buffer.props.has_alpha:
            mode = "RGBA"

        pil_frame = Image.frombytes(mode, (self.width, self.height), frame_buffer_data, "raw", mode, stride)
        frame = np.array(pil_frame)

        return frame
