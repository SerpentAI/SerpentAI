import offshoot

from serpent.config import config

import time
import uuid
import pickle
import h5py
import random
import json

import subprocess
import signal
import shlex
import atexit

import os
import os.path

import serpent.cv

from serpent.utilities import clear_terminal

from serpent.frame_grabber import FrameGrabber
from serpent.input_recorder import InputRecorder

from serpent.game_frame import GameFrame
from serpent.game_frame_buffer import GameFrameBuffer

from serpent.sprite_identifier import SpriteIdentifier

from serpent.analytics_client import AnalyticsClient

from serpent.visual_debugger.visual_debugger import VisualDebugger

import skimage.io
import skimage.transform
import skimage.util

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

        self.analytics_client = AnalyticsClient(project_key=config["analytics"]["topic"])

        if config["analytics"]["broadcast"]:
            self.analytics_client.track(event_key="RESET_DASHBOARD", data={})

        self.flag = None

        self.uuid = str(uuid.uuid4())
        self.started_at = datetime.now()

        self.kwargs = kwargs

    @offshoot.forbidden
    def on_game_frame(self, game_frame, game_frame_pipeline, frame_handler=None, **kwargs):
        if not self.frame_handler_setup_performed:
            self._setup_frame_handler(frame_handler=frame_handler, **kwargs)
            return None

        frame_handler = self.frame_handlers.get(frame_handler or self.config.get("frame_handler", "NOOP"))

        frame_handler(game_frame, game_frame_pipeline, **kwargs)

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
    def update_game_frame(self, frame_type="FULL"):
        game_frame_buffer = FrameGrabber.get_frames([0], frame_type=frame_type)
        return game_frame_buffer.frames[0]

    def handle_noop(self, game_frame, game_frame_pipeline, **kwargs):
        time.sleep(1)

    def setup_collect_frames(self, **kwargs):
        self.game_frames = list()
        self.game_frames_pipeline = list()

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
        self.game_frame_buffers = list()
        self.input_recorder_process = None

        self.frame_offsets = list(range(0, (self.kwargs["frame_count"] * self.kwargs["frame_spacing"]) - 1, self.kwargs["frame_spacing"]))

        self._start_input_recorder()

        clear_terminal()
        print("Start playing the game! Focus out when you are done or want to save the collected data to that point.")

    def handle_collect_frames(self, game_frame, game_frame_pipeline, **kwargs):
        self.game_frames.append(game_frame)
        self.game_frames_pipeline.append(game_frame_pipeline)

        self.collected_frame_count += 1

        clear_terminal()
        print(f"Collected Frame #{self.collected_frame_count}")

        time.sleep(kwargs.get("interval") or self.config.get("collect_frames_interval") or 1)

    def handle_collect_frame_regions(self, game_frame, game_frame_pipeline, **kwargs):
        region = kwargs.get("region")

        self.game_frames.append(game_frame)

        self.collected_frame_count += 1

        clear_terminal()
        print(f"Collected Frame #{self.collected_frame_count} for Region: {region}")

        time.sleep(kwargs.get("interval") or self.config.get("collect_frames_interval") or 1)

    def handle_collect_frames_for_context(self, game_frame, game_frame_pipeline, **kwargs):
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

        clear_terminal()
        print(f"Collected Frame #{self.collected_frame_count} for Context: {context}")

        time.sleep(interval)

    def handle_record(self, game_frame, game_frame_pipeline, **kwargs):
        game_frame_buffer = FrameGrabber.get_frames(
            self.frame_offsets,
            frame_type="PIPELINE"
        )

        self.game_frame_buffers.append(game_frame_buffer)

    def broadcast_previous_analytics_events(self):
        log_file_name = f"{config['analytics']['topic']}.json"

        if os.path.isfile(log_file_name):
            with open(log_file_name, "r") as f:
                for line in list(f):
                    try:
                        event = json.loads(line.strip())
                        self.analytics_client.track(event_key=event["event_key"], data=event["data"], timestamp=event["timestamp"])
                    except Exception:
                        continue

    def on_collect_frames_pause(self, **kwargs):
        for i, game_frame in enumerate(self.game_frames):
            print(f"Saving image {i + 1}/{len(self.game_frames)} to disk...")
            skimage.io.imsave(f"datasets/collect_frames/frame_{game_frame.timestamp}.png", game_frame.frame)

        if not os.path.exists("datasets/collect_frames/pipeline"):
            os.mkdir("datasets/collect_frames/pipeline")

        for i, game_frame in enumerate(self.game_frames_pipeline):
            print(f"Saving pipeline image {i + 1}/{len(self.game_frames)} to disk...")
            skimage.io.imsave(f"datasets/collect_frames/pipeline/frame_{game_frame.timestamp}.png", game_frame.frame)

        self.game_frames = list()
        self.game_frames_pipeline = list()

    def on_collect_frame_regions_pause(self, **kwargs):
        region = kwargs["region"]
        region_path = f"datasets/collect_frames/{region}"

        for i, game_frame in enumerate(self.game_frames):
            frame_region = serpent.cv.extract_region_from_image(game_frame.frame, self.game.screen_regions.get(region))

            if not os.path.isdir(region_path):
                os.mkdir(region_path)

            print(f"Saving image {i + 1}/{len(self.game_frames)} to disk...")
            skimage.io.imsave(f"{region_path}/region_{game_frame.timestamp}.png", frame_region)

        self.game_frames = list()

    def on_collect_frames_for_context_pause(self, **kwargs):
        context = kwargs.get("context") or config["frame_handlers"]["COLLECT_FRAMES_FOR_CONTEXT"]["context"]

        for i, game_frame in enumerate(self.game_frames):
            file_name = f"datasets/collect_frames_for_context/{context}/frame_{game_frame.timestamp}.png"

            print(f"Saving image {i + 1}/{len(self.game_frames)} to disk...")
            skimage.io.imsave(file_name, game_frame.frame)

        self.game_frames = list()

    def on_record_pause(self, **kwargs):
        InputRecorder.pause_input_recording()

        input_events = list()
        input_event_count = self.redis_client.llen(config["input_recorder"]["redis_key"])

        for i in range(input_event_count):
            input_events.append(pickle.loads(self.redis_client.lpop(config["input_recorder"]["redis_key"])))

        data = self._merge_frames_and_input_events(input_events)

        if not len(data):
            time.sleep(1)
            return None

        latest_game_frame_buffer = None

        active_keys = set()
        down_keys = dict()

        observations = dict()

        compute_reward = "reward_function" in self.config and self.config["reward_function"] in self.reward_functions
        reward_func = None 

        if compute_reward:
            reward_func = self.reward_functions[self.config["reward_function"]]

        for item in data:
            if isinstance(item, GameFrameBuffer):
                latest_game_frame_buffer = item

                reward_score = 0

                if compute_reward:
                    reward_score = reward_func(item.frames)
                
                timestamp = item.frames[-2].timestamp
                observations[timestamp] = [item, dict(), list(active_keys), list(), reward_score]
            elif item["type"] == "keyboard":
                key_name, key_event = item["name"].split("-")

                if key_event == "DOWN":
                    active_keys.add(key_name)

                    if latest_game_frame_buffer is not None:
                        timestamp = latest_game_frame_buffer.frames[-2].timestamp
                        observations[timestamp][1][key_name] = item["timestamp"]

                        down_keys[key_name] = timestamp

                elif key_event == "UP":
                    active_keys.remove(key_name)

                    if key_name in down_keys:
                        timestamp = down_keys[key_name]
                        
                        duration = item["timestamp"] - observations[timestamp][1][key_name]
                        observations[timestamp][1][key_name] = duration

                        del down_keys[key_name]
            elif item["type"] == "mouse":
                if latest_game_frame_buffer is not None:
                    timestamp = latest_game_frame_buffer.frames[-2].timestamp
                    observations[timestamp][3].append(item)

        print(f"Writing Recorded Input Data to 'datasets/input_recording.h5'... (0/{len(observations)})")

        with h5py.File("datasets/input_recording.h5", "a") as f:
            i = 0

            for timestamp, observation in observations.items():
                clear_terminal()
                print(f"Writing Recorded Input Data to 'datasets/input_recording.h5'... ({i + 1}/{len(observations)})")
                game_frame_buffer, keyboard_inputs, keyboard_inputs_active, mouse_inputs, reward_score = observation

                f.create_dataset(
                    f"{timestamp}-frames",
                    data=[game_frame.frame_bytes for game_frame in game_frame_buffer.frames]
                )

                f.create_dataset(
                    f"{timestamp}-keyboard-inputs",
                    data=[(key_name.encode("utf-8"), str(duration).encode("utf-8")) for key_name, duration in keyboard_inputs.items()]
                )

                f.create_dataset(
                    f"{timestamp}-keyboard-inputs-active",
                    data=[key_name.encode("utf-8") for key_name in keyboard_inputs_active]
                )

                filtered_mouse_inputs = list()
                mouse_move_index = None

                valid_game_window_x = range(
                    self.game.window_geometry["x_offset"],
                    self.game.window_geometry["x_offset"] + self.game.window_geometry["width"] + 1
                )

                valid_game_window_y = range(
                    self.game.window_geometry["y_offset"],
                    self.game.window_geometry["y_offset"] + self.game.window_geometry["height"] + 1
                )

                for mouse_input in mouse_inputs:
                    if mouse_input["x"] in valid_game_window_x and mouse_input["y"] in valid_game_window_y:
                        if mouse_input["name"] == "MOVE":
                            mouse_move_index = len(filtered_mouse_inputs)
                        
                        filtered_mouse_inputs.append(mouse_input)
                
                mouse_input_data = list()

                for i, mouse_input in enumerate(filtered_mouse_inputs):
                    if mouse_input["name"] == "MOVE" and i != mouse_move_index:
                        continue
                    
                    mouse_input_data.append((
                        mouse_input["name"].encode("utf-8"),
                        mouse_input["button"].encode("utf-8") if mouse_input["button"] else b"",
                        mouse_input["direction"].encode("utf-8") if mouse_input["direction"] else b"",
                        mouse_input["velocity"] or b"",
                        mouse_input["x"],
                        mouse_input["y"],
                        mouse_input["timestamp"]
                    ))

                f.create_dataset(
                    f"{timestamp}-mouse-inputs",
                    data=mouse_input_data
                )

                f.create_dataset(
                    f"{timestamp}-reward",
                    data=reward_score
                )

                i += 1

            self.game_frame_buffers = list()

            clear_terminal()
            print(f"Writing Frame/Input Data to 'datasets/input_recording.h5'... DONE")

        time.sleep(1)

    def reward_test(self, frames, **kwargs):
        return random.choice(range(0, 10))

    def _setup_frame_handler(self, frame_handler=None, **kwargs):
        frame_handler = frame_handler or self.config.get("frame_handler", "NOOP")

        if frame_handler in self.frame_handler_setups:
            self.frame_handler_setups[frame_handler](**kwargs)

        self.frame_handler_setup_performed = True

    def _register_sprites(self):
        for sprite_name, sprite in self.game.sprites.items():
            self.sprite_identifier.register(sprite)

    @offshoot.forbidden
    def _start_input_recorder(self):
        if self.input_recorder_process is not None:
            self._stop_input_recorder()

        input_recorder_command = "serpent record_inputs"

        self.input_recorder_process = subprocess.Popen(shlex.split(input_recorder_command))

        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

        atexit.register(self._handle_signal, 15, None, False)

    @offshoot.forbidden
    def _stop_input_recorder(self):
        if self.input_recorder_process is None:
            return None

        self.input_recorder_process.kill()
        self.input_recorder_process = None

        atexit.unregister(self._handle_signal)

    @offshoot.forbidden
    def _handle_signal(self, signum=15, frame=None, do_exit=True):
        if self.input_recorder_process is not None:
            if self.input_recorder_process.poll() is None:
                self.input_recorder_process.send_signal(signum)

                if do_exit:
                    exit()

    @offshoot.forbidden
    def _merge_frames_and_input_events(self, input_events):
        game_frame_buffer_index = 0
        input_event_index = 0

        merged = list()

        while True:
            game_frame_buffer = None
            input_event = None

            if game_frame_buffer_index > (len(self.game_frame_buffers) - 1) and input_event_index > (len(input_events) - 1):
                break
            else:
                if game_frame_buffer_index <= (len(self.game_frame_buffers) - 1):
                    game_frame_buffer = self.game_frame_buffers[game_frame_buffer_index]

                if input_event_index <= (len(input_events) - 1):
                    input_event = input_events[input_event_index]

            if game_frame_buffer is None:
                item = input_event
                input_event_index += 1
            elif input_event is None:
                item = game_frame_buffer
                game_frame_buffer_index += 1
            else:
                game_frame_buffer_timestamp = game_frame_buffer.frames[-2].timestamp
                input_event_timestamp = input_event["timestamp"]

                if game_frame_buffer_timestamp < input_event_timestamp:
                    item = game_frame_buffer
                    game_frame_buffer_index += 1
                else:
                    item = input_event
                    input_event_index += 1

            merged.append(item)

        return merged
