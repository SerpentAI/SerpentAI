import offshoot

from serpent.config import config

import time
import uuid
import pickle

import os
import os.path

import serpent.cv
import serpent.ocr
import serpent.utilities

from serpent.frame_grabber import FrameGrabber
from serpent.game_frame_buffer import GameFrameBuffer
from serpent.sprite_identifier import SpriteIdentifier
from serpent.visual_debugger.visual_debugger import VisualDebugger

import skimage.io
import skimage.transform

from redis import StrictRedis

from datetime import datetime


class GameAgentError(BaseException):
    pass


class GameAgent(offshoot.Pluggable):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.game = kwargs["game"]
        self.game.api

        self.config = config.get(f"{self.__class__.__name__}Plugin") or dict()

        self.redis_client = StrictRedis(**config["redis"])

        self.input_controller = kwargs["input_controller"]
        self.machine_learning_models = dict()

        self.frame_handlers = dict(
            NOOP=self.handle_noop,
            COLLECT_FRAMES=self.handle_collect_frames,
            COLLECT_FRAME_REGIONS=self.handle_collect_frame_regions,
            COLLECT_FRAMES_FOR_CONTEXT=self.handle_collect_frames_for_context
        )

        self.frame_handler_setups = dict(
            COLLECT_FRAMES_FOR_CONTEXT=self.setup_collect_frames_for_context
        )

        self.frame_handler_setup_performed = False

        self.visual_debugger = VisualDebugger()

        self.game_frame_buffer = GameFrameBuffer(size=self.config.get("game_frame_buffer_size", 5))
        self.game_context = None

        self.sprite_identifier = SpriteIdentifier()
        self._register_sprites()

        self.flag = None

        self.uuid = str(uuid.uuid4())
        self.started_at = datetime.now()

    @offshoot.forbidden
    def on_game_frame(self, game_frame, frame_handler=None, **kwargs):
        if not self.frame_handler_setup_performed:
            self._setup_frame_handler(frame_handler=frame_handler, **kwargs)

        frame_handler = self.frame_handlers.get(frame_handler or self.config.get("frame_handler", "NOOP"))

        frame_handler(game_frame, **kwargs)

        self.game_frame_buffer.add_game_frame(game_frame)

    @offshoot.forbidden
    def load_machine_learning_model(self, file_path):
        with open(file_path, "rb") as f:
            serialized_classifier = f.read()

        return pickle.loads(serialized_classifier)

    @offshoot.forbidden
    def update_game_frame(self, game_frame):
        game_frame_buffer = FrameGrabber.get_frames([0], frame_shape=game_frame.frame.shape)
        return game_frame_buffer.frames[0]

    def handle_noop(self, game_frame, **kwargs):
        time.sleep(1)

    def setup_collect_frames_for_context(self, **kwargs):
        context = kwargs.get("context") or config["frame_handlers"]["COLLECT_FRAMES_FOR_CONTEXT"]["context"]

        if not os.path.isdir(f"datasets/collect_frames_for_context/{context}"):
            os.mkdir(f"datasets/collect_frames_for_context/{context}")

        self.collected_frame_count = 0

    def handle_collect_frames(self, game_frame, **kwargs):
        skimage.io.imsave(f"datasets/collect_frames/frame_{str(uuid.uuid4())}.png", game_frame.frame)
        time.sleep(kwargs.get("interval") or self.config.get("collect_frames_interval") or 1)

    def handle_collect_frame_regions(self, game_frame, **kwargs):
        region = kwargs["region"]
        region_path = f"datasets/collect_frames/{region}"

        frame_region = serpent.cv.extract_region_from_image(game_frame.frame, self.game.screen_regions.get(region))

        if not os.path.isdir(region_path):
            os.mkdir(region_path)

        skimage.io.imsave(f"{region_path}/region_{str(uuid.uuid4())}.png", frame_region)
        time.sleep(kwargs.get("interval") or self.config.get("collect_frames_interval") or 1)

    def handle_collect_frames_for_context(self, game_frame, **kwargs):
        context = kwargs.get("context") or config["frame_handlers"]["COLLECT_FRAMES_FOR_CONTEXT"]["context"]
        interval = kwargs.get("interval") or config["frame_handlers"]["COLLECT_FRAMES_FOR_CONTEXT"]["interval"]

        resized_frame = skimage.transform.resize(
            game_frame.frame,
            (game_frame.frame.shape[0] // 2, game_frame.frame.shape[1] // 2)
        )

        file_name = f"datasets/collect_frames_for_context/{context}/frame_{str(uuid.uuid4())}.png"
        skimage.io.imsave(file_name, resized_frame)

        self.collected_frame_count += 1

        serpent.utilities.clear_terminal()
        print(f"Collected Frame #{self.collected_frame_count} for Context: {context}")

        time.sleep(interval)

    def _setup_frame_handler(self, frame_handler=None, **kwargs):
        frame_handler = frame_handler or self.config.get("frame_handler", "NOOP")

        if frame_handler in self.frame_handler_setups:
            self.frame_handler_setups[frame_handler](**kwargs)

        self.frame_handler_setup_performed = True

    def _register_sprites(self):
        for sprite_name, sprite in self.game.sprites.items():
            self.sprite_identifier.register(sprite)
