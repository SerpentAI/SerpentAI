import enum

import keyboard
import mouse

import time

from serpent.utilities import is_linux, is_macos, is_windows


class MouseButton(enum.Enum):
    LEFT = "LEFT"
    MIDDLE = "MIDDLE"
    RIGHT = "RIGHT"


class KeyboardKey(enum.Enum):
    """Supporting the 104 de facto standard PC keyboard keys"""

    KEY_ESCAPE = "KEY_ESCAPE"
    KEY_F1 = "KEY_F1"
    KEY_F2 = "KEY_F2"
    KEY_F3 = "KEY_F3"
    KEY_F4 = "KEY_F4"
    KEY_F5 = "KEY_F5"
    KEY_F6 = "KEY_F6"
    KEY_F7 = "KEY_F7"
    KEY_F8 = "KEY_F8"
    KEY_F9 = "KEY_F9"
    KEY_F10 = "KEY_F10"
    KEY_F11 = "KEY_F11"
    KEY_F12 = "KEY_F12"
    KEY_PRINT_SCREEN = "KEY_PRINT_SCREEN"
    KEY_SCROLL_LOCK = "KEY_SCROLL_LOCK"
    KEY_PAUSE = "KEY_PAUSE"

    KEY_GRAVE = "KEY_GRAVE"
    KEY_BACKTICK = KEY_GRAVE
    KEY_1 = "KEY_1"
    KEY_2 = "KEY_2"
    KEY_3 = "KEY_3"
    KEY_4 = "KEY_4"
    KEY_5 = "KEY_5"
    KEY_6 = "KEY_6"
    KEY_7 = "KEY_7"
    KEY_8 = "KEY_8"
    KEY_9 = "KEY_9"
    KEY_0 = "KEY_0"
    KEY_MINUS = "KEY_MINUS"
    KEY_DASH = KEY_MINUS
    KEY_EQUALS = "KEY_EQUALS"
    KEY_BACKSPACE = "KEY_BACKSPACE"
    KEY_INSERT = "KEY_INSERT"
    KEY_HOME = "KEY_HOME"
    KEY_PAGE_UP = "KEY_PAGE_UP"
    KEY_NUMLOCK = "KEY_NUMLOCK"
    KEY_NUMPAD_DIVIDE = "KEY_NUMPAD_DIVIDE"
    KEY_NUMPAD_SLASH = KEY_NUMPAD_DIVIDE
    KEY_NUMPAD_MULTIPLY = "KEY_NUMPAD_MULTIPLY"
    KEY_NUMPAD_STAR = KEY_NUMPAD_MULTIPLY
    KEY_NUMPAD_SUBTRACT = "KEY_NUMPAD_SUBTRACT"
    KEY_NUMPAD_DASH = KEY_NUMPAD_SUBTRACT

    KEY_TAB = "KEY_TAB"
    KEY_Q = "KEY_Q"
    KEY_W = "KEY_W"
    KEY_E = "KEY_E"
    KEY_R = "KEY_R"
    KEY_T = "KEY_T"
    KEY_Y = "KEY_Y"
    KEY_U = "KEY_U"
    KEY_I = "KEY_I"
    KEY_O = "KEY_O"
    KEY_P = "KEY_P"
    KEY_LEFT_BRACKET = "KEY_LEFT_BRACKET"
    KEY_RIGHT_BRACKET = "KEY_RIGHT_BRACKET"
    KEY_BACKSLASH = "KEY_BACKSLASH"
    KEY_DELETE = "KEY_DELETE"
    KEY_END = "KEY_END"
    KEY_PAGE_DOWN = "KEY_PAGE_DOWN"
    KEY_NUMPAD_7 = "KEY_NUMPAD_7"
    KEY_NUMPAD_8 = "KEY_NUMPAD_8"
    KEY_NUMPAD_9 = "KEY_NUMPAD_9"
    KEY_NUMPAD_ADD = "KEY_NUMPAD_ADD"
    KEY_NUMPAD_PLUS = KEY_NUMPAD_ADD

    KEY_CAPSLOCK = "KEY_CAPSLOCK"
    KEY_A = "KEY_A"
    KEY_S = "KEY_S"
    KEY_D = "KEY_D"
    KEY_F = "KEY_F"
    KEY_G = "KEY_G"
    KEY_H = "KEY_H"
    KEY_J = "KEY_J"
    KEY_K = "KEY_K"
    KEY_L = "KEY_L"
    KEY_SEMICOLON = "KEY_SEMICOLON"
    KEY_APOSTROPHE = "KEY_APOSTROPHE"
    KEY_RETURN = "KEY_RETURN"
    KEY_ENTER = KEY_RETURN
    KEY_NUMPAD_4 = "KEY_NUMPAD_4"
    KEY_NUMPAD_5 = "KEY_NUMPAD_5"
    KEY_NUMPAD_6 = "KEY_NUMPAD_6"

    KEY_LEFT_SHIFT = "KEY_LEFT_SHIFT"
    KEY_Z = "KEY_Z"
    KEY_X = "KEY_X"
    KEY_C = "KEY_C"
    KEY_V = "KEY_V"
    KEY_B = "KEY_B"
    KEY_N = "KEY_N"
    KEY_M = "KEY_M"
    KEY_COMMA = "KEY_COMMA"
    KEY_PERIOD = "KEY_PERIOD"
    KEY_SLASH = "KEY_SLASH"
    KEY_RIGHT_SHIFT = "KEY_RIGHT_SHIFT"
    KEY_UP = "KEY_UP"
    KEY_NUMPAD_1 = "KEY_NUMPAD_1"
    KEY_NUMPAD_2 = "KEY_NUMPAD_2"
    KEY_NUMPAD_3 = "KEY_NUMPAD_3"
    KEY_NUMPAD_RETURN = "KEY_NUMPAD_RETURN"
    KEY_NUMPAD_ENTER = KEY_NUMPAD_RETURN

    KEY_LEFT_CTRL = "KEY_LEFT_CTRL"
    KEY_LEFT_SUPER = "KEY_LEFT_SUPER"
    KEY_LEFT_WINDOWS = KEY_LEFT_SUPER
    KEY_LEFT_ALT = "KEY_LEFT_ALT"
    KEY_SPACE = "KEY_SPACE"
    KEY_RIGHT_ALT = "KEY_RIGHT_ALT"
    KEY_RIGHT_SUPER = "KEY_RIGHT_SUPER"
    KEY_RIGHT_WINDOWS = KEY_RIGHT_SUPER
    KEY_APP_MENU = "KEY_APP_MENU"
    KEY_RIGHT_CTRL = "KEY_RIGHT_CTRL"
    KEY_LEFT = "KEY_LEFT"
    KEY_DOWN = "KEY_DOWN"
    KEY_RIGHT = "KEY_RIGHT"
    KEY_NUMPAD_0 = "KEY_NUMPAD_0"
    KEY_NUMPAD_DECIMAL = "KEY_NUMPAD_DECIMAL"
    KEY_NUMPAD_PERIOD = KEY_NUMPAD_DECIMAL

    # macOS
    KEY_COMMAND = "KEY_COMMAND"


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

