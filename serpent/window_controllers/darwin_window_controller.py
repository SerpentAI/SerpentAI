from serpent.window_controller import WindowController

import applescript


class DarwinWindowController(WindowController):

    def __init__(self):
        pass

    def locate_window(self, name):
        tuple_id = name.split("::")
        if len(tuple_id) == 1:
            tuple_id = [tuple_id[0], "1"]
        return tuple_id

    def move_window(self, window_id, x, y):
        applescript.AppleScript(f'''
            tell application "System Events" to tell window "{window_id[1]}" of process "{window_id[0]}"
                set position to { {x}, {y} }
            end tell
        ''').run()

    def resize_window(self, window_id, width, height):
        applescript.AppleScript(f'''
            tell application "System Events" to tell window "{window_id[1]}" of process "{window_id[0]}"
                set size to { {width}, {height} }
            end tell
        ''').run()

    def focus_window(self, window_id):
        applescript.AppleScript(f'''
            tell application "System Events" to tell process "{window_id[0]}"
                set frontmost to true
            end tell
        ''').run()

    def is_window_focused(self, window_id):
        return self.get_focused_window_name() == window_id[0]

    def get_focused_window_name(self):
        focused_window_id = applescript.AppleScript('''
            tell application "System Events"
                return title of first application process whose frontmost is true
            end tell
        ''').run()

        return focused_window_id

    def get_window_geometry(self, window_id):
        geometry = dict()

        window_geometry = applescript.AppleScript(f'''
            tell application "System Events" to tell process "{window_id[0]}"
                return get size of window "{window_id[1]}"
            end tell
        ''').run()

        geometry["width"] = int(window_geometry[0])
        geometry["height"] = int(window_geometry[1])

        window_information = applescript.AppleScript(f'''
            tell application "System Events" to tell window "{window_id[1]}" of process "{window_id[0]}"
                return get position
            end tell
        ''').run()

        geometry["x_offset"] = int(window_information[0])
        geometry["y_offset"] = int(window_information[1])

        return geometry
