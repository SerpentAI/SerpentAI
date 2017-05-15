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

    @property
    def game_is_focused(self):
        focused_window_id = subprocess.check_output(shlex.split("xdotool getwindowfocus")).decode("utf-8").strip()
        return focused_window_id == self.game_window_id

    def tap_key(self, key, duration=0.05):
        if self.game_is_focused:
            self.keyboard.press_key(key)
            time.sleep(duration)
            self.keyboard.release_key(key)

    def press_key(self, key):
        if self.game_is_focused:
            self.keyboard.press_key(key)

    def release_key(self, key):
        if self.game_is_focused:
            self.keyboard.release_key(key)
