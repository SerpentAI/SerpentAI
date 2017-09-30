from serpent.input_controller import InputController, MouseButton, KeyboardKey, character_keyboard_key_mapping

from serpent.sprite_locator import SpriteLocator

import serpent.ocr

import time

import pyautogui
import ctypes


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
    KeyboardKey.KEY_INSERT.name: 0xD2,
    KeyboardKey.KEY_HOME.name: 0xC7,
    KeyboardKey.KEY_PAGE_UP.name: 0xC9,
    KeyboardKey.KEY_NUMLOCK.name: 0x45,
    KeyboardKey.KEY_NUMPAD_DIVIDE.name: 0xB5,
    KeyboardKey.KEY_NUMPAD_SLASH.name: 0xB5,
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
    KeyboardKey.KEY_DELETE.name: 0xD3,
    KeyboardKey.KEY_END.name: 0xCF,
    KeyboardKey.KEY_PAGE_DOWN.name: 0xD1,
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
    KeyboardKey.KEY_UP.name: 0xC8,
    KeyboardKey.KEY_NUMPAD_1.name: 0x4F,
    KeyboardKey.KEY_NUMPAD_2.name: 0x50,
    KeyboardKey.KEY_NUMPAD_3.name: 0x51,
    KeyboardKey.KEY_NUMPAD_RETURN.name: 0x9C,
    KeyboardKey.KEY_NUMPAD_ENTER.name: 0x9C,
    KeyboardKey.KEY_LEFT_CTRL.name: 0x1D,
    KeyboardKey.KEY_LEFT_SUPER.name: 0xDB,
    KeyboardKey.KEY_LEFT_WINDOWS.name: 0xDB,
    KeyboardKey.KEY_LEFT_ALT.name: 0x38,
    KeyboardKey.KEY_SPACE.name: 0x39,
    KeyboardKey.KEY_RIGHT_ALT.name: 0xB8,
    KeyboardKey.KEY_RIGHT_SUPER.name: 0xDC,
    KeyboardKey.KEY_RIGHT_WINDOWS.name: 0xDC,
    KeyboardKey.KEY_APP_MENU.name: 0xDD,
    KeyboardKey.KEY_RIGHT_CTRL.name: 0x9D,
    KeyboardKey.KEY_LEFT.name: 0xCB,
    KeyboardKey.KEY_DOWN.name: 0xD0,
    KeyboardKey.KEY_RIGHT.name: 0xCD,
    KeyboardKey.KEY_NUMPAD_0.name: 0x52,
    KeyboardKey.KEY_NUMPAD_DECIMAL.name: 0x53,
    KeyboardKey.KEY_NUMPAD_PERIOD.name: 0x53
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
            self.press_key(key)

        for key in keys_to_release:
            self.release_key(key)

        self.previous_key_collection_set = key_collection_set

    def tap_keys(self, keys, duration=0.05, **kwargs):
        if self.game_is_focused:
            for key in keys:
                self.press_key(key)

            time.sleep(duration)

            for key in keys:
                self.release_key(key)

    def tap_key(self, key, duration=0.05, **kwargs):
        if self.game_is_focused:
            self.press_key(key)

            time.sleep(duration)

            self.release_key(key)

    def press_keys(self, keys, **kwargs):
        for key in keys:
            self.press_key(key)

    def press_key(self, key, **kwargs):
        if self.game_is_focused:
            extra = ctypes.c_ulong(0)
            ii_ = Input_I()
            ii_.ki = KeyBdInput(0, keyboard_key_mapping[key.name], 0x0008, 0, ctypes.pointer(extra))
            x = Input(ctypes.c_ulong(1), ii_)
            ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    def release_keys(self, keys, **kwargs):
        for key in keys:
            self.release_key(key)

    def release_key(self, key, **kwargs):
        if self.game_is_focused:
            extra = ctypes.c_ulong(0)
            ii_ = Input_I()
            ii_.ki = KeyBdInput(0, keyboard_key_mapping[key.name], 0x0008 | 0x0002, 0, ctypes.pointer(extra))
            x = Input(ctypes.c_ulong(1), ii_)
            ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    def type_string(self, string, duration=0.05, **kwargs):
        if self.game_is_focused:
            for character in string:
                keys = character_keyboard_key_mapping.get(character)

                if keys is not None:
                    self.tap_keys(keys, duration=duration)

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
