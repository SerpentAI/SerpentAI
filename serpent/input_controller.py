import enum

from serpent.utilities import is_linux, is_macos, is_windows

from sneakysnek.keyboard_keys import KeyboardKey
from sneakysnek.keyboard_event import KeyboardEvent as SneakySnekKeyboardEvent

from sneakysnek.mouse_buttons import MouseButton
from sneakysnek.mouse_event import MouseEvent as SneakySnekMouseEvent


# US layout - What's to be done for other keyboard layouts?
character_keyboard_key_mapping = {
    "`": [KeyboardKey.KEY_GRAVE],
    "~": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_GRAVE],
    "1": [KeyboardKey.KEY_1],
    "!": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_1],
    "2": [KeyboardKey.KEY_2],
    "@": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_2],
    "3": [KeyboardKey.KEY_3],
    "#": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_3],
    "4": [KeyboardKey.KEY_4],
    "$": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_4],
    "5": [KeyboardKey.KEY_5],
    "%": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_5],
    "6": [KeyboardKey.KEY_6],
    "^": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_6],
    "7": [KeyboardKey.KEY_7],
    "&": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_7],
    "8": [KeyboardKey.KEY_8],
    "*": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_8],
    "9": [KeyboardKey.KEY_9],
    "(": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_9],
    "0": [KeyboardKey.KEY_0],
    ")": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_0],
    "-": [KeyboardKey.KEY_MINUS],
    "_": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_MINUS],
    "=": [KeyboardKey.KEY_EQUALS],
    "+": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_EQUALS],
    "q": [KeyboardKey.KEY_Q],
    "Q": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_Q],
    "w": [KeyboardKey.KEY_W],
    "W": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_W],
    "e": [KeyboardKey.KEY_E],
    "E": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_E],
    "r": [KeyboardKey.KEY_R],
    "R": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_R],
    "t": [KeyboardKey.KEY_T],
    "T": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_T],
    "y": [KeyboardKey.KEY_Y],
    "Y": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_Y],
    "u": [KeyboardKey.KEY_U],
    "U": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_U],
    "i": [KeyboardKey.KEY_I],
    "I": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_I],
    "o": [KeyboardKey.KEY_O],
    "O": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_O],
    "p": [KeyboardKey.KEY_P],
    "P": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_P],
    "[": [KeyboardKey.KEY_LEFT_BRACKET],
    "{": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_LEFT_BRACKET],
    "]": [KeyboardKey.KEY_RIGHT_BRACKET],
    "}": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_RIGHT_BRACKET],
    "\n": [KeyboardKey.KEY_RETURN],
    "a": [KeyboardKey.KEY_A],
    "A": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_A],
    "s": [KeyboardKey.KEY_S],
    "S": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_S],
    "d": [KeyboardKey.KEY_D],
    "D": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_D],
    "f": [KeyboardKey.KEY_F],
    "F": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_F],
    "g": [KeyboardKey.KEY_G],
    "G": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_G],
    "h": [KeyboardKey.KEY_H],
    "H": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_H],
    "j": [KeyboardKey.KEY_J],
    "J": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_J],
    "k": [KeyboardKey.KEY_K],
    "K": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_K],
    "l": [KeyboardKey.KEY_L],
    "L": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_L],
    ";": [KeyboardKey.KEY_SEMICOLON],
    ":": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_SEMICOLON],
    "'": [KeyboardKey.KEY_APOSTROPHE],
    '"': [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_APOSTROPHE],
    "z": [KeyboardKey.KEY_Z],
    "Z": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_Z],
    "x": [KeyboardKey.KEY_X],
    "X": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_X],
    "c": [KeyboardKey.KEY_C],
    "C": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_C],
    "v": [KeyboardKey.KEY_V],
    "V": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_V],
    "b": [KeyboardKey.KEY_B],
    "B": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_B],
    "n": [KeyboardKey.KEY_N],
    "N": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_N],
    "m": [KeyboardKey.KEY_M],
    "M": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_M],
    ",": [KeyboardKey.KEY_COMMA],
    "<": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_COMMA],
    ".": [KeyboardKey.KEY_PERIOD],
    ">": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_PERIOD],
    "/": [KeyboardKey.KEY_SLASH],
    "?": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_SLASH],
    "\\": [KeyboardKey.KEY_BACKSLASH],
    "|": [KeyboardKey.KEY_LEFT_SHIFT, KeyboardKey.KEY_BACKSLASH],
    " ": [KeyboardKey.KEY_SPACE]
}


