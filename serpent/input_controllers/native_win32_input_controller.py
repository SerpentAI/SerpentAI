from serpent.input_controller import InputController, MouseButton, KeyboardKey, character_keyboard_key_mapping

from serpent.sprite_locator import SpriteLocator

import serpent.ocr

import time

import ctypes
import win32api

import scipy.interpolate
import numpy as np


# Adding 1024 to extended keys to be able to detect the need to use a flag later on
keyboard_key_mapping = {
    KeyboardKey.KEY_ESCAPE.name: 0x01,
    KeyboardKey.KEY_F1.name: 0x3B,
    KeyboardKey.KEY_F2.name: 0x3C,
    KeyboardKey.KEY_F3.name: 0x3D,
    KeyboardKey.KEY_F4.name: 0x3E,
    KeyboardKey.KEY_F5.name: 0x3F,
    KeyboardKey.KEY_F6.name: 0x40,
    KeyboardKey.KEY_F7.name: 0x41,
    KeyboardKey.KEY_F8.name: 0x42,
    KeyboardKey.KEY_F9.name: 0x43,
    KeyboardKey.KEY_F10.name: 0x44,
    KeyboardKey.KEY_F11.name: 0x57,
    KeyboardKey.KEY_F12.name: 0x58,
    KeyboardKey.KEY_PRINT_SCREEN.name: 0xB7,
    KeyboardKey.KEY_SCROLL_LOCK.name: 0x46,
    KeyboardKey.KEY_PAUSE.name: 0xC5,
    KeyboardKey.KEY_GRAVE.name: 0x29,
    KeyboardKey.KEY_BACKTICK.name: 0x29,
    KeyboardKey.KEY_1.name: 0x02,
    KeyboardKey.KEY_2.name: 0x03,
    KeyboardKey.KEY_3.name: 0x04,
    KeyboardKey.KEY_4.name: 0x05,
    KeyboardKey.KEY_5.name: 0x06,
    KeyboardKey.KEY_6.name: 0x07,
    KeyboardKey.KEY_7.name: 0x08,
    KeyboardKey.KEY_8.name: 0x09,
    KeyboardKey.KEY_9.name: 0x0A,
    KeyboardKey.KEY_0.name: 0x0B,
    KeyboardKey.KEY_MINUS.name: 0x0C,
    KeyboardKey.KEY_DASH.name: 0x0C,
    KeyboardKey.KEY_EQUALS.name: 0x0D,
    KeyboardKey.KEY_BACKSPACE.name: 0x0E,
    KeyboardKey.KEY_INSERT.name: 0xD2 + 1024,
    KeyboardKey.KEY_HOME.name: 0xC7 + 1024,
    KeyboardKey.KEY_PAGE_UP.name: 0xC9 + 1024,
    KeyboardKey.KEY_NUMLOCK.name: 0x45,
    KeyboardKey.KEY_NUMPAD_DIVIDE.name: 0xB5 + 1024,
    KeyboardKey.KEY_NUMPAD_SLASH.name: 0xB5 + 1024,
    KeyboardKey.KEY_NUMPAD_MULTIPLY.name: 0x37,
    KeyboardKey.KEY_NUMPAD_STAR.name: 0x37,
    KeyboardKey.KEY_NUMPAD_SUBTRACT.name: 0x4A,
    KeyboardKey.KEY_NUMPAD_DASH.name: 0x4A,
    KeyboardKey.KEY_TAB.name: 0x0F,
    KeyboardKey.KEY_Q.name: 0x10,
    KeyboardKey.KEY_W.name: 0x11,
    KeyboardKey.KEY_E.name: 0x12,
    KeyboardKey.KEY_R.name: 0x13,
    KeyboardKey.KEY_T.name: 0x14,
    KeyboardKey.KEY_Y.name: 0x15,
    KeyboardKey.KEY_U.name: 0x16,
    KeyboardKey.KEY_I.name: 0x17,
    KeyboardKey.KEY_O.name: 0x18,
    KeyboardKey.KEY_P.name: 0x19,
    KeyboardKey.KEY_LEFT_BRACKET.name: 0x1A,
    KeyboardKey.KEY_RIGHT_BRACKET.name: 0x1B,
    KeyboardKey.KEY_BACKSLASH.name: 0x2B,
    KeyboardKey.KEY_DELETE.name: 0xD3 + 1024,
    KeyboardKey.KEY_END.name: 0xCF + 1024,
    KeyboardKey.KEY_PAGE_DOWN.name: 0xD1 + 1024,
    KeyboardKey.KEY_NUMPAD_7.name: 0x47,
    KeyboardKey.KEY_NUMPAD_8.name: 0x48,
    KeyboardKey.KEY_NUMPAD_9.name: 0x49,
    KeyboardKey.KEY_NUMPAD_ADD.name: 0x4E,
    KeyboardKey.KEY_NUMPAD_PLUS.name: 0x4E,
    KeyboardKey.KEY_CAPSLOCK.name: 0x3A,
    KeyboardKey.KEY_A.name: 0x1E,
    KeyboardKey.KEY_S.name: 0x1F,
    KeyboardKey.KEY_D.name: 0x20,
    KeyboardKey.KEY_F.name: 0x21,
    KeyboardKey.KEY_G.name: 0x22,
    KeyboardKey.KEY_H.name: 0x23,
    KeyboardKey.KEY_J.name: 0x24,
    KeyboardKey.KEY_K.name: 0x25,
    KeyboardKey.KEY_L.name: 0x26,
    KeyboardKey.KEY_SEMICOLON.name: 0x27,
    KeyboardKey.KEY_APOSTROPHE.name: 0x28,
    KeyboardKey.KEY_RETURN.name: 0x1C,
    KeyboardKey.KEY_ENTER.name: 0x1C,
    KeyboardKey.KEY_NUMPAD_4.name: 0x4B,
    KeyboardKey.KEY_NUMPAD_5.name: 0x4C,
    KeyboardKey.KEY_NUMPAD_6.name: 0x4D,
    KeyboardKey.KEY_LEFT_SHIFT.name: 0x2A,
    KeyboardKey.KEY_Z.name: 0x2C,
    KeyboardKey.KEY_X.name: 0x2D,
    KeyboardKey.KEY_C.name: 0x2E,
    KeyboardKey.KEY_V.name: 0x2F,
    KeyboardKey.KEY_B.name: 0x30,
    KeyboardKey.KEY_N.name: 0x31,
    KeyboardKey.KEY_M.name: 0x32,
    KeyboardKey.KEY_COMMA.name: 0x33,
    KeyboardKey.KEY_PERIOD.name: 0x34,
    KeyboardKey.KEY_SLASH.name: 0x35,
    KeyboardKey.KEY_RIGHT_SHIFT.name: 0x36,
    KeyboardKey.KEY_UP.name: 0xC8 + 1024,
    KeyboardKey.KEY_NUMPAD_1.name: 0x4F,
    KeyboardKey.KEY_NUMPAD_2.name: 0x50,
    KeyboardKey.KEY_NUMPAD_3.name: 0x51,
    KeyboardKey.KEY_NUMPAD_RETURN.name: 0x9C + 1024,
    KeyboardKey.KEY_NUMPAD_ENTER.name: 0x9C + 1024,
    KeyboardKey.KEY_LEFT_CTRL.name: 0x1D,
    KeyboardKey.KEY_LEFT_SUPER.name: 0xDB + 1024,
    KeyboardKey.KEY_LEFT_WINDOWS.name: 0xDB + 1024,
    KeyboardKey.KEY_LEFT_ALT.name: 0x38,
    KeyboardKey.KEY_SPACE.name: 0x39,
    KeyboardKey.KEY_RIGHT_ALT.name: 0xB8 + 1024,
    KeyboardKey.KEY_RIGHT_SUPER.name: 0xDC + 1024,
    KeyboardKey.KEY_RIGHT_WINDOWS.name: 0xDC + 1024,
    KeyboardKey.KEY_APP_MENU.name: 0xDD + 1024,
    KeyboardKey.KEY_RIGHT_CTRL.name: 0x9D + 1024,
    KeyboardKey.KEY_LEFT.name: 0xCB + 1024,
    KeyboardKey.KEY_DOWN.name: 0xD0 + 1024,
    KeyboardKey.KEY_RIGHT.name: 0xCD + 1024,
    KeyboardKey.KEY_NUMPAD_0.name: 0x52,
    KeyboardKey.KEY_NUMPAD_DECIMAL.name: 0x53,
    KeyboardKey.KEY_NUMPAD_PERIOD.name: 0x53
}

