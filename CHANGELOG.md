## 0.1.7b1

* FIX - macOS frame reshape error should be resolved; Including the top bar as part of the capture until someone can a programmatic way to get the inner window size.
* FEATURE - added a Web Browser GameLauncher for people who want to tackle web games
* FIX - Added a default static seed to the the training of the context classifier dataset split operation

## 0.1.6b1

* REFACTOR - InputController now pivots on a backend to allow extension; PyAutoGUI extracted to a backend (default)
* FIX - no CUDA initialization unless it's actually needed
* FEATURE - new `serpent window_name` command to assist in finding the proper kwargs["window_name"] for Game plugins
* FIX - stopped initializing a VisualDebugger instance on every new GameFrameBuffer. Huge performance gain in frame consumption rate.

## 0.1.5b1

* FIX - DarwinWindowController is_window_focused should use process title and not name

## 0.1.4b1

* FIX - initial applescript to find focused windows was fine but macOS users need to use process name and not the window name

## 0.1.3b1

* FEATURE - added resize_window to all WindowController classes
* TWEAK - Base Game Agent GameFrameLimiter FPS to 30

## 0.1.2b1

* FEATURE - retina display detection and handling on macOS
* FIX - most mouse events were missing the window geometry offsets
* FIX - replaced the applescript used to determine the focused window so the visible title bar name can be used in all cases

## 0.1.1b1

* FIX - conda not found on Windows serpent setup
* FIX - version locked Cython to version 0.26.1 because Kivy doesn't build on 0.27

## 0.1.0b1

* Initial Beta Release