class InputControllers(enum.Enum):
    PYAUTOGUI = 0
    NATIVE_WIN32 = 1


class InputControllerError(BaseException):
    pass


class InputController:

    def __init__(self, backend=InputControllers.PYAUTOGUI, game=None, **kwargs):
        self.game = game
        self.backend = self._initialize_backend(backend, **kwargs)

    @property
    def game_is_focused(self):
        return self.game.is_focused

    # Keyboard Actions
    def handle_keys(self, key_collection, **kwargs):
        self._is_game_launched_check()
        self.backend.handle_keys(key_collection, **kwargs)

    def tap_keys(self, keys, duration=0.05, **kwargs):
        self._is_game_launched_check()
        self.backend.tap_keys(keys, duration=duration, **kwargs)

    def tap_key(self, key, duration=0.05, **kwargs):
        self._is_game_launched_check()
        self.backend.tap_key(key, duration=duration, **kwargs)

    def press_keys(self, keys, **kwargs):
        self._is_game_launched_check()
        self.backend.press_keys(keys, **kwargs)

    def press_key(self, key, **kwargs):
        self._is_game_launched_check()
        self.backend.press_key(key, **kwargs)

    def release_keys(self, keys, **kwargs):
        self._is_game_launched_check()
        self.backend.release_keys(keys, **kwargs)

    def release_key(self, key, **kwargs):
        self._is_game_launched_check()
        self.backend.release_key(key, **kwargs)

    def type_string(self, string, duration=0.05, **kwargs):
        self._is_game_launched_check()
        self.backend.type_string(string, duration=duration, **kwargs)

    # Mouse Actions
    def move(self, x=None, y=None, duration=0.25, absolute=True, **kwargs):
        self._is_game_launched_check()
        self.backend.move(x=x, y=y, duration=duration, absolute=absolute, **kwargs)

    def click_down(self, button=MouseButton.LEFT, **kwargs):
        self._is_game_launched_check()
        self.backend.click_down(button=button, **kwargs)

    def click_up(self, button=MouseButton.LEFT, **kwargs):
        self._is_game_launched_check()
        self.backend.click_up(button=button, **kwargs)

    def click(self, button=MouseButton.LEFT, duration=0.25, **kwargs):
        self._is_game_launched_check()
        self.backend.click(button=button, duration=duration, **kwargs)

    def click_screen_region(self, button=MouseButton.LEFT, screen_region=None, **kwargs):
        self._is_game_launched_check()
        self.backend.click_screen_region(button=button, screen_region=screen_region, **kwargs)

    def click_sprite(self, button=MouseButton.LEFT, sprite=None, game_frame=None, **kwargs):
        self._is_game_launched_check()
        self.backend.click_sprite(button=button, sprite=sprite, game_frame=game_frame, **kwargs)

    # Requires the Serpent OCR module
    def click_string(self, query_string, button=MouseButton.LEFT, game_frame=None, fuzziness=2, ocr_preset=None, **kwargs):
        self._is_game_launched_check()
        self.backend.click_string(query_string, button=button, game_frame=game_frame, fuzziness=fuzziness, ocr_preset=ocr_preset, **kwargs)

    def drag(self, button=MouseButton.LEFT, x0=None, y0=None, x1=None, y1=None, duration=1, **kwargs):
        self._is_game_launched_check()
        self.backend.drag(button=button, x0=x0, y0=y0, x1=x1, y1=y1, duration=duration, **kwargs)

    def drag_screen_region_to_screen_region(self, button=MouseButton.LEFT, start_screen_region=None, end_screen_region=None, duration=1, **kwargs):
        self._is_game_launched_check()
        self.backend.drag_screen_region_to_screen_region(button=button, start_screen_region=start_screen_region, end_screen_region=end_screen_region, duration=duration, **kwargs)

    def scroll(self, clicks=1, direction="DOWN", **kwargs):
        self._is_game_launched_check()
        self.backend.scroll(clicks=clicks, direction=direction, **kwargs)

    def ratios_to_coordinates(self, ratios, screen_region=None):
        window_offset_x = self.game.window_geometry["x_offset"]
        window_offset_y = self.game.window_geometry["y_offset"]

        if screen_region is None:
            width = self.game.window_geometry["width"]
            height = self.game.window_geometry["height"]

            y0, x0, y1, x1 = (0, 0, height, width)
        else:
            y0, x0, y1, x1 = self.game.screen_regions[screen_region]

            width = x1 - x0
            height = y1 - y0

        return (
            window_offset_x + x0 + (ratios[0] * width),
            window_offset_y + y0 + (ratios[1] * height)
        )

    def _initialize_backend(self, backend, **kwargs):
        if backend == InputControllers.PYAUTOGUI:
            from serpent.input_controllers.pyautogui_input_controller import PyAutoGUIInputController
            return PyAutoGUIInputController(game=self.game, **kwargs)
        elif backend == InputControllers.NATIVE_WIN32:
            from serpent.input_controllers.native_win32_input_controller import NativeWin32InputController
            return NativeWin32InputController(game=self.game, **kwargs)
        else:
            raise InputControllerError("The specified backend is invalid!")

    def _is_game_launched_check(self):
        if not self.game.is_launched:
            raise InputControllerError("InputController cannot be used while the game is not running!")

    def _extract_screen_region_coordinates(self, screen_region):
        screen_region_coordinates = self.game.screen_regions.get(screen_region)

        x = (screen_region_coordinates[1] + screen_region_coordinates[3]) // 2
        x += self.game.window_geometry["x_offset"]

        y = (screen_region_coordinates[0] + screen_region_coordinates[2]) // 2
        y += self.game.window_geometry["y_offset"]

        return x, y


