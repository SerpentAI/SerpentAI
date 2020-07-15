#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
Cef Keyboard Manager.
Cef Keyboard management is complex, so we outsourced it to this file for
better readability.
'''

from kivy.core.window import Window

from .cefpython import cefpython


class CEFKeyboardManagerSingleton:
    # Kivy does not provide modifiers in on_key_up, but these
    # must be sent to CEF as well.
    is_shift1 = False
    is_shift2 = False
    is_ctrl1 = False
    is_ctrl2 = False
    is_alt1 = False
    is_alt2 = False

    def __init__(self, *largs, **dargs):
        pass

    def reset_all_modifiers(self):
        self.is_shift1 = False
        self.is_shift2 = False
        self.is_ctrl1 = False
        self.is_ctrl2 = False
        self.is_alt1 = False
        self.is_alt2 = False

    def kivy_keyboard_on_textinput(self, browser, window, text):
        """ Kivy ~ > 1.9.2 with SDL2 window, uses on_textinput instead of
        on_key_down
        """
        modifiers = list()
        keycode = (ord(text), text)
        self.process_key_down(browser, None, keycode, text, modifiers)

    def kivy_on_key_down(self, browser, keyboard, keycode, text, modifiers):
        whitelist = (9, 8, 13, 27)
        if Window.__class__.__module__ == 'kivy.core.window.window_sdl2' and \
                (keycode[0] not in whitelist):
            return
        self.process_key_down(browser, keyboard, keycode, text, modifiers)

    def process_key_down(self, browser, keyboard, key, text, modifiers):
        # NOTE: Right alt modifier is not sent by Kivy through modifiers param.
        # print("---- on_key_down")
        # print("-- key="+str(key))
        # print(text) - utf-8 char
        # print("-- modifiers="+str(modifiers))
        # if text:
        #    print("-- ord(text)="+str(ord(text)))

        # CEF key event type:
        #   KEYEVENT_RAWKEYDOWN = 0
        #   KEYEVENT_KEYDOWN = 1
        #   KEYEVENT_KEYUP = 2
        #   KEYEVENT_CHAR = 3

        # Check if key is 'special'.
        # if we pass that to cefpython, it will crash.
        if key[1] == 'special':
            return

        # On escape release the keyboard, see the injected in OnLoadStart()
        if key[0] == 27:
            browser.GetFocusedFrame().ExecuteJavascript(
                "__kivy__on_escape()")
            return

        # Modify text for enter key
        if key[0] == 13:
            text = "\r"

        # CEF modifiers
        # When pressing ctrl also set modifiers for ctrl
        if key[0] in (306, 305):
            modifiers.append('ctrl')
        cef_modifiers = cefpython.EVENTFLAG_NONE
        if "shift" in modifiers:
            cef_modifiers |= cefpython.EVENTFLAG_SHIFT_DOWN
        if "ctrl" in modifiers:
            cef_modifiers |= cefpython.EVENTFLAG_CONTROL_DOWN
        if "alt" in modifiers:
            cef_modifiers |= cefpython.EVENTFLAG_ALT_DOWN
        if "capslock" in modifiers:
            cef_modifiers |= cefpython.EVENTFLAG_CAPS_LOCK_ON

        keycode = self.get_windows_key_code(key[0])
        charcode = key[0]
        if text:
            charcode = ord(text)

        # Do not send RAW-key for key-codes 35-40 aka ($#%&
        if key[0] not in range(35, 40+1):
            # Send key event to cef: RAWKEYDOWN
            key_event = {
                    "type": cefpython.KEYEVENT_RAWKEYDOWN,
                    "windows_key_code": keycode,
                    "character": charcode,
                    "unmodified_character": charcode,
                    "modifiers": cef_modifiers,
            }
            # print("- DOWN RAW SendKeyEvent: %s" % key_event)
            browser.SendKeyEvent(key_event)

        # Send key event to cef: CHAR
        if text:
            key_event = {
                    "type": cefpython.KEYEVENT_CHAR,
                    "windows_key_code": keycode,
                    "character": charcode,
                    "unmodified_character": charcode,
                    "modifiers": cef_modifiers,
            }
            # print("- DOWN text SendKeyEvent: %s" % key_event)
            browser.SendKeyEvent(key_event)

        if key[0] == 304:
            self.is_shift1 = True
        elif key[0] == 303:
            self.is_shift2 = True
        elif key[0] == 306:
            self.is_ctrl1 = True
        elif key[0] == 305:
            self.is_ctrl2 = True
        elif key[0] == 308:
            self.is_alt1 = True
        elif key[0] == 313:
            self.is_alt2 = True

    def kivy_on_key_up(self, browser, keyboard, key):
        # print("---- on_key_up")
        # print("-- key="+str(key))

        # Check if kivy-key-code is -1. This means it is a not a key which
        # should be passed to CEF. (Ex: Change keyboard layout)
        if key[0] == -1:
            return

        # CEF modifiers
        cef_modifiers = cefpython.EVENTFLAG_NONE
        if self.is_shift1 or self.is_shift2:
            cef_modifiers |= cefpython.EVENTFLAG_SHIFT_DOWN
        if self.is_ctrl1 or self.is_ctrl2:
            cef_modifiers |= cefpython.EVENTFLAG_CONTROL_DOWN
        if self.is_alt1:
            cef_modifiers |= cefpython.EVENTFLAG_ALT_DOWN

        keycode = self.get_windows_key_code(key[0])
        charcode = key[0]

        # Send key event to cef: KEYUP
        key_event = {
                "type": cefpython.KEYEVENT_KEYUP,
                "windows_key_code": keycode,
                "character": charcode,
                "unmodified_character": charcode,
                "modifiers": cef_modifiers,
        }
        # print("- UP SendKeyEvent: %s" % key_event)
        browser.SendKeyEvent(key_event)

        if key[0] == 304:
            self.is_shift1 = False
        elif key[0] == 303:
            self.is_shift2 = False
        elif key[0] == 306:
            self.is_ctrl1 = False
        elif key[0] == 305:
            self.is_ctrl2 = False
        elif key[0] == 308:
            self.is_alt1 = False
        elif key[0] == 313:
            self.is_alt2 = False

    def get_windows_key_code(self, kivycode):

        cefcode = kivycode

        # NOTES:
        # - Map on all platforms to OnPreKeyEvent.event["windows_key_code"]
        # - Mapping all keys was not necessary on Linux, for example
        #   'comma' worked fine, while 'dot' did not, but mapping all keys
        #   to make sure it will work correctly on all platforms.
        # - If some key mapping is missing launch wxpython.py and see
        #   OnPreKeyEvent info for key events and replacate it here.
        #   (key codes can also be found on MSDN Virtual-key codes page)

        other_keys_map = {
            # Escape
            "27": 27,
            # F1-F12
            "282": 112, "283": 113, "284": 114, "285": 115,
            "286": 116, "287": 117, "288": 118, "289": 119,
            "290": 120, "291": 121, "292": 122, "293": 123,
            # Tab
            "9": 9,
            # Left Shift, Right Shift
            "304": 16, "303": 16,
            # Left Ctrl, Right Ctrl
            "306": 17, "305": 17,
            # Left Alt, Right Alt
            # TODO: left alt is_system_key=True in CEF but only when RAWKEYDOWN
            "308": 18, "313": 225,
            # Backspace
            "8": 8,
            # Enter
            "13": 13,
            # PrScr, ScrLck, Pause
            "316": 42, "302": 145, "19": 19,
            # Insert, Delete,
            # Home, End,
            # Pgup, Pgdn
            "277": 45, "127": 46,
            "278": 36, "279": 35,
            "280": 33, "281": 34,
            # Arrows (left, up, right, down)
            "276": 37, "273": 38, "275": 39, "274": 40,
            # tilde
            "96": 192,
            # minus, plus
            "45": 189, "61": 187,
            # square brackets / curly brackets, backslash
            "91": 219, "93": 221, "92": 220,
            # windows key
            "311": 91,
            # colon / semicolon
            "59": 186,
            # single quote / double quote
            "39": 222,
            # comma, dot, slash
            "44": 188, "46": 190, "47": 91,
            # context menu key is 93, but disable as it crashes app after
            # context menu is shown.
            "319": 0,
        }
        if str(kivycode) in other_keys_map:
            cefcode = other_keys_map[str(kivycode)]

        return cefcode


CEFKeyboardManager = CEFKeyboardManagerSingleton()
