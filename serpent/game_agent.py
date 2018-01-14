import offshoot

from serpent.config import config

import time
import uuid
import pickle
import io
import h5py
import random

import os
import os.path

import serpent.cv
import serpent.ocr
import serpent.utilities

from serpent.frame_grabber import FrameGrabber
from serpent.game_frame import GameFrame
from serpent.game_frame_buffer import GameFrameBuffer
from serpent.sprite_identifier import SpriteIdentifier
from serpent.input_controller import keyboard_module_scan_code_mapping
from serpent.visual_debugger.visual_debugger import VisualDebugger

import skimage.io
import skimage.transform
import skimage.util

from PIL import Image

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
            COLLECT_FRAMES_FOR_CONTEXT=self.handle_collect_frames_for_context,
            RECORD=self.handle_record
        )

        self.frame_handler_setups = dict(
            COLLECT_FRAMES=self.setup_collect_frames,
            COLLECT_FRAME_REGIONS=self.setup_collect_frame_regions,
            COLLECT_FRAMES_FOR_CONTEXT=self.setup_collect_frames_for_context,
            RECORD=self.setup_handle_record
        )

        self.frame_handler_pause_callbacks = dict(
            COLLECT_FRAMES=self.on_collect_frames_pause,
            COLLECT_FRAME_REGIONS=self.on_collect_frame_regions_pause,
            COLLECT_FRAMES_FOR_CONTEXT=self.on_collect_frames_for_context_pause,
            RECORD=self.on_record_pause
        )

        self.reward_functions = dict(
            TEST=self.reward_test   
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
    def on_pause(self, frame_handler=None, **kwargs):
        on_frame_handler_pause = self.frame_handler_pause_callbacks.get(frame_handler or self.config.get("frame_handler"))

        if on_frame_handler_pause is not None:
            on_frame_handler_pause(**kwargs)

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

    def setup_collect_frames(self, **kwargs):
        self.game_frames = list()
        self.collected_frame_count = 0

    def setup_collect_frame_regions(self, **kwargs):
        self.game_frames = list()
        self.collected_frame_count = 0

    def setup_collect_frames_for_context(self, **kwargs):
        context = kwargs.get("context") or config["frame_handlers"]["COLLECT_FRAMES_FOR_CONTEXT"]["context"]

        if not os.path.isdir(f"datasets/collect_frames_for_context/{context}"):
            os.mkdir(f"datasets/collect_frames_for_context/{context}")

        self.game_frames = list()
        self.collected_frame_count = 0

    def setup_handle_record(self, **kwargs):
        self.frame_input_pairs = list()
        
        self.keyboard_events = dict()
        
        self.frame_keys = dict()
        self.frame_keyboard_events = dict()

        time.sleep(1)

        serpent.utilities.clear_terminal()
        print("Start playing the game! Focus out when you are done or want to save the collected data to that point.")

    def handle_collect_frames(self, game_frame, **kwargs):
        self.game_frames.append(game_frame)

        self.collected_frame_count += 1

        serpent.utilities.clear_terminal()
        print(f"Collected Frame #{self.collected_frame_count}")

        time.sleep(kwargs.get("interval") or self.config.get("collect_frames_interval") or 1)

    def handle_collect_frame_regions(self, game_frame, **kwargs):
        region = kwargs.get("region")

        self.game_frames.append(game_frame)

        self.collected_frame_count += 1

        serpent.utilities.clear_terminal()
        print(f"Collected Frame #{self.collected_frame_count} for Region: {region}")

        time.sleep(kwargs.get("interval") or self.config.get("collect_frames_interval") or 1)

    def handle_collect_frames_for_context(self, game_frame, **kwargs):
        context = kwargs.get("context") or config["frame_handlers"]["COLLECT_FRAMES_FOR_CONTEXT"]["context"]
        interval = kwargs.get("interval") or config["frame_handlers"]["COLLECT_FRAMES_FOR_CONTEXT"]["interval"]

        screen_region = kwargs.get("screen_region")

        if screen_region is not None:
            if screen_region not in self.game.screen_regions:
                raise GameAgentError("Invalid game screen region...")

            frame_region = serpent.cv.extract_region_from_image(
                game_frame.frame,
                self.game.screen_regions[screen_region]
            )

            game_frame = GameFrame(frame_region)

        self.game_frames.append(game_frame)

        self.collected_frame_count += 1

        serpent.utilities.clear_terminal()
        print(f"Collected Frame #{self.collected_frame_count} for Context: {context}")

        time.sleep(interval)

    def handle_record(self, game_frame, **kwargs):
        keyboard_events = self.input_controller.capture_keys(duration=1 / self.config["fps"])
        # TODO: mouse capture (no segfault plz)

        game_frame_buffer = FrameGrabber.get_frames(
            [0, 4, 8, 12],
            frame_shape=(self.game.frame_height, self.game.frame_width),
            frame_type="PIPELINE",
            dtype="float64"
        )

        frame_uuid = str(uuid.uuid4())

        self.frame_keys[frame_uuid] = list() 
        self.frame_keyboard_events[frame_uuid] = list() 

        if len(keyboard_events):
            for keyboard_event in keyboard_events:
                key_name = keyboard_module_scan_code_mapping.get(keyboard_event.scan_code)

                if keyboard_event.event_type == "down":
                    if key_name.name not in self.keyboard_events:
                        self.frame_keys[frame_uuid].append(key_name)
                        
                        self.keyboard_events[key_name.name] = [
                            frame_uuid,
                            game_frame_buffer.frames,
                            keyboard_event.time
                        ]
                elif keyboard_event.event_type == "up":
                    if key_name.name in self.keyboard_events:
                        duration = keyboard_event.time - self.keyboard_events[key_name.name][2]
                        keypress_data = (key_name, str(duration))

                        print(f"{key_name.name} was pressed for {round(duration, 4)} seconds")

                        frame_uuid = self.keyboard_events[key_name.name][0]

                        self.frame_keyboard_events[frame_uuid].append(keypress_data)
                        
                        if len(self.frame_keys[frame_uuid]) == len(self.frame_keyboard_events[frame_uuid]):
                            self.frame_input_pairs.append((self.keyboard_events[key_name.name][1], self.frame_keyboard_events[frame_uuid]))

                        del self.keyboard_events[key_name.name]
        else:
            self.frame_input_pairs.append((game_frame_buffer.frames, []))

            del self.frame_keys[frame_uuid]
            del self.frame_keyboard_events[frame_uuid]

    def on_collect_frames_pause(self, **kwargs):
        for i, game_frame in enumerate(self.game_frames):
            print(f"Saving image {i + 1}/{len(self.game_frames)} to disk...")
            skimage.io.imsave(f"datasets/collect_frames/frame_{str(uuid.uuid4())}.png", game_frame.frame)

        self.game_frames = list()

    def on_collect_frame_regions_pause(self, **kwargs):
        region = kwargs["region"]
        region_path = f"datasets/collect_frames/{region}"

        for i, game_frame in enumerate(self.game_frames):
            frame_region = serpent.cv.extract_region_from_image(game_frame.frame, self.game.screen_regions.get(region))

            if not os.path.isdir(region_path):
                os.mkdir(region_path)

            print(f"Saving image {i + 1}/{len(self.game_frames)} to disk...")
            skimage.io.imsave(f"{region_path}/region_{str(uuid.uuid4())}.png", frame_region)

        self.game_frames = list()

    def on_collect_frames_for_context_pause(self, **kwargs):
        context = kwargs.get("context") or config["frame_handlers"]["COLLECT_FRAMES_FOR_CONTEXT"]["context"]

        for i, game_frame in enumerate(self.game_frames):
            file_name = f"datasets/collect_frames_for_context/{context}/frame_{str(uuid.uuid4())}.png"

            print(f"Saving image {i + 1}/{len(self.game_frames)} to disk...")
            skimage.io.imsave(file_name, game_frame.frame)

        self.game_frames = list()

    def on_record_pause(self, **kwargs):
        print(f"Writing Frame/Input Data to 'datasets/frame_input.h5'... (0/{len(self.frame_input_pairs)})")

        compute_reward = "reward_function" in self.config and self.config["reward_function"] in self.reward_functions
        reward_func = None

        if compute_reward:
            reward_func = self.reward_functions[self.config["reward_function"]]

        with h5py.File("datasets/frame_input.h5", "a") as f:
            for i, frames_inputs in enumerate(self.frame_input_pairs):
                serpent.utilities.clear_terminal()
                print(f"Writing Frame/Input Data to 'datasets/frame_input.h5'... ({i + 1}/{len(self.frame_input_pairs)})")
                frames, inputs = frames_inputs

                dataset_uuid = str(uuid.uuid4())

                reward_score = 0

                if compute_reward:
                    reward_score = reward_func(frames, inputs)

                png_frames = list()

                for frame in frames:
                    pil_image = Image.fromarray(skimage.util.img_as_ubyte(frame.frame))
                    pil_image = pil_image.convert("RGB")

                    png_frame = io.BytesIO()

                    pil_image.save(png_frame, format="PNG")
                    png_frame.seek(0)

                    png_frames.append(png_frame.read())

                del frames

                f.create_dataset(
                    f"{dataset_uuid}-frames",
                    data=png_frames
                )

                f.create_dataset(
                    f"{dataset_uuid}-inputs",
                    data=[(keyboard_key.name.encode("utf-8"), duration.encode("utf-8")) for keyboard_key, duration in inputs]
                )

                f.create_dataset(
                    f"{dataset_uuid}-reward",
                    data=reward_score
                )

            self.frame_input_pairs = list()
            self.keyboard_event_times = dict()

            time.sleep(10)


    def reward_test(self, frames, inputs, **kwargs):
        return random.choice(range(0, 10))


    def _setup_frame_handler(self, frame_handler=None, **kwargs):
        frame_handler = frame_handler or self.config.get("frame_handler", "NOOP")

        if frame_handler in self.frame_handler_setups:
            self.frame_handler_setups[frame_handler](**kwargs)

        self.frame_handler_setup_performed = True

    def _register_sprites(self):
        for sprite_name, sprite in self.game.sprites.items():
            self.sprite_identifier.register(sprite)
