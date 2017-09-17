import numpy as np

import mss

from redis import StrictRedis

from serpent.config import config

import time
from datetime import datetime

from serpent.game_frame import GameFrame
from serpent.game_frame_buffer import GameFrameBuffer


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
        self.screen_grabber = mss.mss()

        # Clear any previously stored frames
        self.redis_client.delete(config["frame_grabber"]["redis_key"])

    def start(self):
        while True:
            cycle_start = datetime.utcnow()
            frame = self.grab_frame()

            self.redis_client.lpush(config["frame_grabber"]["redis_key"], frame.tobytes())
            self.redis_client.ltrim(config["frame_grabber"]["redis_key"], 0, self.frame_buffer_size)

            cycle_end = datetime.utcnow()
            cycle_duration = (cycle_end - cycle_start).microseconds / 1000000

            frame_time_left = self.frame_time - cycle_duration

            if frame_time_left > 0:
                time.sleep(frame_time_left)

    def grab_frame(self):
        frame = np.array(
            self.screen_grabber.grab({
                "top": self.y_offset,
                "left": self.x_offset,
                "width": self.width,
                "height": self.height
            }),
            dtype="uint8"
        )

        frame = frame[..., [2, 1, 0, 3]]

        return frame[..., :3]

    @classmethod
    def get_frames(cls, frame_buffer_indices, frame_shape=None):
        game_frame_buffer = GameFrameBuffer(size=len(frame_buffer_indices))

        for i in frame_buffer_indices:
            frame_bytes = redis_client.lindex(config["frame_grabber"]["redis_key"], i)
            frame_array = np.fromstring(frame_bytes, dtype="uint8").reshape(frame_shape)

            game_frame = GameFrame(frame_array)

            game_frame_buffer.add_game_frame(game_frame)

        return game_frame_buffer
