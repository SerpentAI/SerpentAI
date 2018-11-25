from serpent.input_controller import InputController, MouseButton, KeyboardKey

from serpent.sprite_locator import SpriteLocator

import pyautogui

import time


keyboard_key_mapping = {
    KeyboardKey.KEY_ESCAPE.name: "esc",
    KeyboardKey.KEY_F1.name: "f1",
    KeyboardKey.KEY_F2.name: "f2",
    KeyboardKey.KEY_F3.name: "f3",
    KeyboardKey.KEY_F4.name: "f4",
    KeyboardKey.KEY_F5.name: "f5",
    KeyboardKey.KEY_F6.name: "f6",
    KeyboardKey.KEY_F7.name: "f7",
    KeyboardKey.KEY_F8.name: "f8",
    KeyboardKey.KEY_F9.name: "f9",
    KeyboardKey.KEY_F10.name: "f10",
    KeyboardKey.KEY_F11.name: "f11",
    KeyboardKey.KEY_F12.name: "f12",
    KeyboardKey.KEY_PRINT_SCREEN.name: "printscreen",
    KeyboardKey.KEY_SCROLL_LOCK.name: "scrolllock",
    KeyboardKey.KEY_PAUSE.name: "pause",
    KeyboardKey.KEY_GRAVE.name: "`",
    KeyboardKey.KEY_BACKTICK.name: "`",
    KeyboardKey.KEY_1.name: "1",
    KeyboardKey.KEY_2.name: "2",
    KeyboardKey.KEY_3.name: "3",
    KeyboardKey.KEY_4.name: "4",
    KeyboardKey.KEY_5.name: "5",
    KeyboardKey.KEY_6.name: "6",
    KeyboardKey.KEY_7.name: "7",
    KeyboardKey.KEY_8.name: "8",
    KeyboardKey.KEY_9.name: "9",
    KeyboardKey.KEY_0.name: "0",
    KeyboardKey.KEY_MINUS.name: "-",
    KeyboardKey.KEY_DASH.name: "-",
    KeyboardKey.KEY_EQUALS.name: "=",
    KeyboardKey.KEY_BACKSPACE.name: "backspace",
    KeyboardKey.KEY_INSERT.name: "insert",
    KeyboardKey.KEY_HOME.name: "home",
    KeyboardKey.KEY_PAGE_UP.name: "pageup",
    KeyboardKey.KEY_NUMLOCK.name: "numlock",
    KeyboardKey.KEY_NUMPAD_DIVIDE.name: "divide",
    KeyboardKey.KEY_NUMPAD_SLASH.name: "divide",
    KeyboardKey.KEY_NUMPAD_MULTIPLY.name: "multiply",
    KeyboardKey.KEY_NUMPAD_STAR.name: "multiply",
    KeyboardKey.KEY_NUMPAD_SUBTRACT.name: "subtract",
    KeyboardKey.KEY_NUMPAD_DASH.name: "subtract",
    KeyboardKey.KEY_TAB.name: "tab",
    KeyboardKey.KEY_Q.name: "q",
    KeyboardKey.KEY_W.name: "w",
    KeyboardKey.KEY_E.name: "e",
    KeyboardKey.KEY_R.name: "r",
    KeyboardKey.KEY_T.name: "t",
    KeyboardKey.KEY_Y.name: "y",
    KeyboardKey.KEY_U.name: "u",
    KeyboardKey.KEY_I.name: "i",
    KeyboardKey.KEY_O.name: "o",
    KeyboardKey.KEY_P.name: "p",
    KeyboardKey.KEY_LEFT_BRACKET.name: "[",
    KeyboardKey.KEY_RIGHT_BRACKET.name: "]",
    KeyboardKey.KEY_BACKSLASH.name: "\\",
    KeyboardKey.KEY_DELETE.name: "delete",
    KeyboardKey.KEY_END.name: "end",
    KeyboardKey.KEY_PAGE_DOWN.name: "pagedown",
    KeyboardKey.KEY_NUMPAD_7.name: "num7",
    KeyboardKey.KEY_NUMPAD_8.name: "num8",
    KeyboardKey.KEY_NUMPAD_9.name: "num9",
    KeyboardKey.KEY_NUMPAD_ADD.name: "add",
    KeyboardKey.KEY_NUMPAD_PLUS.name: "add",
    KeyboardKey.KEY_CAPSLOCK.name: "capslock",
    KeyboardKey.KEY_A.name: "a",
    KeyboardKey.KEY_S.name: "s",
    KeyboardKey.KEY_D.name: "d",
    KeyboardKey.KEY_F.name: "f",
    KeyboardKey.KEY_G.name: "g",
    KeyboardKey.KEY_H.name: "h",
    KeyboardKey.KEY_J.name: "j",
    KeyboardKey.KEY_K.name: "k",
    KeyboardKey.KEY_L.name: "l",
    KeyboardKey.KEY_SEMICOLON.name: ';',
    KeyboardKey.KEY_APOSTROPHE.name: "'",
    KeyboardKey.KEY_RETURN.name: "enter",
    KeyboardKey.KEY_ENTER.name: "enter",
    KeyboardKey.KEY_NUMPAD_4.name: "num4",
    KeyboardKey.KEY_NUMPAD_5.name: "num5",
    KeyboardKey.KEY_NUMPAD_6.name: "num6",
    KeyboardKey.KEY_LEFT_SHIFT.name: "shiftleft",
    KeyboardKey.KEY_Z.name: "z",
    KeyboardKey.KEY_X.name: "x",
    KeyboardKey.KEY_C.name: "c",
    KeyboardKey.KEY_V.name: "v",
    KeyboardKey.KEY_B.name: "b",
    KeyboardKey.KEY_N.name: "n",
    KeyboardKey.KEY_M.name: "m",
    KeyboardKey.KEY_COMMA.name: ",",
    KeyboardKey.KEY_PERIOD.name: ".",
    KeyboardKey.KEY_SLASH.name: "/",
    KeyboardKey.KEY_RIGHT_SHIFT.name: "shiftright",
    KeyboardKey.KEY_UP.name: "up",
    KeyboardKey.KEY_NUMPAD_1.name: "num1",
    KeyboardKey.KEY_NUMPAD_2.name: "num2",
    KeyboardKey.KEY_NUMPAD_3.name: "num3",
    KeyboardKey.KEY_NUMPAD_RETURN.name: "separator",
    KeyboardKey.KEY_NUMPAD_ENTER.name: "separator",
    KeyboardKey.KEY_LEFT_CTRL.name: "ctrlleft",
    KeyboardKey.KEY_LEFT_SUPER.name: "winleft",
    KeyboardKey.KEY_LEFT_WINDOWS.name: "winleft",
    KeyboardKey.KEY_LEFT_ALT.name: "altleft",
    KeyboardKey.KEY_SPACE.name: "space",
    KeyboardKey.KEY_RIGHT_ALT.name: "altright",
    KeyboardKey.KEY_RIGHT_SUPER.name: "winright",
    KeyboardKey.KEY_RIGHT_WINDOWS.name: "winright",
    KeyboardKey.KEY_APP_MENU.name: "apps",
    KeyboardKey.KEY_RIGHT_CTRL.name: "ctrlright",
    KeyboardKey.KEY_LEFT.name: "left",
    KeyboardKey.KEY_DOWN.name: "down",
    KeyboardKey.KEY_RIGHT.name: "right",
    KeyboardKey.KEY_NUMPAD_0.name: "num0",
    KeyboardKey.KEY_NUMPAD_DECIMAL.name: "decimal",
    KeyboardKey.KEY_NUMPAD_PERIOD.name: "decimal",
    KeyboardKey.KEY_COMMAND.name: "command",
}

