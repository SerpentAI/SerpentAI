## 2021.4.0

* FIX - Locking keras version to 1.2.2 to avoid importation problems when using DQN and DDQN. All other algorithms(Random, Recorder, PPO and RainbowDQN) uses Pytorch which makes keras and tensorflow irrelevant.
* FIX - Offshoot now won't cause UnicodeDecodeError.
* FIX - Now win32gui will return the correct window size for an application
* FIX - RainbowDQN shall now correctly save and load input and weights in the appropriate device(CPU when using CPU, GPU when using GPU) instead of saving inputs in the CPU and weights in the GPU.
* IMPROVEMENT - RainbowDQN now allows for mouse inputs, including moving the cursor and clicking.

## 2018.1.2

* FEATURE - analytics client is now automatically initialized and in scope for a game agent
* FIX - analytics WAMP component now uses the analytics topic config key to determine redis key
* FIX - Locking Tensorflow to appropriate version on Windows

## 2018.1.1

* FIX - use interpolation order 0 in frame transformation pipeline resize
* FIX - use offshoot selection kwarg when discovering to avoid running code of all plugins
* FIX - sprite identifier needs to reject sprites that don't have the same shape as query sprite when using constellation of pixels
* FIX - mild attempt to shutdown frame grabber process on game agent exception

## 2018.1.0

Exiting Beta! Changed the versioning scheme to YEAR.QUARTER.RELEASE

* IMPROVEMENT - easier framework installation; only the core gets installed with `serpent setup`; other modules with more involved installation steps can be set up later as needed!
* IMPROVEMENT - added a `serpent update` command; headache-free framework updates
* IMPROVEMENT - added a `serpent modules` command to check the installation status of optional modules
* MAJOR FEATURE - cross-platform gameplay recording with ̀`serpent record`; capture keyboard/mouse inputs alongside frame buffers who are optionally put through a reward function; data is neatly packed in a single HDF5 file when done;
* FEATURE - a "force" kwarg can now be passed to input controller methods to ignore the game focus requirement
* FEATURE - context frame captures can now be scoped to game plugins' screen regions
* FEATURE - GameFrame objects now have a timestamp representing the capture time with microsecond precision
* FEATURE - GameFrame objects can now hold frame bytes (for PNG data) instead of a frame array
* FEATURE - FrameGrabber get_frames doesn't require shape and dtype information anymore
* FEATURE - added a mechanism to register custom reward functions in a GameAgent
* TWEAK - no longer halving width & height in context frame capture; frame transformation pipeline should be used instead
* TWEAK - files generated from any frame capture operation are now named with the timestamp instead of a random UUID4
* FIX - CNNInceptionV3Classifier can now also handle uint8 dtypes
* INTERNAL - reshape metadata and timestamp are now encoded alongside frame bytes; saving a ton of reshape preperation logic
* INTERNAL - added 'PNG' operator in frame transformation pipelines
* INTERNAL / REFACTOR - better OS abstractions to control platform-specific snippets
* NOTEBOOK - added a Jupyter Notebook to demonstrate common operations with the input recording HDF5 files

## 0.1.12b1

* FIX - inceptionv3 context classifier is now using the newer normalize function instead of the old scale_range one
* REFACTOR / FIX - added a mechanism to handle scancodes for extended keys in NativeWin32 input controller. Fixes arrow keys on Windows :)
* FIX - added a dtype kwarg to FrameGrabber get_frames. necessary when using 'FLOAT' pipeline operator

## 0.1.11b1

* FEATURE - added 'FLOAT' operator in frame transformation pipelines (needed for DQN)
* FEATURE - added 'SSIM' mode to sprite identifier
* FIX - sprite identifier score thresholds now work consistently with all offered modes
* FIX - resolved an issue with sprite identifier constellation of pixels mode and sprites with alpha channel
* FIX - added macOS command key to KeyboardKey enum and added a mapping for PyAutoGUI input controller backend
* FIX - linux window controller will now only consider visible windows when attempting to find game windows
* FEATURE - better range normalization in serpent.cv: ability to pass in target domain

## 0.1.10b1

* FEATURE - added frame transformation pipelines
* FIX - DQN and DDQN fixes and Windows compatibility tweaks

## 0.1.9b1

* FIX - emptied out __init__.py for serpent.input_controllers (AKA win32api trying to import on Linux)

## 0.1.8b1

* MAJOR CHANGE - added a KeyboardKey enum containing all valid keys that can be pressed on a standard keyboard; all InputController methods that accept keys now require KeyboardKey items
* FEATURE - added a fully-compliant native Windows input controller that uses the SendInput DLL function
* FEATURE - added 'move', 'click_down' & 'click_up' to the InputController protocol; implemented them in PYAUTOGUI & NATIVE_WIN32
* FEATURE - context classifier validation during training can now be skipped
* FEATURE - context classifier model checkpoints can now be autosaved
* FEATURE - locate() from the SpriteLocator can now use screen regions
* FIX - prevented an empty list to get to a min() call in locate_string

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
