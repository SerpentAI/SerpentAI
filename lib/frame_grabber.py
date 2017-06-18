import numpy as np

from PIL import Image

import gi
gi.require_version('Gdk', '3.0')

from gi.repository import Gdk

from redis import StrictRedis

from lib.config import config

import time
from datetime import datetime

import skimage.transform
import skimage.color


class FrameGrabber:

    def __init__(self, width=640, height=480, x_offset=0, y_offset=0, fps=30):
        self.width = width
        self.height = height

        self.x_offset = x_offset
        self.y_offset = y_offset

        self.frame_time = 1 / fps

        self.redis_client = StrictRedis(**config["redis"])

        # Clear any previously stored frames
        self.redis_client.delete(config["frame_grabber"]["redis_key"])

    def start(self):
        while True:
            cycle_start = datetime.utcnow()
            frame = self.grab_frame()

            self.redis_client.set(config["frame_grabber"]["redis_key"], frame.tobytes())

            mini_frame = np.array(
                skimage.transform.resize(
                    frame,
                    (frame.shape[0] // 8, frame.shape[1] // 8),
                    order=0,
                    preserve_range=True
                ),
                dtype="uint8"
            )

            mini_frame_gray = np.array(skimage.color.rgb2gray(mini_frame), dtype="float16")

            self.redis_client.set(config["frame_grabber"]["redis_key"] + ":MINI", mini_frame_gray.tobytes())

            cycle_end = datetime.utcnow()

            cycle_duration = (cycle_end - cycle_start).microseconds / 1000000
            frame_time_left = self.frame_time - cycle_duration

            if frame_time_left > 0:
                time.sleep(frame_time_left)

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
