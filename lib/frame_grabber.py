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

from lib.game_frame import GameFrame
from lib.game_frame_buffer import GameFrameBuffer


redis_client = StrictRedis(**config["redis"])


class FrameGrabber:

    def __init__(self, width=640, height=480, x_offset=0, y_offset=0, fps=30, buffer_seconds=5):
        self.width = width
        self.height = height

        self.x_offset = x_offset
        self.y_offset = y_offset

        self.frame_time = 1 / fps
        self.frame_buffer_size = buffer_seconds * fps

        self.redis_client = redis_client

        # Clear any previously stored frames
        self.redis_client.delete(config["frame_grabber"]["redis_key"])

    def start(self):
        while True:
            cycle_start = datetime.utcnow()
            frame = self.grab_frame()

            self.redis_client.lpush(config["frame_grabber"]["redis_key"], frame.tobytes())
            self.redis_client.ltrim(config["frame_grabber"]["redis_key"], 0, self.frame_buffer_size)

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

            self.redis_client.lpush(config["frame_grabber"]["redis_key"] + ":MINI", mini_frame_gray.tobytes())
            self.redis_client.ltrim(config["frame_grabber"]["redis_key"] + ":MINI", 0, self.frame_buffer_size)

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

    @classmethod
    def get_frames(cls, frame_buffer_indices, frame_shape=None, mode="BOTH"):
        game_frame_buffer = GameFrameBuffer(size=len(frame_buffer_indices))

        for i in frame_buffer_indices:
            game_frame = None

            if mode in ["FULL", "BOTH"]:
                frame_bytes = redis_client.lindex(config["frame_grabber"]["redis_key"], i)
                frame_array = np.fromstring(frame_bytes, dtype="uint8").reshape(frame_shape)

                game_frame = GameFrame(frame_array)

            if mode in ["MINI", "BOTH"]:
                mini_frame_shape = (frame_shape[0] // 8, frame_shape[1] // 8)

                mini_frame_bytes = redis_client.lindex(config["frame_grabber"]["redis_key"] + ":MINI", i)
                mini_frame_array = np.fromstring(mini_frame_bytes, dtype="float16").reshape(mini_frame_shape)

            if mode == "BOTH":
                game_frame.frame_variants["eighth_grayscale"] = mini_frame_array
            elif mode == "MINI":
                game_frame = GameFrame(mini_frame_array, frame_variants={"eighth_grayscale": mini_frame_array})

            game_frame_buffer.add_game_frame(game_frame)

        return game_frame_buffer
