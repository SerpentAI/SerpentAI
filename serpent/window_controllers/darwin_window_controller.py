from serpent.window_controller import WindowController

import applescript


class DarwinWindowController(WindowController):

    def __init__(self):
        pass

    def locate_window(self, name):
        return name

    def move_window(self, window_id, x, y):
        applescript.AppleScript(f'''
            tell application "System Events" to tell window 1 of process "{window_id}"
                set position to { {x}, {y} }
            end tell
        ''').run()

    def focus_window(self, window_id):
        applescript.AppleScript(f'''
            tell application "System Events" to tell process "{window_id}"
                set frontmost to true
            end tell
        ''').run()

    def is_window_focused(self, window_id):
        focused_window_id = applescript.AppleScript('''
            tell application "System Events"
                set focusedWindow to name of first application process whose frontmost is true
                return focusedWindow
            end tell
        ''').run()

        return focused_window_id == window_id

    def get_window_geometry(self, window_id):
        geometry = dict()

        window_geometry = applescript.AppleScript(f'''
            tell application "System Events" to tell process "{window_id}"
                return get size of window 1
            end tell
        ''').run()

        geometry["width"] = int(window_geometry[0])
        geometry["height"] = int(window_geometry[1] - 20)

        window_information = applescript.AppleScript(f'''
            tell application "System Events" to tell window 1 of process "{window_id}"
                return get position
            end tell
        ''').run()

        geometry["x_offset"] = int(window_information[0])
        geometry["y_offset"] = int(window_information[1] + 20)

        return geometry
