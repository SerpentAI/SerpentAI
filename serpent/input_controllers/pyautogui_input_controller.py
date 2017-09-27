from serpent.input_controller import InputController, MouseButton

from serpent.sprite_locator import SpriteLocator

import serpent.ocr

import pyautogui

import time


class PyAutoGUIInputController(InputController):

    def __init__(self, game=None, **kwargs):
        self.game = game

        self.mouse_buttons = {
            MouseButton.LEFT.name: "left",
            MouseButton.MIDDLE.name: "middle",
            MouseButton.RIGHT.name: "right"
        }

        self.previous_key_collection_set = set()

        self.sprite_locator = SpriteLocator()

    # Keyboard Actions
    def handle_keys(self, key_collection, **kwargs):
        key_collection_set = set(key_collection)

        keys_to_press = key_collection_set - self.previous_key_collection_set
        keys_to_release = self.previous_key_collection_set - key_collection_set

        for key in keys_to_press:
            self.press_key(key)

        for key in keys_to_release:
            self.release_key(key)

        self.previous_key_collection_set = key_collection_set

    def tap_keys(self, keys, duration=0.05, **kwargs):
        if self.game_is_focused:
            for key in keys:
                pyautogui.keyDown(key)

            time.sleep(duration)

            for key in keys:
                pyautogui.keyUp(key)

    def tap_key(self, key, duration=0.05, **kwargs):
        if self.game_is_focused:
            pyautogui.keyDown(key)

            time.sleep(duration)

            pyautogui.keyUp(key)

    def press_keys(self, keys, **kwargs):
        for key in keys:
            self.press_key(key)

    def press_key(self, key, **kwargs):
        if self.game_is_focused:
            pyautogui.keyDown(key)

    def release_keys(self, **kwargs):
        for key in self.previous_key_collection_set:
            self.release_key(key)

        self.previous_key_collection_set = set()

    def release_key(self, key, **kwargs):
        if self.game_is_focused:
            pyautogui.keyUp(key)

    def type_string(self, string, duration=0.05, **kwargs):
        if self.game_is_focused:
            pyautogui.typewrite(message=string, interval=duration)

    # Mouse Actions
    def click(self, button=MouseButton.LEFT, y=None, x=None, duration=0.25, **kwargs):
        if self.game_is_focused:
            x += self.game.window_geometry["x_offset"]
            y += self.game.window_geometry["y_offset"]

            pyautogui.moveTo(x, y, duration=duration)
            pyautogui.click(button=self.mouse_buttons.get(button.name, "left"))

    def click_screen_region(self, button=MouseButton.LEFT, screen_region=None, **kwargs):
        if self.game_is_focused:
            screen_region_coordinates = self.game.screen_regions.get(screen_region)

            x = (screen_region_coordinates[1] + screen_region_coordinates[3]) // 2
            y = (screen_region_coordinates[0] + screen_region_coordinates[2]) // 2

            self.click(button=button, y=y, x=x)

    def click_sprite(self, button=MouseButton.LEFT, sprite=None, game_frame=None, **kwargs):
        if self.game_is_focused:
            sprite_location = self.sprite_locator.locate(sprite=sprite, game_frame=game_frame)

            if sprite_location is None:
                return False

            x = (sprite_location[1] + sprite_location[3]) // 2
            y = (sprite_location[0] + sprite_location[2]) // 2

            self.click(button=button, y=y, x=x)

            return True

    def click_string(self, query_string, button=MouseButton.LEFT, game_frame=None, fuzziness=2, ocr_preset=None, **kwargs):
        if self.game_is_focused:
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
                y = (string_location[0] + string_location[2]) // 2

                self.click(button=button, y=y, x=x)

                return True

            return False

    def drag(self, button=MouseButton.LEFT, x0=None, y0=None, x1=None, y1=None, duration=1, **kwargs):
        if self.game_is_focused:
            x0 += self.game.window_geometry["x_offset"]
            x1 += self.game.window_geometry["x_offset"]
            y0 += self.game.window_geometry["y_offset"]
            y1 += self.game.window_geometry["y_offset"]

            pyautogui.moveTo(x0, y0, duration=0.2)
            pyautogui.dragTo(x1, y1, button=button, duration=duration)

    def drag_screen_region_to_screen_region(self, button=MouseButton.LEFT, start_screen_region=None, end_screen_region=None, duration=1, **kwargs):
        if self.game_is_focused:
            start_screen_region_coordinates = self._extract_screen_region_coordinates(start_screen_region)
            end_screen_region_coordinates = self._extract_screen_region_coordinates(end_screen_region)

            self.drag(
                button=button,
                x0=start_screen_region_coordinates[0],
                y0=start_screen_region_coordinates[1],
                x1=end_screen_region_coordinates[0],
                y1=end_screen_region_coordinates[1],
                duration=duration
            )

    def scroll(self, y=None, x=None, clicks=1, direction="DOWN", **kwargs):
        if self.game_is_focused:
            clicks = clicks * (1 if direction == "DOWN" else -1)

            x += self.game.window_geometry["x_offset"]
            y += self.game.window_geometry["y_offset"]

            pyautogui.scroll(clicks, x=x, y=y)
