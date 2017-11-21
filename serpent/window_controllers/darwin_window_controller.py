from serpent.window_controller import WindowController

import applescript


class DarwinWindowController(WindowController):

    def __init__(self):
        pass

    def locate_window(self, name):
        all_windows = applescript.AppleScript('''
            set visibleWindows to {}
            tell application "System Events"
                repeat with this_app in (get processes whose background only is false) --get applications with 1+ window
                    tell this_app
                        set p_name to name
                    end tell
                    repeat with this_window in (get windows of this_app)
                        tell this_window
                            set w_name to name
                        end tell
                        set end of visibleWindows to {p_name, w_name}
                    end repeat
                end repeat
            end tell
            return visibleWindows
        ''').run()
        for (p_name, w_name) in all_windows:
            if w_name == name:
                return (p_name, w_name)
        return ["", ""]

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
        return self.get_focused_window_name() == window_id[1]

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

        return focused_window_name[1]

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
