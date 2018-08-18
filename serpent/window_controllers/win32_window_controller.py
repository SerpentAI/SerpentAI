from serpent.window_controller import WindowController

import win32gui
import win32con

import re

window_id = 0


class Win32WindowController(WindowController):

    def __init__(self):
        pass

    def locate_window(self, name):
        global window_id
        window_id = win32gui.FindWindow(None, name)

        if window_id != 0:
            return window_id

        def callback(wid, pattern):
            global window_id

            if re.match(pattern, str(win32gui.GetWindowText(wid))) is not None:
                window_id = wid

        win32gui.EnumWindows(callback, name)

        return window_id

    def move_window(self, window_id, x, y):
        x0, y0, x1, y1 = win32gui.GetWindowRect(window_id)
        win32gui.MoveWindow(window_id, x, y, x1 - x0, y1 - y0, True)

    def resize_window(self, window_id, width, height):
        x0, y0, x1, y1 = win32gui.GetWindowRect(window_id)
        win32gui.MoveWindow(window_id, x0, y0, width, height, True)

    def focus_window(self, window_id):
        win32gui.SetForegroundWindow(window_id)

    def bring_window_to_top(self, window_id):
        win32gui.ShowWindow(window_id, win32con.SW_RESTORE)
        win32gui.SetWindowPos(window_id, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)  
        win32gui.SetWindowPos(window_id, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)  
        win32gui.SetWindowPos(window_id, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_SHOWWINDOW + win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)

    def is_window_focused(self, window_id):
        focused_window_id = win32gui.GetForegroundWindow()
        return focused_window_id == window_id

    def get_focused_window_name(self):
        return win32gui.GetWindowText(win32gui.GetForegroundWindow())

    def get_window_geometry(self, window_id):
        geometry = dict()

        x, y, width, height = win32gui.GetClientRect(window_id)

        geometry["width"] = width
        geometry["height"] = height

        x0, y0, x1, y1 = win32gui.GetWindowRect(window_id)

        border_width = ((x1 - x0 - width) // 2)

        geometry["x_offset"] = x0 + border_width
        geometry["y_offset"] = y0 + (y1 - y0 - height - border_width)

        return geometry
