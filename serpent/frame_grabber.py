import numpy as np

import mss

from redis import StrictRedis

import skimage.transform
import skimage.util

from serpent.config import config

import sys
import time

from datetime import datetime

from serpent.game_frame import GameFrame
from serpent.game_frame_buffer import GameFrameBuffer

from serpent.frame_transformation_pipeline import FrameTransformationPipeline


redis_client = StrictRedis(**config["redis"])


class FrameGrabber:

    def __init__(self, width=640, height=480, x_offset=0, y_offset=0, fps=30, pipeline_string=None, buffer_seconds=5):
        self.width = width
        self.height = height

        self.x_offset = x_offset
        self.y_offset = y_offset

        self.frame_time = 1 / fps
        self.frame_buffer_size = buffer_seconds * fps

        self.redis_client = redis_client
        self.screen_grabber = mss.mss()

        self.frame_transformation_pipeline = None

        if pipeline_string is not None and isinstance(pipeline_string, str):
            self.frame_transformation_pipeline = FrameTransformationPipeline(pipeline_string=pipeline_string)

        self.is_retina_display = False
        self.is_retina_display = self._perform_retina_display_check()

        # Clear any previously stored frames
        self.redis_client.delete(config["frame_grabber"]["redis_key"])
        self.redis_client.delete(config["frame_grabber"]["redis_key"] + "_PIPELINE")

    def start(self):
        while True:
            cycle_start = datetime.utcnow()

            frame = self.grab_frame()

            if self.frame_transformation_pipeline is not None:
                frame_pipeline = self.frame_transformation_pipeline.transform(frame)
            else:
                frame_pipeline = frame

            self.redis_client.lpush(config["frame_grabber"]["redis_key"], frame.tobytes())
            self.redis_client.ltrim(config["frame_grabber"]["redis_key"], 0, self.frame_buffer_size)

            self.redis_client.lpush(config["frame_grabber"]["redis_key"] + "_PIPELINE", frame_pipeline.tobytes())
            self.redis_client.ltrim(config["frame_grabber"]["redis_key"] + "_PIPELINE", 0, self.frame_buffer_size)

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

        if self.is_retina_display:
            frame = skimage.util.img_as_ubyte(skimage.transform.resize(frame, (frame.shape[0] // 2, frame.shape[1] // 2)))
            frame = frame[:self.height, :self.width, :]

        return frame[..., :3]

    def _perform_retina_display_check(self):
        retina_display = False

        if sys.platform == "darwin":
            frame = self.grab_frame()

            if frame.shape[0] > self.height:
                retina_display = True

        return retina_display

    @classmethod
    def get_frames(cls, frame_buffer_indices, frame_shape=None, frame_type="FULL"):
        game_frame_buffer = GameFrameBuffer(size=len(frame_buffer_indices))

        for i in frame_buffer_indices:
            redis_key = config["frame_grabber"]["redis_key"]
            redis_key = redis_key + "_PIPELINE" if frame_type == "PIPELINE" else redis_key

            frame_bytes = redis_client.lindex(redis_key, i)
            frame_array = np.fromstring(frame_bytes, dtype="uint8").reshape(frame_shape)

            game_frame = GameFrame(frame_array)

            game_frame_buffer.add_game_frame(game_frame)

        return game_frame_buffer
