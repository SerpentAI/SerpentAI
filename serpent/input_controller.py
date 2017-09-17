from serpent.sprite_locator import SpriteLocator

import serpent.ocr

import pyautogui

import enum

import time


class MouseButton(enum.Enum):
    LEFT = 0
    MIDDLE = 1
    RIGHT = 2


class InputController:

    def __init__(self, game=None):
        self.game = game

        self.mouse_buttons = {
            MouseButton.LEFT.name: "left",
            MouseButton.MIDDLE.name: "middle",
            MouseButton.RIGHT.name: "right"
        }

        self.previous_key_collection_set = set()

        self.sprite_locator = SpriteLocator()

    @property
    def game_is_focused(self):
        return self.game.is_focused

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
                pyautogui.keyDown(key)

            time.sleep(duration)

            for key in keys:
                pyautogui.keyUp(key)

    def tap_key(self, key, duration=0.05):
        if self.game_is_focused:
            pyautogui.keyDown(key)

            time.sleep(duration)

            pyautogui.keyUp(key)

    def press_keys(self, keys):
        for key in keys:
            self.press_key(key)

    def press_key(self, key):
        if self.game_is_focused:
            pyautogui.keyDown(key)

    def release_keys(self):
        for key in self.previous_key_collection_set:
            self.release_key(key)

        self.previous_key_collection_set = set()

    def release_key(self, key):
        if self.game_is_focused:
            pyautogui.keyUp(key)

    def type_string(self, string, duration=0.05):
        if self.game_is_focused:
            pyautogui.typewrite(message=string, interval=duration)

    # Mouse Actions
    def click(self, button=MouseButton.LEFT, y=None, x=None, duration=0.25, **kwargs):
        pyautogui.moveTo(x, y, duration=duration)
        pyautogui.click(button=self.mouse_buttons.get(button.name, "left"))

    def click_screen_region(self, button=MouseButton.LEFT, screen_region=None, **kwargs):
        screen_region_coordinates = self.game.screen_regions.get(screen_region)

        x = (screen_region_coordinates[1] + screen_region_coordinates[3]) // 2
        x += self.game.window_geometry["x_offset"]

        y = (screen_region_coordinates[0] + screen_region_coordinates[2]) // 2
        y += self.game.window_geometry["y_offset"]

        self.click(button=button, y=y, x=x, **kwargs)

    def click_sprite(self, button=MouseButton.LEFT, sprite=None, game_frame=None, **kwargs):
        sprite_location = self.sprite_locator.locate(sprite=sprite, game_frame=game_frame)

        if sprite_location is None:
            return False

        x = (sprite_location[1] + sprite_location[3]) // 2
        x += self.game.window_geometry["x_offset"]

        y = (sprite_location[0] + sprite_location[2]) // 2
        y += self.game.window_geometry["y_offset"]

        self.click(button=button, y=y, x=x, **kwargs)

        return True

    def click_string(self, query_string, game_frame, button=MouseButton.LEFT, fuzziness=2, ocr_preset=None, **kwargs):
        string_location = serpent.ocr.locate_string(
            query_string,
            game_frame.frame,
            fuzziness=fuzziness,
            ocr_preset=ocr_preset,
            offset_x=game_frame.offset_x,
            offset_y=game_frame.offset_y
        )

        if string_location is not None:
            x = (string_location[1] + string_location[3]) // 2
            x += self.game.window_geometry["x_offset"]

            y = (string_location[0] + string_location[2]) // 2
            y += self.game.window_geometry["y_offset"]

            self.click(button=button, y=y, x=x, **kwargs)

            return True

        return False

    def drag(self, button=MouseButton.LEFT, x0=None, y0=None, x1=None, y1=None):
        pass

    def drag_screen_region_to_screen_region(self, start_screen_region=None, end_screen_region=None, duration=1, offset=(0, 0)):
        start_screen_region_coordinates = self._extract_screen_region_coordinates(start_screen_region)
        end_screen_region_coordinates = self._extract_screen_region_coordinates(end_screen_region)

        pyautogui.moveTo(*start_screen_region_coordinates)

        coordinates = (end_screen_region_coordinates[0] + offset[0], end_screen_region_coordinates[1] + offset[1])
        pyautogui.dragTo(*coordinates, duration=duration)

    def _extract_screen_region_coordinates(self, screen_region):
        screen_region_coordinates = self.game.screen_regions.get(screen_region)

        x = (screen_region_coordinates[1] + screen_region_coordinates[3]) // 2
        x += self.game.window_geometry["x_offset"]

        y = (screen_region_coordinates[0] + screen_region_coordinates[2]) // 2
        y += self.game.window_geometry["y_offset"]

        return x, y