if is_linux():
    keyboard_module_scan_code_mapping = {
        1: KeyboardKey.KEY_ESCAPE,
        59: KeyboardKey.KEY_F1,
        60: KeyboardKey.KEY_F2,
        61: KeyboardKey.KEY_F3,
        62: KeyboardKey.KEY_F4,
        63: KeyboardKey.KEY_F5,
        64: KeyboardKey.KEY_F6,
        65: KeyboardKey.KEY_F7,
        66: KeyboardKey.KEY_F8,
        67: KeyboardKey.KEY_F9,
        68: KeyboardKey.KEY_F10,
        87: KeyboardKey.KEY_F11,
        88: KeyboardKey.KEY_F12,
        99: KeyboardKey.KEY_PRINT_SCREEN,
        119: KeyboardKey.KEY_PAUSE,
        41: KeyboardKey.KEY_GRAVE,
        2: KeyboardKey.KEY_1,
        3: KeyboardKey.KEY_2,
        4: KeyboardKey.KEY_3,
        5: KeyboardKey.KEY_4,
        6: KeyboardKey.KEY_5,
        7: KeyboardKey.KEY_6,
        8: KeyboardKey.KEY_7,
        9: KeyboardKey.KEY_8,
        10: KeyboardKey.KEY_9,
        11: KeyboardKey.KEY_0,
        12: KeyboardKey.KEY_MINUS,
        13: KeyboardKey.KEY_EQUALS,
        14: KeyboardKey.KEY_BACKSPACE,
        110: KeyboardKey.KEY_INSERT,
        102: KeyboardKey.KEY_HOME,
        104: KeyboardKey.KEY_PAGE_UP,
        69: KeyboardKey.KEY_NUMLOCK,
        98: KeyboardKey.KEY_NUMPAD_DIVIDE,
        55: KeyboardKey.KEY_NUMPAD_MULTIPLY,
        74: KeyboardKey.KEY_NUMPAD_SUBTRACT,
        15: KeyboardKey.KEY_TAB,
        16: KeyboardKey.KEY_Q,
        17: KeyboardKey.KEY_W,
        18: KeyboardKey.KEY_E,
        19: KeyboardKey.KEY_R,
        20: KeyboardKey.KEY_T,
        21: KeyboardKey.KEY_Y,
        22: KeyboardKey.KEY_U,
        23: KeyboardKey.KEY_I,
        24: KeyboardKey.KEY_O,
        25: KeyboardKey.KEY_P,
        26: KeyboardKey.KEY_LEFT_BRACKET,
        27: KeyboardKey.KEY_RIGHT_BRACKET,
        43: KeyboardKey.KEY_BACKSLASH,
        111: KeyboardKey.KEY_DELETE,
        107: KeyboardKey.KEY_END,
        109: KeyboardKey.KEY_PAGE_DOWN,
        71: KeyboardKey.KEY_NUMPAD_7,
        72: KeyboardKey.KEY_NUMPAD_8,
        73: KeyboardKey.KEY_NUMPAD_9,
        78: KeyboardKey.KEY_NUMPAD_ADD,
        30: KeyboardKey.KEY_A,
        31: KeyboardKey.KEY_S,
        32: KeyboardKey.KEY_D,
        33: KeyboardKey.KEY_F,
        34: KeyboardKey.KEY_G,
        35: KeyboardKey.KEY_H,
        36: KeyboardKey.KEY_J,
        37: KeyboardKey.KEY_K,
        38: KeyboardKey.KEY_L,
        39: KeyboardKey.KEY_SEMICOLON,
        40: KeyboardKey.KEY_APOSTROPHE,
        28: KeyboardKey.KEY_RETURN,
        75: KeyboardKey.KEY_NUMPAD_4,
        76: KeyboardKey.KEY_NUMPAD_5,
        77: KeyboardKey.KEY_NUMPAD_6,
        42: KeyboardKey.KEY_LEFT_SHIFT,
        44: KeyboardKey.KEY_Z,
        45: KeyboardKey.KEY_X,
        46: KeyboardKey.KEY_C,
        47: KeyboardKey.KEY_V,
        48: KeyboardKey.KEY_B,
        49: KeyboardKey.KEY_N,
        50: KeyboardKey.KEY_M,
        51: KeyboardKey.KEY_COMMA,
        52: KeyboardKey.KEY_PERIOD,
        53: KeyboardKey.KEY_SLASH,
        54: KeyboardKey.KEY_RIGHT_SHIFT,
        103: KeyboardKey.KEY_UP,
        79: KeyboardKey.KEY_NUMPAD_1,
        80: KeyboardKey.KEY_NUMPAD_2,
        81: KeyboardKey.KEY_NUMPAD_3,
        96: KeyboardKey.KEY_NUMPAD_RETURN,
        29: KeyboardKey.KEY_LEFT_CTRL,
        56: KeyboardKey.KEY_LEFT_ALT,
        57: KeyboardKey.KEY_SPACE,
        100: KeyboardKey.KEY_RIGHT_ALT,
        97: KeyboardKey.KEY_RIGHT_CTRL,
        105: KeyboardKey.KEY_LEFT,
        108: KeyboardKey.KEY_DOWN,
        106: KeyboardKey.KEY_RIGHT,
        82: KeyboardKey.KEY_NUMPAD_0,
        83: KeyboardKey.KEY_NUMPAD_PERIOD,
        125: KeyboardKey.KEY_LEFT_WINDOWS,
        126: KeyboardKey.KEY_RIGHT_WINDOWS
    }
