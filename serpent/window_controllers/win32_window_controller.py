from serpent.window_controller import WindowController

import win32gui


class Win32WindowController(WindowController):

    def __init__(self):
        pass

    def locate_window(self, name):
        return win32gui.FindWindow(None, name)

    def move_window(self, window_id, x, y):
        x0, y0, x1, y1 = win32gui.GetWindowRect(window_id)
        win32gui.MoveWindow(window_id, x, y, x1 - x0, y1 - y0, True)

    def focus_window(self, window_id):
        win32gui.SetForegroundWindow(window_id)

    def is_window_focused(self, window_id):
        focused_window_id = win32gui.GetForegroundWindow()
        return focused_window_id == window_id

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
