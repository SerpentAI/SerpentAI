import sys


class WindowControllerError(BaseException):
    pass


class WindowController:

    def __init__(self):
        self.adapter = self._load_adapter()()

    def locate_window(self, name):
        return self.adapter.locate_window(name)

    def move_window(self, window_id, x, y):
        self.adapter.move_window(window_id, x, y)

    def focus_window(self, window_id):
        self.adapter.focus_window(window_id)

    def is_window_focused(self, window_id):
        return self.adapter.is_window_focused(window_id)

    def get_window_geometry(self, window_id):
        return self.adapter.get_window_geometry(window_id)

    def _load_adapter(self):
        if sys.platform in ["linux", "linux2"]:
            from serpent.window_controllers.linux_window_controller import LinuxWindowController
            return LinuxWindowController
        elif sys.platform == "darwin":
            raise WindowControllerError("Mac OS is not supported... :(")
        elif sys.platform == "win32":
            from serpent.window_controllers.win32_window_controller import Win32WindowController
            return Win32WindowController