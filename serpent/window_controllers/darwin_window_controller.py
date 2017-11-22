from serpent.window_controller import WindowController

import re
import applescript


class DarwinWindowController(WindowController):

    def __init__(self):
        pass

    def locate_window(self, name):
        all_windows = applescript.AppleScript('''
            set visibleWindows to {}
            tell application "System Events"
                repeat with this_app in (get processes whose background only is false) --get applications with 1+ window
                    set end of visibleWindows to { (name of this_app), (get name of every window of this_app) }
                end repeat
            end tell
            return visibleWindows
        ''').run()
        for p_name, windows in all_windows:
            for i, w_name in enumerate(windows):
                if re.search(".*" + name + ".*", w_name):
                    return (p_name, i + 1) # Windows are ordered by order of creations, it's a value that is fixed for the duration of the window's life
        # If we didn't found the window, we fallback by testing if name is a process name
        return [name, 1]

    def move_window(self, window_id, x, y):
        applescript.AppleScript(f'''
            tell application "System Events" to tell window {window_id[1]} of process "{window_id[0]}"
                set position to { {x}, {y} }
            end tell
        ''').run()

    def resize_window(self, window_id, width, height):
        applescript.AppleScript(f'''
            tell application "System Events" to tell window {window_id[1]} of process "{window_id[0]}"
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
        return window_id[0] == self.get_focused_window_name()

    def get_focused_window_name(self):
        focused_window_name = applescript.AppleScript('''
            set windowTitle to ""
            tell application "System Events"
                set frontApp to first application process whose frontmost is true
                set frontAppName to name of frontApp
                tell process frontAppName
                    tell (1st window whose value of attribute "AXMain" is true)
                        set windowTitle to value of attribute "AXTitle"
                    end tell
                end tell
            end tell

            return {frontAppName, windowTitle}
        ''').run()

        return focused_window_name[0]

    def get_window_geometry(self, window_id):
        geometry = dict()

        window_geometry = applescript.AppleScript(f'''
            tell application "System Events" to tell process "{window_id[0]}"
                return get size of window {window_id[1]}
            end tell
        ''').run()

        geometry["width"] = int(window_geometry[0])
        geometry["height"] = int(window_geometry[1])

        window_information = applescript.AppleScript(f'''
            tell application "System Events" to tell window {window_id[1]} of process "{window_id[0]}"
                return get position
            end tell
        ''').run()

        geometry["x_offset"] = int(window_information[0])
        geometry["y_offset"] = int(window_information[1])

        return geometry