elif is_macos():
    keyboard_module_scan_code_mapping = {
        0x35: KeyboardKey.KEY_ESCAPE,
        0x7A: KeyboardKey.KEY_F1,
        0x78: KeyboardKey.KEY_F2,
        0x63: KeyboardKey.KEY_F3,
        0x76: KeyboardKey.KEY_F4,
        0x60: KeyboardKey.KEY_F5,
        0x61: KeyboardKey.KEY_F6,
        0x62: KeyboardKey.KEY_F7,
        0x64: KeyboardKey.KEY_F8,
        0x65: KeyboardKey.KEY_F9,
        0x6D: KeyboardKey.KEY_F10,
        0x67: KeyboardKey.KEY_F11,
        0x6F: KeyboardKey.KEY_F12,
        0x69: KeyboardKey.KEY_PRINT_SCREEN,
        0x6B: KeyboardKey.KEY_SCROLL_LOCK,
        0x71: KeyboardKey.KEY_PAUSE,
        0x32: KeyboardKey.KEY_GRAVE,
        0x12: KeyboardKey.KEY_1,
        0x13: KeyboardKey.KEY_2,
        0x14: KeyboardKey.KEY_3,
        0x15: KeyboardKey.KEY_4,
        0x17: KeyboardKey.KEY_5,
        0x16: KeyboardKey.KEY_6,
        0x1A: KeyboardKey.KEY_7,
        0x1C: KeyboardKey.KEY_8,
        0x19: KeyboardKey.KEY_9,
        0x1D: KeyboardKey.KEY_0,
        0x1B: KeyboardKey.KEY_MINUS,
        0x18: KeyboardKey.KEY_EQUALS,
        0x33: KeyboardKey.KEY_BACKSPACE,
        0x72: KeyboardKey.KEY_INSERT,
        0x73: KeyboardKey.KEY_HOME,
        0x74: KeyboardKey.KEY_PAGE_UP,
        0x47: KeyboardKey.KEY_NUMLOCK,
        0x4B: KeyboardKey.KEY_NUMPAD_DIVIDE,
        0x43: KeyboardKey.KEY_NUMPAD_MULTIPLY,
        0x4E: KeyboardKey.KEY_NUMPAD_SUBTRACT,
        0x30: KeyboardKey.KEY_TAB,
        0x0C: KeyboardKey.KEY_Q,
        0x0D: KeyboardKey.KEY_W,
        0x0E: KeyboardKey.KEY_E,
        0x0F: KeyboardKey.KEY_R,
        0x11: KeyboardKey.KEY_T,
        0x10: KeyboardKey.KEY_Y,
        0x20: KeyboardKey.KEY_U,
        0x22: KeyboardKey.KEY_I,
        0x1F: KeyboardKey.KEY_O,
        0x23: KeyboardKey.KEY_P,
        0x21: KeyboardKey.KEY_LEFT_BRACKET,
        0x1E: KeyboardKey.KEY_RIGHT_BRACKET,
        0x2A: KeyboardKey.KEY_BACKSLASH,
        0x75: KeyboardKey.KEY_DELETE,
        0x77: KeyboardKey.KEY_END,
        0x79: KeyboardKey.KEY_PAGE_DOWN,
        0x59: KeyboardKey.KEY_NUMPAD_7,
        0x5B: KeyboardKey.KEY_NUMPAD_8,
        0x5C: KeyboardKey.KEY_NUMPAD_9,
        0x45: KeyboardKey.KEY_NUMPAD_ADD,
        0x39: KeyboardKey.KEY_CAPSLOCK,
        0x00: KeyboardKey.KEY_A,
        0x01: KeyboardKey.KEY_S,
        0x02: KeyboardKey.KEY_D,
        0x03: KeyboardKey.KEY_F,
        0x05: KeyboardKey.KEY_G,
        0x04: KeyboardKey.KEY_H,
        0x26: KeyboardKey.KEY_J,
        0x28: KeyboardKey.KEY_K,
        0x25: KeyboardKey.KEY_L,
        0x29: KeyboardKey.KEY_SEMICOLON,
        0x27: KeyboardKey.KEY_APOSTROPHE,
        0x24: KeyboardKey.KEY_RETURN,
        0x56: KeyboardKey.KEY_NUMPAD_4,
        0x57: KeyboardKey.KEY_NUMPAD_5,
        0x58: KeyboardKey.KEY_NUMPAD_6,
        0x38: KeyboardKey.KEY_LEFT_SHIFT,
        0x06: KeyboardKey.KEY_Z,
        0x07: KeyboardKey.KEY_X,
        0x08: KeyboardKey.KEY_C,
        0x09: KeyboardKey.KEY_V,
        0x0B: KeyboardKey.KEY_B,
        0x2D: KeyboardKey.KEY_N,
        0x2E: KeyboardKey.KEY_M,
        0x2B: KeyboardKey.KEY_COMMA,
        0x2F: KeyboardKey.KEY_PERIOD,
        0x2C: KeyboardKey.KEY_SLASH,
        0x3C: KeyboardKey.KEY_RIGHT_SHIFT,
        0x7E: KeyboardKey.KEY_UP,
        0x53: KeyboardKey.KEY_NUMPAD_1,
        0x54: KeyboardKey.KEY_NUMPAD_2,
        0x55: KeyboardKey.KEY_NUMPAD_3,
        0x4C: KeyboardKey.KEY_NUMPAD_RETURN,
        0x3B: KeyboardKey.KEY_LEFT_CTRL,
        0x3A: KeyboardKey.KEY_LEFT_ALT,
        0x31: KeyboardKey.KEY_SPACE,
        0x3D: KeyboardKey.KEY_RIGHT_ALT,
        0x3E: KeyboardKey.KEY_RIGHT_CTRL,
        0x7B: KeyboardKey.KEY_LEFT,
        0x7D: KeyboardKey.KEY_DOWN,
        0x7C: KeyboardKey.KEY_RIGHT,
        0x52: KeyboardKey.KEY_NUMPAD_0,
        0x41: KeyboardKey.KEY_NUMPAD_PERIOD,
        0x37: KeyboardKey.KEY_LEFT_WINDOWS,
        0x36: KeyboardKey.KEY_RIGHT_WINDOWS
    }
