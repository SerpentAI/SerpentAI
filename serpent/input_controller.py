import enum


class MouseButton(enum.Enum):
    LEFT = 0
    MIDDLE = 1
    RIGHT = 2


class KeyboardKey(enum.Enum):
    W = 0
    A = 1
    S = 2
    D = 3
    ESC = 4,
    LSHIFT = 5

character_keyboard_key_mapping = {
    "a": [KeyboardKey.A],
    "d": [KeyboardKey.D],
    "s": [KeyboardKey.S],
    "w": [KeyboardKey.W],
    "A": [KeyboardKey.LSHIFT, KeyboardKey.A],
    "D": [KeyboardKey.LSHIFT, KeyboardKey.D],
    "S": [KeyboardKey.LSHIFT, KeyboardKey.S],
    "W": [KeyboardKey.LSHIFT, KeyboardKey.W],
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

    def release_keys(self, **kwargs):
        self._is_game_launched_check()
        self.backend.release_keys(**kwargs)

    def release_key(self, key, **kwargs):
        self._is_game_launched_check()
        self.backend.release_key(key, **kwargs)

    def type_string(self, string, duration=0.05, **kwargs):
        self._is_game_launched_check()
        self.backend.type_string(string, duration=duration, **kwargs)

    # Mouse Actions
    def click(self, button=MouseButton.LEFT, y=None, x=None, duration=0.25, **kwargs):
        self._is_game_launched_check()
        self.backend.click(button=button, y=y, x=x, duration=duration, **kwargs)

    def click_screen_region(self, button=MouseButton.LEFT, screen_region=None, **kwargs):
        self._is_game_launched_check()
        self.backend.click_screen_region(button=button, screen_region=screen_region, **kwargs)

    def click_sprite(self, button=MouseButton.LEFT, sprite=None, game_frame=None, **kwargs):
        self._is_game_launched_check()
        self.backend.click_sprite(button=button, sprite=sprite, game_frame=game_frame, **kwargs)

    def click_string(self, query_string, button=MouseButton.LEFT, game_frame=None, fuzziness=2, ocr_preset=None, **kwargs):
        self._is_game_launched_check()
        self.backend.click_string(query_string, button=button, game_frame=game_frame, fuzziness=fuzziness, ocr_preset=ocr_preset, **kwargs)

    def drag(self, button=MouseButton.LEFT, x0=None, y0=None, x1=None, y1=None, duration=1, **kwargs):
        self._is_game_launched_check()
        self.backend.drag(button=button, x0=x0, y0=y0, x1=x1, y1=y1, duration=duration, **kwargs)

    def drag_screen_region_to_screen_region(self, button=MouseButton.LEFT, start_screen_region=None, end_screen_region=None, duration=1, **kwargs):
        self._is_game_launched_check()
        self.backend.drag_screen_region_to_screen_region(button=button, start_screen_region=start_screen_region, end_screen_region=end_screen_region, duration=duration, **kwargs)

    def scroll(self, y=None, x=None, clicks=1, direction="DOWN", **kwargs):
        self._is_game_launched_check()
        self.backend.scroll(y=y, x=x, clicks=clicks, direction=direction, **kwargs)

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