mouse_button_down_mapping = {
    MouseButton.LEFT.name: 0x0002,
    MouseButton.MIDDLE.name: 0x0020,
    MouseButton.RIGHT.name: 0x0008
}

mouse_button_up_mapping = {
    MouseButton.LEFT.name: 0x0004,
    MouseButton.MIDDLE.name: 0x0040,
    MouseButton.RIGHT.name: 0x0010
}

PUL = ctypes.POINTER(ctypes.c_ulong)


class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]


class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]


class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]


class NativeWin32InputController(InputController):

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
            extra = ctypes.c_ulong(0)
            ii_ = Input_I()

            if keyboard_key_mapping[key.name] >= 1024:
                key = keyboard_key_mapping[key.name] - 1024
                flags = 0x0008 | 0x0001
            else:
                key = keyboard_key_mapping[key.name]
                flags = 0x0008

            ii_.ki = KeyBdInput(0, key, flags, 0, ctypes.pointer(extra))
            x = Input(ctypes.c_ulong(1), ii_)
            ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    def release_keys(self, keys, **kwargs):
        for key in keys:
            self.release_key(key, **kwargs)

    def release_key(self, key, **kwargs):
        if ("force" in kwargs and kwargs["force"] is True) or self.game_is_focused:
            extra = ctypes.c_ulong(0)
            ii_ = Input_I()

            if keyboard_key_mapping[key.name] >= 1024:
                key = keyboard_key_mapping[key.name] - 1024
                flags = 0x0008 | 0x0001 | 0x0002
            else:
                key = keyboard_key_mapping[key.name]
                flags = 0x0008 | 0x0002

            ii_.ki = KeyBdInput(0, key, flags, 0, ctypes.pointer(extra))
            x = Input(ctypes.c_ulong(1), ii_)
            ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    def type_string(self, string, duration=0.05, **kwargs):
        if ("force" in kwargs and kwargs["force"] is True) or self.game_is_focused:
            for character in string:
                keys = character_keyboard_key_mapping.get(character)

                if keys is not None:
                    self.tap_keys(keys, duration=duration, **kwargs)

    # Mouse Actions
    def move(self, x=None, y=None, duration=0.25, absolute=True, **kwargs):
        if ("force" in kwargs and kwargs["force"] is True) or self.game_is_focused:
            x += self.game.window_geometry["x_offset"]
            y += self.game.window_geometry["y_offset"]

            current_pixel_coordinates = win32api.GetCursorPos()
            start_coordinates = self._to_windows_coordinates(*current_pixel_coordinates)

            if absolute:
                end_coordinates = self._to_windows_coordinates(x, y)
            else:
                end_coordinates = self._to_windows_coordinates(current_pixel_coordinates[0] + x, current_pixel_coordinates[1] + y)

            coordinates = self._interpolate_mouse_movement(
                start_windows_coordinates=start_coordinates,
                end_windows_coordinates=end_coordinates
            )

            for x, y in coordinates:
                extra = ctypes.c_ulong(0)
                ii_ = Input_I()
                ii_.mi = MouseInput(x, y, 0, (0x0001 | 0x8000), 0, ctypes.pointer(extra))
                x = Input(ctypes.c_ulong(0), ii_)
                ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

                time.sleep(duration / 20)

    def click_down(self, button=MouseButton.LEFT, **kwargs):
        if ("force" in kwargs and kwargs["force"] is True) or self.game_is_focused:
            extra = ctypes.c_ulong(0)
            ii_ = Input_I()
            ii_.mi = MouseInput(0, 0, 0, mouse_button_down_mapping[button.name], 0, ctypes.pointer(extra))
            x = Input(ctypes.c_ulong(0), ii_)
            ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    def click_up(self, button=MouseButton.LEFT, **kwargs):
        if ("force" in kwargs and kwargs["force"] is True) or self.game_is_focused:
            extra = ctypes.c_ulong(0)
            ii_ = Input_I()
            ii_.mi = MouseInput(0, 0, 0, mouse_button_up_mapping[button.name], 0, ctypes.pointer(extra))
            x = Input(ctypes.c_ulong(0), ii_)
            ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    def click(self, button=MouseButton.LEFT, duration=0.05, **kwargs):
        if ("force" in kwargs and kwargs["force"] is True) or self.game_is_focused:
            self.click_down(button=button, **kwargs)
            time.sleep(duration)
            self.click_up(button=button, **kwargs)

    def click_screen_region(self, button=MouseButton.LEFT, screen_region=None, **kwargs):
        if ("force" in kwargs and kwargs["force"] is True) or self.game_is_focused:
            screen_region_coordinates = self.game.screen_regions.get(screen_region)

            x = (screen_region_coordinates[1] + screen_region_coordinates[3]) // 2
            y = (screen_region_coordinates[0] + screen_region_coordinates[2]) // 2

            self.move(x, y)
            self.click(button=button, **kwargs)

    def click_sprite(self, button=MouseButton.LEFT, sprite=None, game_frame=None, **kwargs):
        if ("force" in kwargs and kwargs["force"] is True) or self.game_is_focused:
            sprite_location = self.sprite_locator.locate(sprite=sprite, game_frame=game_frame)

            if sprite_location is None:
                return False

            x = (sprite_location[1] + sprite_location[3]) // 2
            y = (sprite_location[0] + sprite_location[2]) // 2

            self.move(x, y)
            self.click(button=button, **kwargs)

            return True

    def click_string(self, query_string, button=MouseButton.LEFT, game_frame=None, fuzziness=2, ocr_preset=None, **kwargs):
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

                self.move(x, y)
                self.click(button=button, **kwargs)

                return True

            return False

    def drag(self, button=MouseButton.LEFT, x0=None, y0=None, x1=None, y1=None, duration=0.25, **kwargs):
        if ("force" in kwargs and kwargs["force"] is True) or self.game_is_focused:
            self.move(x=x0, y=y0)
            self.click_down(button=button)
            self.move(x=x1, y=y1, duration=duration)
            self.click_up(button=button)

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
            clicks = clicks * (1 if direction == "UP" else -1) * 120

            extra = ctypes.c_ulong(0)
            ii_ = Input_I()
            ii_.mi = MouseInput(0, 0, clicks, 0x0800, 0, ctypes.pointer(extra))
            x = Input(ctypes.c_ulong(0), ii_)
            ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    @staticmethod
    def _to_windows_coordinates(x=0, y=0):
        display_width = win32api.GetSystemMetrics(0)
        display_height = win32api.GetSystemMetrics(1)

        windows_x = (x * 65535) // display_width
        windows_y = (y * 65535) // display_height

        return windows_x, windows_y

    @staticmethod
    def _interpolate_mouse_movement(start_windows_coordinates, end_windows_coordinates, steps=20):
        x_coordinates = [start_windows_coordinates[0], end_windows_coordinates[0]]
        y_coordinates = [start_windows_coordinates[1], end_windows_coordinates[1]]

        if x_coordinates[0] == x_coordinates[1]:
            x_coordinates[1] += 1

        if y_coordinates[0] == y_coordinates[1]:
            y_coordinates[1] += 1

        interpolation_func = scipy.interpolate.interp1d(x_coordinates, y_coordinates)

        intermediate_x_coordinates = np.linspace(start_windows_coordinates[0], end_windows_coordinates[0], steps + 1)[1:]
        coordinates = list(map(lambda x: (int(round(x)), int(interpolation_func(x))), intermediate_x_coordinates))

        return coordinates
