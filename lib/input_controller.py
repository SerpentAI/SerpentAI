from pymouse import PyMouse
from pykeyboard import PyKeyboard

import pyautogui

import time

import subprocess
import shlex


class InputController:

    def __init__(self, game_window_id=None):
        self.game_window_id = game_window_id

        self.keyboard = PyKeyboard()

        self.mouse = PyMouse()
        self.mouse_buttons = {
            "LEFT": "left",
            "MIDDLE": "middle",
            "RIGHT": "right"
        }

        self.previous_key_collection_set = set()

    @property
    def game_is_focused(self):
        focused_window_id = subprocess.check_output(shlex.split("xdotool getwindowfocus")).decode("utf-8").strip()
        return focused_window_id == self.game_window_id

    # Keyboard Actions

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

        self.previous_key_collection_set = set()

    def release_key(self, key):
        if self.game_is_focused:
            self.keyboard.release_key(key)

    def type_string(self, string, duration=0.05):
        if self.game_is_focused:
            for character in string:
                self.tap_key(character, duration=duration)

    # Mouse Actions
    def click(self, button="LEFT", y=None, x=None):
        pyautogui.moveTo(x, y)
        pyautogui.click(button=self.mouse_buttons.get(button, "left"))

    def click_screen_region(self, button="LEFT", screen_region=None, game=None):
        screen_region_coordinates = game.screen_regions.get(screen_region)

        x = (screen_region_coordinates[1] + screen_region_coordinates[3]) // 2
        x += game.window_geometry["x_offset"]

        y = (screen_region_coordinates[0] + screen_region_coordinates[2]) // 2
        y += game.window_geometry["y_offset"]

        self.click(button=button, y=y, x=x)

    def drag(self, button="LEFT", x0=None, y0=None, x1=None, y1=None):
        pass

    def drag_screen_region_to_screen_region(self, start_screen_region=None, end_screen_region=None, duration=1, offset=(0, 0), game=None):
        start_screen_region_coordinates = self._extract_screen_region_coordinates(start_screen_region, game=game)
        end_screen_region_coordinates = self._extract_screen_region_coordinates(end_screen_region, game=game)

        pyautogui.moveTo(*start_screen_region_coordinates)

        coordinates = (end_screen_region_coordinates[0] + offset[0], end_screen_region_coordinates[1] + offset[1])
        pyautogui.dragTo(*coordinates, duration=duration)

    def _extract_screen_region_coordinates(self, screen_region, game=None):
        screen_region_coordinates = game.screen_regions.get(screen_region)

        x = (screen_region_coordinates[1] + screen_region_coordinates[3]) // 2
        x += game.window_geometry["x_offset"]

        y = (screen_region_coordinates[0] + screen_region_coordinates[2]) // 2
        y += game.window_geometry["y_offset"]

        return x, y

    @staticmethod
    def human_readable_key_mapping():
        return {
            111: "UP",
            114: "RIGHT",
            116: "DOWN",
            113: "LEFT"
        }
