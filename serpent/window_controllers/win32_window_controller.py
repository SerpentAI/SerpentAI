from serpent.window_controller import WindowController

import win32gui
import win32api

import win32process
import win32con

class Win32WindowController(WindowController):

    def get_hwnds_for_pid (self, pid):
        def callback (hwnd, hwnds):
            if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                _, found_pid = win32process.GetWindowThreadProcessId (hwnd)
                if found_pid == pid:
                    hwnds.append (hwnd)
            return True
        
        hwnds = []
        win32gui.EnumWindows (callback, hwnds)
        return hwnds

    def get_child_hwnds(self, hwnd):
        def callback (hwnd, hwnds):
            hwnds.append(hwnd)            
            return True
        hwnds = []
        win32gui.EnumChildWindows (hwnd, callback, hwnds)

        return hwnds
    

    def __init__(self):
        pass

    def locate_window(self, name):
        return win32gui.FindWindow(None, name)

    def move_window(self, window_id, x, y):
        x0, y0, x1, y1 = win32gui.GetWindowRect(window_id)
        win32gui.MoveWindow(window_id, x, y, x1 - x0, y1 - y0, True)

    def resize_window(self, window_id, width, height):
        x0, y0, x1, y1 = win32gui.GetWindowRect(window_id)
        win32gui.MoveWindow(window_id, x0, y0, width, height, True)

    def focus_window(self, window_id):
        win32gui.SetForegroundWindow(window_id)

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