elif is_windows():  # Important Missing Keys: PAUSE, RIGHT CTRL, RIGHT ALT (Dupe Info from 'keyboard' library)
    keyboard_module_scan_code_mapping = {
        1: KeyboardKey.KEY_ESCAPE,
        59: KeyboardKey.KEY_F1,
        60: KeyboardKey.KEY_F2,
        61: KeyboardKey.KEY_F3,
        62: KeyboardKey.KEY_F4,
        63: KeyboardKey.KEY_F5,
        64: KeyboardKey.KEY_F6,
        65: KeyboardKey.KEY_F7,
        66: KeyboardKey.KEY_F8,
        67: KeyboardKey.KEY_F9,
        68: KeyboardKey.KEY_F10,
        87: KeyboardKey.KEY_F11,
        88: KeyboardKey.KEY_F12,
        55: KeyboardKey.KEY_PRINT_SCREEN,
        70: KeyboardKey.KEY_SCROLL_LOCK,
        41: KeyboardKey.KEY_GRAVE,
        2: KeyboardKey.KEY_1,
        3: KeyboardKey.KEY_2,
        4: KeyboardKey.KEY_3,
        5: KeyboardKey.KEY_4,
        6: KeyboardKey.KEY_5,
        7: KeyboardKey.KEY_6,
        8: KeyboardKey.KEY_7,
        9: KeyboardKey.KEY_8,
        10: KeyboardKey.KEY_9,
        11: KeyboardKey.KEY_0,
        12: KeyboardKey.KEY_MINUS,
        13: KeyboardKey.KEY_EQUALS,
        14: KeyboardKey.KEY_BACKSPACE,
        82: KeyboardKey.KEY_INSERT,
        71: KeyboardKey.KEY_HOME,
        73: KeyboardKey.KEY_PAGE_UP,
        69: KeyboardKey.KEY_NUMLOCK,
        1077: KeyboardKey.KEY_NUMPAD_DIVIDE,
        1079: KeyboardKey.KEY_NUMPAD_MULTIPLY,
        1098: KeyboardKey.KEY_NUMPAD_SUBTRACT,
        15: KeyboardKey.KEY_TAB,
        16: KeyboardKey.KEY_Q,
        17: KeyboardKey.KEY_W,
        18: KeyboardKey.KEY_E,
        19: KeyboardKey.KEY_R,
        20: KeyboardKey.KEY_T,
        21: KeyboardKey.KEY_Y,
        22: KeyboardKey.KEY_U,
        23: KeyboardKey.KEY_I,
        24: KeyboardKey.KEY_O,
        25: KeyboardKey.KEY_P,
        26: KeyboardKey.KEY_LEFT_BRACKET,
        27: KeyboardKey.KEY_RIGHT_BRACKET,
        43: KeyboardKey.KEY_BACKSLASH,
        83: KeyboardKey.KEY_DELETE,
        79: KeyboardKey.KEY_END,
        81: KeyboardKey.KEY_PAGE_DOWN,
        1095: KeyboardKey.KEY_NUMPAD_7,
        1096: KeyboardKey.KEY_NUMPAD_8,
        1097: KeyboardKey.KEY_NUMPAD_9,
        1102: KeyboardKey.KEY_NUMPAD_ADD,
        58: KeyboardKey.KEY_CAPSLOCK,
        30: KeyboardKey.KEY_A,
        31: KeyboardKey.KEY_S,
        32: KeyboardKey.KEY_D,
        33: KeyboardKey.KEY_F,
        34: KeyboardKey.KEY_G,
        35: KeyboardKey.KEY_H,
        36: KeyboardKey.KEY_J,
        37: KeyboardKey.KEY_K,
        38: KeyboardKey.KEY_L,
        39: KeyboardKey.KEY_SEMICOLON,
        40: KeyboardKey.KEY_APOSTROPHE,
        28: KeyboardKey.KEY_RETURN,
        1099: KeyboardKey.KEY_NUMPAD_4,
        1100: KeyboardKey.KEY_NUMPAD_5,
        1101: KeyboardKey.KEY_NUMPAD_6,
        42: KeyboardKey.KEY_LEFT_SHIFT,
        44: KeyboardKey.KEY_Z,
        45: KeyboardKey.KEY_X,
        46: KeyboardKey.KEY_C,
        47: KeyboardKey.KEY_V,
        48: KeyboardKey.KEY_B,
        49: KeyboardKey.KEY_N,
        50: KeyboardKey.KEY_M,
        51: KeyboardKey.KEY_COMMA,
        52: KeyboardKey.KEY_PERIOD,
        53: KeyboardKey.KEY_SLASH,
        54: KeyboardKey.KEY_RIGHT_SHIFT,
        72: KeyboardKey.KEY_UP,
        1103: KeyboardKey.KEY_NUMPAD_1,
        1104: KeyboardKey.KEY_NUMPAD_2,
        1105: KeyboardKey.KEY_NUMPAD_3,
        1052: KeyboardKey.KEY_NUMPAD_RETURN,
        29: KeyboardKey.KEY_LEFT_CTRL,
        56: KeyboardKey.KEY_LEFT_ALT,
        57: KeyboardKey.KEY_SPACE,
        75: KeyboardKey.KEY_LEFT,
        80: KeyboardKey.KEY_DOWN,
        77: KeyboardKey.KEY_RIGHT,
        1106: KeyboardKey.KEY_NUMPAD_0,
        1107: KeyboardKey.KEY_NUMPAD_PERIOD,
        91: KeyboardKey.KEY_LEFT_WINDOWS,
        92: KeyboardKey.KEY_RIGHT_WINDOWS,
        93: KeyboardKey.KEY_APP_MENU
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

    def capture_keys(self, duration=0.5):
        started_at = time.time()
        captured_key_events = list()

        keyboard.hook(captured_key_events.append)

        while time.time() - started_at <= duration:
            time.sleep(0.01)

        keyboard.unhook(captured_key_events.append)

        return captured_key_events

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

    def click_string(self, query_string, button=MouseButton.LEFT, game_frame=None, fuzziness=2, ocr_preset=None, **kwargs):
        self._is_game_launched_check()
        self.backend.click_string(query_string, button=button, game_frame=game_frame, fuzziness=fuzziness, ocr_preset=ocr_preset, **kwargs)

    def drag(self, button=MouseButton.LEFT, x0=None, y0=None, x1=None, y1=None, duration=1, **kwargs):
        self._is_game_launched_check()
        self.backend.drag(button=button, x0=x0, y0=y0, x1=x1, y1=y1, duration=duration, **kwargs)

    def drag_screen_region_to_screen_region(self, button=MouseButton.LEFT, start_screen_region=None, end_screen_region=None, duration=1, **kwargs):
        self._is_game_launched_check()
        self.backend.drag_screen_region_to_screen_region(button=button, start_screen_region=start_screen_region, end_screen_region=end_screen_region, duration=duration, **kwargs)

    def scroll(self, x=None, y=None, clicks=1, direction="DOWN", **kwargs):
        self._is_game_launched_check()
        self.backend.scroll(x=x, y=y, clicks=clicks, direction=direction, **kwargs)

    def capture_mouse(self, duration=0.5):
        started_at = time.time()
        captured_mouse_events = list()

        mouse.hook(captured_mouse_events.append)

        while time.time() - started_at <= duration:
            time.sleep(0.01)

        mouse.unhook(captured_mouse_events.append)

        return captured_mouse_events

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
