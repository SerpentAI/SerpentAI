from serpent.machine_learning.reinforcement_learning.agent import Agent

from serpent.game_frame_buffer import GameFrameBuffer
from serpent.input_recorder import InputRecorder

from serpent.utilities import SerpentError, clear_terminal

from serpent.enums import InputControlTypes

from serpent.config import config

import random
import time
import pickle

import signal
import atexit

import subprocess
import shlex

import h5py

from redis import StrictRedis


class RecorderAgent(Agent):

    def __init__(self, name, game_inputs=None, callbacks=None, window_geometry=None):
        super().__init__(name, game_inputs=game_inputs, callbacks=callbacks)

        if window_geometry is None or not isinstance(window_geometry, dict):
            raise SerpentError("RecorderAgent expects a 'window_geometry' dict kwarg.")

        self.window_geometry = window_geometry

        self.game_frame_buffers = list()
        self.rewards = list()

        self.current_step = 0

        self.redis_client = StrictRedis(**config["redis"])

        InputRecorder.pause_input_recording()

        input_recorder_command = "serpent record_inputs"
        self.input_recorder_process = subprocess.Popen(shlex.split(input_recorder_command))

        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

        atexit.register(self._handle_signal, 15, None, False)

    def generate_actions(self, state, **kwargs):
        if not isinstance(state, GameFrameBuffer):
            raise SerpentError("RecorderAgent 'generate_actions' state should be a GameFrameBuffer")

        self.game_frame_buffers.append(state)
        self.current_state = state

        actions = list()

        for game_inputs_item in self.game_inputs:
            if game_inputs_item["control_type"] == InputControlTypes.DISCRETE:
                label = random.choice(list(game_inputs_item["inputs"].keys()))
                action = list()

                actions.append((label, action, None))
            elif game_inputs_item["control_type"] == InputControlTypes.CONTINUOUS:
                label = game_inputs_item["name"]
                action = list()

                size = 1

                if "size" in game_inputs_item["inputs"]:
                    size = game_inputs_item["inputs"]["size"]

                if size == 1:
                    input_value = random.uniform(
                        game_inputs_item["inputs"]["minimum"],
                        game_inputs_item["inputs"]["maximum"]
                    )
                else:
                    input_value = list()

                    for i in range(size):
                        input_value.append(
                            random.uniform(
                                game_inputs_item["inputs"]["minimum"],
                                game_inputs_item["inputs"]["maximum"]
                            )
                        )

                actions.append((label, action, input_value))

        return actions

    def observe(self, reward=0, terminal=False, **kwargs):
        if self.current_state is None:
            return None

        self.current_step += 1
        print(self.current_step)

        self.rewards.append((reward, terminal))

        if terminal:
            InputRecorder.pause_input_recording()

            input_events = list()
            input_event_count = self.redis_client.llen(config["input_recorder"]["redis_key"])

            for i in range(input_event_count):
                input_events.append(pickle.loads(self.redis_client.lpop(config["input_recorder"]["redis_key"])))

            data = self._merge_frames_and_input_events(input_events)

            latest_game_frame_buffer = None
            rewards_index = 0

            active_keys = set()
            down_keys = dict()

            observations = dict()

            for item in data:
                if isinstance(item, GameFrameBuffer):
                    latest_game_frame_buffer = item

                    reward, terminal = self.rewards[rewards_index]
                    rewards_index += 1

                    timestamp = item.frames[-2].timestamp
                    observations[timestamp] = [item, dict(), list(active_keys), list(), reward, terminal]
                elif item["type"] == "keyboard":
                    key_name, key_event = item["name"].split("-")

                    if key_event == "DOWN":
                        active_keys.add(key_name)

                        if latest_game_frame_buffer is not None:
                            timestamp = latest_game_frame_buffer.frames[-2].timestamp
                            observations[timestamp][1][key_name] = item["timestamp"]

                            down_keys[key_name] = timestamp

                    elif key_event == "UP":
                        if key_name in active_keys:
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

            with h5py.File(f"datasets/{self.name}_input_recording.h5", "a") as f:
                i = 0

                for timestamp, observation in observations.items():
                    game_frame_buffer, keyboard_inputs, keyboard_inputs_active, mouse_inputs, reward, terminal = observation

                    f.create_dataset(
                        f"{timestamp}-frames",
                        data=[game_frame.to_png_bytes() for game_frame in game_frame_buffer.frames]
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
                        self.window_geometry["x_offset"],
                        self.window_geometry["x_offset"] + self.window_geometry["width"] + 1
                    )

                    valid_game_window_y = range(
                        self.window_geometry["y_offset"],
                        self.window_geometry["y_offset"] + self.window_geometry["height"] + 1
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
                        data=reward
                    )

                    f.create_dataset(
                        f"{timestamp}-terminal",
                        data=terminal
                    )

                    i += 1

                self.game_frame_buffers = list()
                self.rewards = list()
        else:
            InputRecorder.resume_input_recording()

        super().observe(reward=reward, terminal=terminal, **kwargs)

    def _merge_frames_and_input_events(self, input_events):
        has_game_frame_buffer = False

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

            if isinstance(item, GameFrameBuffer):
                merged.append(item)
                has_game_frame_buffer = True
            else:
                if has_game_frame_buffer:
                    merged.append(item)

        self.rewards = self.rewards[1:]

        return merged[1:]

    def _handle_signal(self, signum=15, frame=None, do_exit=True):
        if self.input_recorder_process is not None:
            if self.input_recorder_process.poll() is None:
                self.input_recorder_process.send_signal(signum)

                if do_exit:
                    exit()
