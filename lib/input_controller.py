from pymouse import PyMouse
from pykeyboard import PyKeyboard

import time

import subprocess
import shlex


class InputController:

    def __init__(self, game_window_id=None):
        self.game_window_id = game_window_id

        self.keyboard = PyKeyboard()
        self.mouse = PyMouse()

        self.previous_key_collection_set = set()

    @property
    def game_is_focused(self):
        focused_window_id = subprocess.check_output(shlex.split("xdotool getwindowfocus")).decode("utf-8").strip()
        return focused_window_id == self.game_window_id

    def handle_keys(self, key_collection):
        key_collection_set = set(key_collection)

        keys_to_press = key_collection_set - self.previous_key_collection_set
        keys_to_release = self.previous_key_collection_set - key_collection_set

        for key in keys_to_press:
            self.press_key(key)

        for key in keys_to_release:
            self.release_key(key)

        self.previous_key_collection_set = key_collection_set

    def tap_keys(self, keys, duration=0.05):
        if self.game_is_focused:
            for key in keys:
                self.keyboard.press_key(key)

            time.sleep(duration)

            for key in keys:
                self.keyboard.release_key(key)

    def tap_key(self, key, duration=0.05):
        if self.game_is_focused:
            self.keyboard.press_key(key)

            time.sleep(duration)

            self.keyboard.release_key(key)

    def press_keys(self, keys):
        for key in keys:
            self.press_key(key)

    def press_key(self, key):
        if self.game_is_focused:
            self.keyboard.press_key(key)

    def release_keys(self):
        for key in self.previous_key_collection_set:
            self.release_key(key)

    def release_key(self, key):
        if self.game_is_focused:
            self.keyboard.release_key(key)

    def type_string(self, string, duration=0.05):
        if self.game_is_focused:
            for character in string:
                self.tap_key(character, duration=duration)

    @staticmethod
    def human_readable_key_mapping():
        return {
            111: "UP",
            114: "RIGHT",
            116: "DOWN",
            113: "LEFT"
        }