class KeyboardEvents(enum.Enum):
    DOWN = "DOWN"
    UP = "UP"


class KeyboardEvent(SneakySnekKeyboardEvent):

    def __init__(self, event, keyboard_key, **kwargs):
        super().__init__(event, keyboard_key)
        self.kwargs = kwargs

    @property
    def as_label(self):
        pass

    @property
    def as_input(self):
        pass


class MouseEvents(enum.Enum):
    CLICK = "CLICK"
    CLICK_DOWN = "CLICK_DOWN"
    CLICK_UP = "CLICK_UP"
    CLICK_SCREEN_REGION = "CLICK_SCREEN_REGION"
    DRAG_START = "DRAG_START"
    DRAG_END = "DRAG_END"
    MOVE = "MOVE"
    MOVE_RELATIVE = "MOVE_RELATIVE"
    SCROLL = "SCROLL"


class MouseEvent(SneakySnekMouseEvent):

    def __init__(self, event, button=None, direction=None, velocity=None, x=None, y=None, **kwargs):
        super().__init__(event, button=button, direction=direction, velocity=velocity, x=x, y=y)
        self.kwargs = kwargs

    @property
    def as_label(self):
        if self.event == MouseEvents.CLICK and self.button == MouseButton.LEFT:
            return "Mouse - Left Click"
        elif self.event == MouseEvents.CLICK and self.button == MouseButton.RIGHT:
            return "Mouse - Right Click"
        elif self.event == MouseEvents.CLICK and self.button == MouseButton.MIDDLE:
            return "Mouse - Middle Click"
        elif self.event == MouseEvents.CLICK_DOWN and self.button == MouseButton.LEFT:
            return "Mouse - Left Click - Pressed"
        elif self.event == MouseEvents.CLICK_DOWN and self.button == MouseButton.RIGHT:
            return "Mouse - Right Click - Pressed"
        elif self.event == MouseEvents.CLICK_DOWN and self.button == MouseButton.MIDDLE:
            return "Mouse - Middle Click - Pressed"
        elif self.event == MouseEvents.CLICK_UP and self.button == MouseButton.LEFT:
            return "Mouse - Left Click - Released"
        elif self.event == MouseEvents.CLICK_UP and self.button == MouseButton.RIGHT:
            return "Mouse - Right Click - Released"
        elif self.event == MouseEvents.CLICK_UP and self.button == MouseButton.MIDDLE:
            return "Mouse - Middle Click - Released"
        elif self.event == MouseEvents.CLICK_SCREEN_REGION and self.button == MouseButton.LEFT:
            return f"Mouse - Left Region Click - {self.kwargs['screen_region']}"
        elif self.event == MouseEvents.CLICK_SCREEN_REGION and self.button == MouseButton.RIGHT:
            return f"Mouse - Right Region Click - {self.kwargs['screen_region']}"
        elif self.event == MouseEvents.CLICK_SCREEN_REGION and self.button == MouseButton.MIDDLE:
            return f"Mouse - Middle Region Click - {self.kwargs['screen_region']}"
        elif self.event == MouseEvents.DRAG_START and self.button == MouseButton.LEFT:
            return f"Mouse - Left Drag Start - ({self.x}, {self.y})"
        elif self.event == MouseEvents.DRAG_START and self.button == MouseButton.RIGHT:
            return f"Mouse - Right Drag Start - ({self.x}, {self.y})"
        elif self.event == MouseEvents.DRAG_START and self.button == MouseButton.MIDDLE:
            return f"Mouse - Middle Drag Start - ({self.x}, {self.y})"
        elif self.event == MouseEvents.DRAG_END and self.button == MouseButton.LEFT:
            return f"Mouse - Left Drag End - ({self.x}, {self.y})"
        elif self.event == MouseEvents.DRAG_END and self.button == MouseButton.RIGHT:
            return f"Mouse - Right Drag End - ({self.x}, {self.y})"
        elif self.event == MouseEvents.DRAG_END and self.button == MouseButton.MIDDLE:
            return f"Mouse - Middle Drag End - ({self.x}, {self.y})"
        elif self.event == MouseEvents.MOVE:
            return f"Mouse - Move - ({self.x}, {self.y})"
        elif self.event == MouseEvents.MOVE_RELATIVE:
            return f"Mouse - Move (Relative) - ({self.x}, {self.y})"
        elif self.event == MouseEvents.SCROLL and self.direction == "UP":
            return "Mouse - Scroll Up"
        elif self.event == MouseEvents.SCROLL and self.direction == "DOWN":
            return "Mouse - Scroll Down"
        else:
            return "Mouse - Unknown"

    @property
    def as_input(self):
        if self.event == MouseEvents.CLICK and self.button == MouseButton.LEFT:
            return "MOUSE_LEFT_CLICK"
        elif self.event == MouseEvents.CLICK and self.button == MouseButton.RIGHT:
            return "MOUSE_RIGHT_CLICK"
        elif self.event == MouseEvents.CLICK and self.button == MouseButton.MIDDLE:
            return "MOUSE_MIDDLE_CLICK"
        elif self.event == MouseEvents.CLICK_DOWN and self.button == MouseButton.LEFT:
            return "MOUSE_LEFT_DOWN"
        elif self.event == MouseEvents.CLICK_DOWN and self.button == MouseButton.RIGHT:
            return "MOUSE_RIGHT_DOWN"
        elif self.event == MouseEvents.CLICK_DOWN and self.button == MouseButton.MIDDLE:
            return "MOUSE_MIDDLE_DOWN"
        elif self.event == MouseEvents.CLICK_UP and self.button == MouseButton.LEFT:
            return "MOUSE_LEFT_UP"
        elif self.event == MouseEvents.CLICK_UP and self.button == MouseButton.RIGHT:
            return "MOUSE_RIGHT_UP"
        elif self.event == MouseEvents.CLICK_UP and self.button == MouseButton.MIDDLE:
            return "MOUSE_MIDDLE_UP"
        elif self.event == MouseEvents.CLICK_SCREEN_REGION and self.button == MouseButton.LEFT:
            return "MOUSE_LEFT_REGION_CLICK"
        elif self.event == MouseEvents.CLICK_SCREEN_REGION and self.button == MouseButton.RIGHT:
            return "MOUSE_RIGHT_REGION_CLICK"
        elif self.event == MouseEvents.CLICK_SCREEN_REGION and self.button == MouseButton.MIDDLE:
            return "MOUSE_MIDDLE_REGION_CLICK"
        elif self.event == MouseEvents.DRAG_START and self.button == MouseButton.LEFT:
            return "MOUSE_LEFT_DRAG_START"
        elif self.event == MouseEvents.DRAG_START and self.button == MouseButton.RIGHT:
            return "MOUSE_RIGHT_DRAG_START"
        elif self.event == MouseEvents.DRAG_START and self.button == MouseButton.MIDDLE:
            return "MOUSE_MIDDLE_DRAG_START"
        elif self.event == MouseEvents.DRAG_END and self.button == MouseButton.LEFT:
            return "MOUSE_LEFT_DRAG_END"
        elif self.event == MouseEvents.DRAG_END and self.button == MouseButton.RIGHT:
            return "MOUSE_RIGHT_DRAG_END"
        elif self.event == MouseEvents.DRAG_END and self.button == MouseButton.MIDDLE:
            return "MOUSE_MIDDLE_DRAG_END"
        elif self.event == MouseEvents.MOVE:
            return "MOUSE_MOVE"
        elif self.event == MouseEvents.MOVE_RELATIVE:
            return "MOUSE_MOVE_RELATIVE"
        elif self.event == MouseEvents.SCROLL and self.direction == "UP":
            return "MOUSE_SCROLL_UP"
        elif self.event == MouseEvents.SCROLL and self.direction == "DOWN":
            return "MOUSE_SCROLL_DOWN"
        else:
            return "MOUSE_UNKNOWN"