mouse_button_mapping = {
    MouseButton.LEFT.name: "left",
    MouseButton.MIDDLE.name: "middle",
    MouseButton.RIGHT.name: "right",
}


class PyAutoGUIInputController(InputController):

    def __init__(self, game=None, **kwargs):
        self.game = game

        self.previous_key_collection_set = set()

        self.sprite_locator = SpriteLocator()

    # Keyboard Actions
    def handle_keys(self, key_collection, **kwargs):
        key_collection_set = set(key_collection)

        keys_to_press = key_collection_set - self.previous_key_collection_set
        keys_to_release = self.previous_key_collection_set - key_collection_set

        for key in keys_to_press:
            self.press_key(key, **kwargs)

        for key in keys_to_release:
            self.release_key(key, **kwargs)

        self.previous_key_collection_set = key_collection_set

    def tap_keys(self, keys, duration=0.05, **kwargs):
        if ("force" in kwargs and kwargs["force"] is True) or self.game_is_focused:
            for key in keys:
                self.press_key(key, **kwargs)

            time.sleep(duration)

            for key in keys:
                self.release_key(key, **kwargs)

    def tap_key(self, key, duration=0.05, **kwargs):
        if ("force" in kwargs and kwargs["force"] is True) or self.game_is_focused:
            self.press_key(key, **kwargs)

            time.sleep(duration)

            self.release_key(key, **kwargs)

    def press_keys(self, keys, **kwargs):
        for key in keys:
            self.press_key(key, **kwargs)

    def press_key(self, key, **kwargs):
        if ("force" in kwargs and kwargs["force"] is True) or self.game_is_focused:
            pyautogui.keyDown(keyboard_key_mapping[key.name])

    def release_keys(self, keys, **kwargs):
        for key in keys:
            self.release_key(key, **kwargs)

    def release_key(self, key, **kwargs):
        if ("force" in kwargs and kwargs["force"] is True) or self.game_is_focused:
            pyautogui.keyUp(keyboard_key_mapping[key.name])

    def type_string(self, string, duration=0.05, **kwargs):
        if ("force" in kwargs and kwargs["force"] is True) or self.game_is_focused:
            pyautogui.typewrite(message=string, interval=duration)

    # Mouse Actions
    def move(self, x=None, y=None, duration=0.25, absolute=True, **kwargs):
        if ("force" in kwargs and kwargs["force"] is True) or self.game_is_focused:
            x += self.game.window_geometry["x_offset"]
            y += self.game.window_geometry["y_offset"]

            if absolute:
                pyautogui.moveTo(x=x, y=y, duration=duration)
            else:
                pyautogui.moveRel(xOffset=x, yOffset=y, duration=duration)

    def click_down(self, button=MouseButton.LEFT, **kwargs):
        if ("force" in kwargs and kwargs["force"] is True) or self.game_is_focused:
            pyautogui.mouseDown(button=mouse_button_mapping[button.name])

    def click_up(self, button=MouseButton.LEFT, **kwargs):
        if ("force" in kwargs and kwargs["force"] is True) or self.game_is_focused:
            pyautogui.mouseUp(button=mouse_button_mapping[button.name])

    def click(self, button=MouseButton.LEFT, duration=0.25, **kwargs):
        if ("force" in kwargs and kwargs["force"] is True) or self.game_is_focused:
            self.click_down(button=button, **kwargs)
            time.sleep(duration)
            self.click_up(button=button, **kwargs)

    def click_screen_region(self, button=MouseButton.LEFT, screen_region=None, **kwargs):
        if ("force" in kwargs and kwargs["force"] is True) or self.game_is_focused:
            screen_region_coordinates = self.game.screen_regions.get(screen_region)

            x = (screen_region_coordinates[1] + screen_region_coordinates[3]) // 2
            y = (screen_region_coordinates[0] + screen_region_coordinates[2]) // 2

            self.move(x=x, y=y)
            self.click(button=button, **kwargs)

    def click_sprite(self, button=MouseButton.LEFT, sprite=None, game_frame=None, **kwargs):
        if ("force" in kwargs and kwargs["force"] is True) or self.game_is_focused:
            sprite_location = self.sprite_locator.better_locate(sprite=sprite, game_frame=game_frame)

            if sprite_location is None:
                return False

            x = (sprite_location[1] + sprite_location[3]) // 2
            y = (sprite_location[0] + sprite_location[2]) // 2

            self.move(x=x, y=y)
            self.click(button=button, **kwargs)

            return True

    # Requires the Serpent OCR module
    def click_string(self, query_string, button=MouseButton.LEFT, game_frame=None, fuzziness=2, ocr_preset=None, **kwargs):
        import serpent.ocr

        if ("force" in kwargs and kwargs["force"] is True) or self.game_is_focused:
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

                self.move(x=x, y=y)
                self.click(button=button, **kwargs)

                return True

            return False

    def drag(self, button=MouseButton.LEFT, x0=None, y0=None, x1=None, y1=None, duration=0.25, **kwargs):
        if ("force" in kwargs and kwargs["force"] is True) or self.game_is_focused:
            self.move(x=x0, y=y0)
            self.click_down(button=button, **kwargs)
            self.move(x=x1, y=y1, duration=duration)
            self.click_up(button=button, **kwargs)

    def drag_screen_region_to_screen_region(self, button=MouseButton.LEFT, start_screen_region=None, end_screen_region=None, duration=1, **kwargs):
        if ("force" in kwargs and kwargs["force"] is True) or self.game_is_focused:
            start_screen_region_coordinates = self._extract_screen_region_coordinates(start_screen_region)
            end_screen_region_coordinates = self._extract_screen_region_coordinates(end_screen_region)

            self.drag(
                button=button,
                x0=start_screen_region_coordinates[0],
                y0=start_screen_region_coordinates[1],
                x1=end_screen_region_coordinates[0],
                y1=end_screen_region_coordinates[1],
                duration=duration,
                **kwargs
            )

    def scroll(self, clicks=1, direction="DOWN", **kwargs):
        if ("force" in kwargs and kwargs["force"] is True) or self.game_is_focused:
            clicks = clicks * (1 if direction == "DOWN" else -1)
            pyautogui.scroll(clicks)
