#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
The CEFBrowser Widget actually displays the browser. It displays ONLY the
browser. If you need controls or tabs, check out the `examples`
"""

import ctypes
from functools import partial
import json
import os
import random
import time

from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.graphics.texture import Texture
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import StringProperty
from kivy.properties import NumericProperty
from kivy.properties import BooleanProperty
from kivy.properties import ReferenceListProperty
from kivy import resources
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.bubble import Bubble, BubbleButton
from kivy.uix.widget import Widget

from .cefpython import cefpython, cefpython_initialize
from .cefkeyboard import CEFKeyboardManager


class CEFAlreadyInitialized(Exception):
    pass


class CEFBrowser(Widget, FocusBehavior):
    """Displays a Browser"""
    # Class Variables
    certificate_error_handler = None
    """The value of the `certificate_error_handler` class variable is a
    function that handles certificate errors.
    It takes 2 arguments:
    - `err`: The certificate error number that occurred
    - `url`: The URL that was to be loaded
    It should return a bool that indicates whether to ignore the error or not:
    - True: Ignore warning - False: Abort loading
    If `certificate_error_handler` is None or cannot be executed, the default
    is False."""
    _cefpython_initialized = False
    _flags = {}
    """Flags for CEFBrowser"""
    _command_line_switches = {
        "ppapi-flash-path":
            "/opt/google/chrome/PepperFlash/libpepflashplayer.so",
        "disable-gpu-compositing": ""}
    """Command line switches for cefpython"""
    _settings = {}
    """Settings for cefpython"""
    _caches_path = None
    _cookies_path = None
    _logs_path = None
    _cookie_manager = None

    # Instance Variables
    url = StringProperty("")
    """The URL of the (main frame of the) browser."""
    is_loading = BooleanProperty(False)
    """Whether the browser is loading content"""
    can_go_back = BooleanProperty(False)
    """Whether the browser gan go back in history at this time"""
    can_go_forward = BooleanProperty(False)
    """Whether the browser gan go forward in history at this time"""
    title = StringProperty("")
    """The title of the currently displayed content
    (e.g. for tab/window title)"""
    popup_policy = None
    """The value of the `popup_policy` variable is a function that handles
    the policy whether to allow or block popups.
    It takes 2 arguments:
    - `browser`: The browser which wants to open the popup
    - `url`: The URL of the (future) popup
    It should return a bool that indicates whether to open the popup or not:
    - True: Allow popup - False: Block popup
    If `popup_policy` is None or cannot be executed, the default is False."""
    popup_handler = None
    """The value of the `popup_handler` variable is a function that handles
    newly created popups.
    It takes 2 arguments:
    - `browser`: The browser which opened the popup
    - `popup_browser`: The (newly created) popup browser
    It should place the `popup_browser` somewhere in the widget tree
    If `popup_handler` is None, cannot be executed or doesn't insert
    `popup_browser` to the widget tree, the default is to add it to the Window.
    """
    close_handler = None
    """The value of the `close_handler` variable is a function that handles
    closing browsers or popups.
    It takes 1 argumeSetAsChildnt:
    - `browser`: The browser to be closed
    It remove everything belonging to `browser` from the widget tree
    If `close_handler` is None, cannot be executed or doesn't remove `browser`
    from the widget tree, the default is to just remove the `browser` from its
    parent."""
    keyboard_position = None
    """The value of the `keyboard_position` variable is a function that handles
    positioning of the keyboard on focusing a keyboard element in the browser.
    It takes 1 argument:
    - `browser`: The browser in which the element was focused
    - `keyboard_widget`: The keyboard widget
    - `rect`: The rectangle the focused element takes *within* the browser
    - `attributes`: The HTML attributes of the focused element
    It should set `keyboard_widget.pos` to the desired value
    If `close_handler` is None, cannot be executed or doesn't remove `browser`
    from the widget tree, the default is to just leave the keyboard widget
    where it is."""
    _touches = []
    _browser = None
    _popup = None
    _texture = None

    def __init__(self, url="", *largs, **dargs):
        self.url = url
        self.popup_policy = dargs.pop(
            "popup_policy", CEFBrowser.always_block_popups)
        self.popup_handler = dargs.pop(
            "popup_handler", CEFBrowser.fullscreen_popup)
        self.close_handler = dargs.pop(
            "close_handler", CEFBrowser.do_nothing)
        self.keyboard_position = dargs.pop(
            "keyboard_position", CEFBrowser.keyboard_position_optimal)
        self._browser = dargs.pop("browser", None)
        self._popup = CEFBrowserPopup(self)
        self._selection_bubble = CEFBrowserCutCopyPasteBubble(self)
        self.__rect = None
        self.__keyboard_state = {}
        self.js = CEFBrowserJSProxy(self)

        super(CEFBrowser, self).__init__(**dargs)

        self.register_event_type("on_load_start")
        self.register_event_type("on_load_end")
        self.register_event_type("on_load_error")
        self.register_event_type("on_js_dialog")
        self.register_event_type("on_before_unload_dialog")

        self._texture = Texture.create(
            size=self.size, colorfmt="rgba", bufferfmt="ubyte")
        self._texture.flip_vertical()
        with self.canvas:
            Color(1, 1, 1)
            self.__rect = Rectangle(
                pos=self.pos, size=self.size, texture=self._texture)

        if not CEFBrowser._cefpython_initialized:
            cefpython_initialize(CEFBrowser)
            CEFBrowser._cefpython_initialized = True
        if not self._browser:
            # On x11 input provider we have the window-id (handle)
            window_id = 0
            try:
                from kivy.core.window import Window as KivyWindow
                window_id = KivyWindow.window_id
            except Exception as e:
                Logger.debug("Use window handle %s, because: %s", window_id, e)
            window_info = cefpython.WindowInfo()
            window_info.SetAsOffscreen(window_id)
            window_info.SetTransparentPainting(True)

            self._browser = cefpython.CreateBrowserSync(
                window_info,
                {"windowless_frame_rate": 60},
                navigateUrl=self.url,
            )
        self._browser.SetClientHandler(client_handler)
        client_handler.browser_widgets[self._browser] = self
        self._browser.WasResized()
        self.bind(size=self._realign)
        self.bind(pos=self._realign)
        self.bind(parent=self._on_parent)
        self.bind(focus=self._on_focus)
        self.html5_drag_representation = Factory.HTML5DragIcon()
        self.js._inject()

        Window.bind(mouse_pos=self.on_mouse_pos)

    @classmethod
    def update_flags(cls, d):
        """ Updates the flags for CEFBrowser with the options given in the dict `d`.
        For possible keys and values, see the docs."""
        CEFBrowser._flags.update(d)

    @classmethod
    def update_command_line_switches(cls, d):
        """ Updates the command line switches for cefpython with the options
        given in the dict `d`.
        For possible keys and values, see the cefpython docs."""
        if CEFBrowser._cefpython_initialized:
            raise CEFAlreadyInitialized()
        CEFBrowser._command_line_switches.update(d)
        Logger.debug(
            "CEFBrowser: update_command_line_switches => %s",
            CEFBrowser._command_line_switches,
        )
        # print("update_command_line_switches", cls._command_line_switches)

    @classmethod
    def update_settings(cls, d):
        """ Updates the settings for cefpython with the options given in the dict `d`.
        For possible keys and values, see the cefpython docs."""
        if CEFBrowser._cefpython_initialized:
            raise CEFAlreadyInitialized()
        CEFBrowser._settings.update(d)
        Logger.debug("CEFBrowser: update_settings => %s", CEFBrowser._settings)

    @classmethod
    def set_caches_path(cls, cp):
        """ The string `cp` is the path to a read- and writeable location
        where CEF can store its run-time caches."""
        if CEFBrowser._cefpython_initialized:
            raise CEFAlreadyInitialized()
        CEFBrowser._caches_path = cp
        Logger.debug(
            "CEFBrowser: caches_path: %s\n cookies_path: %s\n logs_path: %s",
            CEFBrowser._caches_path,
            CEFBrowser._cookies_path,
            CEFBrowser._logs_path,
        )

    @classmethod
    def set_cookies_path(cls, cp):
        """ The string `cp` is the path to a read- and writeable location
        where CEF can store its run-time cookies."""
        if CEFBrowser._cefpython_initialized:
            raise CEFAlreadyInitialized()
        CEFBrowser._cookies_path = cp
        Logger.debug(
            "CEFBrowser: caches_path: %s\n cookies_path: %s\n logs_path: %s",
            CEFBrowser._caches_path,
            CEFBrowser._cookies_path,
            CEFBrowser._logs_path,
        )

    @classmethod
    def set_logs_path(cls, lp):
        """ The string `lp` is the path to a read- and writeable location
        where CEF can write its log."""
        if CEFBrowser._cefpython_initialized:
            raise CEFAlreadyInitialized()
        CEFBrowser._logs_path = lp
        Logger.debug(
            "CEFBrowser: caches_path: %s\n cookies_path: %s\n logs_path: %s",
            CEFBrowser._caches_path,
            CEFBrowser._cookies_path,
            CEFBrowser._logs_path,
        )

    @classmethod
    def set_data_path(cls, dp):
        """ The string `dp` class variable is the path to a read- and
        writeable location where CEF can write its run-time data:
        - caches to '`dp`/cache'
        - cookies to '`dp`/cookies'
        - logs to '`dp`/logs'
        """
        if CEFBrowser._cefpython_initialized:
            raise CEFAlreadyInitialized()
        if not os.path.isdir(dp):
            os.mkdir(dp, 0o700)
        CEFBrowser._caches_path = os.path.join(dp, "caches")
        CEFBrowser._cookies_path = os.path.join(dp, "cookies")
        CEFBrowser._logs_path = os.path.join(dp, "logs")
        Logger.debug(
            "CEFBrowser: \ncaches_path: %s\n cookies_path: %s\n logs_path: %s",
            CEFBrowser._caches_path,
            CEFBrowser._cookies_path,
            CEFBrowser._logs_path,
        )

    def _realign(self, *largs):
        ts = self._texture.size
        ss = self.size
        schg = (ts[0] != ss[0] or ts[1] != ss[1])
        if schg:
            self._texture = Texture.create(
                size=self.size, colorfmt="rgba", bufferfmt="ubyte")
            self._texture.flip_vertical()
        if self.__rect:
            with self.canvas:
                Color(1, 1, 1)
                self.__rect.pos = self.pos
                if schg:
                    self.__rect.size = self.size
            if schg:
                self._update_rect()
        if self._browser:
            self._browser.WasResized()
            self._browser.NotifyScreenInfoChanged()
        try:
            self._keyboard_update(**self.__keyboard_state)
        except:
            pass

    def _on_parent(self, obj, parent):
        self._browser.WasHidden(not parent)  # optimize the shit out of CEF
        try:
            self._keyboard_update(**self.__keyboard_state)
        except:
            pass

    def _on_focus(self, obj, focus):
        super(CEFBrowser, self)._on_focus(obj, focus)
        if not focus and self.__keyboard_state["shown"]:
            self._browser.GetMainFrame().ExecuteJavascript(
                "__kivy__activeKeyboardElement.blur();")

    def _update_rect(self):
        if self.__rect:
            self.__rect.texture = self._texture

    def go_back(self):
        self._browser.GoBack()

    def go_forward(self):
        self._browser.GoForward()

    def stop_loading(self):
        self._browser.StopLoad()

    def reload(self, ignore_cache=True):
        if ignore_cache:
            self._browser.ReloadIgnoreCache()
        else:
            self._browser.Reload()

    def delete_cookie(self, url=""):
        """ Deletes the cookie with the given url. If url is empty all cookies
        get deleted.
        """
        cookie_manager = cefpython.CookieManager.GetGlobalManager()
        if cookie_manager:
            cookie_manager.DeleteCookies(url, "")
        else:
            Logger.warning("No cookie manager found!, Can't delete cookie(s)")

    def on_url(self, instance, value):
        if self._browser and value and value != self._browser.GetUrl():
            # print(
            #     "ON URL",
            #     instance,
            #     value,
            #     self._browser.GetUrl(),
            #     self._browser.GetMainFrame().GetUrl(),
            # )
            self._browser.Navigate(self.url)

    def on_js_dialog(
        self,
        browser,
        origin_url,
        accept_lang,
        dialog_type,
        message_text,
        default_prompt_text,
        callback,
        suppress_message,
    ):
        pass

    def on_before_unload_dialog(
        self,
        browser,
        message_text,
        is_reload,
        callback,
    ):
        pass

    def on_load_start(self, frame):
        pass

    def on_load_end(self, frame, http_status_code):
        pass

    def on_load_error(self, frame, error_code, error_text, failed_url):
        Logger.error(
            "on_load_error=> Code: %s, error_text: %s, failedURL: %s",
            error_code,
            error_text,
            failed_url,
        )
        pass

    def _keyboard_update(self, shown, rect, attributes):
        """
        :param shown: Show keyboard if true, hide if false (blur)
        :param rect: [x,y,width,height] of the input element
        :param attributes: Attributes of HTML element
        """
        self.__keyboard_state = {
            "shown": shown,
            "rect": rect,
            "attributes": attributes,
        }
        # print("KB", self.url, self.__keyboard_state, self.parent)
        if shown and self.parent:  # No orphaned keyboards
            self.focus = True
            self.keyboard_position(
                self, self.keyboard.widget, rect, attributes)
        else:
            self.focus = False
        # CEFKeyboardManager.reset_all_modifiers() # TODO: necessary?

    @classmethod
    def keyboard_position_simple(
        cls,
        browser,
        keyboard_widget,
        rect,
        attributes,
    ):
        if not keyboard_widget.docked:
            if rect and len(rect) == 4:
                keyboard_widget.pos = (
                    browser.x + rect[0] +
                    (rect[2] - keyboard_widget.width) / 2,
                    browser.y + browser.height - rect[1] - rect[3] -
                    keyboard_widget.height,
                )
            else:
                keyboard_widget.pos = (browser.x, browser.y)

    @classmethod
    def keyboard_position_optimal(
        cls,
        browser,
        keyboard_widget,
        rect,
        attributes,
    ):  # TODO: place right, left, etc. see cefkivy
        if not keyboard_widget.docked:
            cls.keyboard_position_simple(
                browser, keyboard_widget, rect, attributes)
            if Window.width < keyboard_widget.x + keyboard_widget.width:
                keyboard_widget.x = Window.width - keyboard_widget.width
            if keyboard_widget.x < 0:
                keyboard_widget.x = 0
            if Window.height < keyboard_widget.y + keyboard_widget.height:
                keyboard_widget.y = Window.height - keyboard_widget.height
            if keyboard_widget.y < 0:
                keyboard_widget.y = 0

    @classmethod
    def always_allow_popups(cls, browser, url):
        return True

    @classmethod
    def always_block_popups(cls, browser, url):
        return True

    @classmethod
    def fullscreen_popup(cls, browser, popup_browser):
        Window.add_widget(popup_browser)

    @classmethod
    def do_nothing(cls, browser):
        pass

    @classmethod
    def allow_invalid_certificates(cls, browser, err, url):
        """
        `browser` is a dummy argument, because python treats class variables
        containing a function as unbound class methods
        """
        return True

    @classmethod
    def block_invalid_certificates(cls, browser, err, url):
        """
        `browser` is a dummy argument, because python treats class variables
        containing a function as unbound class methods
        """
        return False

    def keyboard_on_key_down(self, *largs):
        # print("KEY DOWN", largs)
        CEFKeyboardManager.kivy_on_key_down(self._browser, *largs)

    def keyboard_on_key_up(self, *largs):
        # print("KEY UP", largs)
        CEFKeyboardManager.kivy_on_key_up(self._browser, *largs)

    def keyboard_on_textinput(self, window, text):
        CEFKeyboardManager.kivy_keyboard_on_textinput(self._browser,
                                                      window, text)

    is_html5_drag = False  # Indicates if a html5 drag is happening
    is_html5_drag_leave = False  # Mouse leaves web view
    html5_drag_data = None
    current_html5_drag_operation = cefpython.DRAG_OPERATION_NONE

    def on_mouse_pos(self, window, position):
        if not len(self._touches):
            self.cef_mouse_move(int(position[0]), self.height - int(position[1]), mouse_leave=False, modifiers=0)

    def on_touch_down(self, touch, *kwargs):
        if not self.collide_point(*touch.pos):
            return

        # Do not support more than two touches!
        if len(self._touches) > 2:
            return

        touch.is_dragging = False
        touch.is_scrolling = False
        touch.is_right_click = False
        self._touches.append(touch)
        touch.grab(self)

        return True

    def on_touch_move(self, touch, *kwargs):
        if touch.grab_current is not self:
            return

        x = touch.x - self.pos[0]
        y = self.height-touch.y + self.pos[1]

        x_start = touch.opos[0] - self.pos[0]
        y_start = self.height-touch.opos[1] + self.pos[1]

        if len(self._touches) == 1:
            if not touch.is_scrolling or touch.is_right_click:
                # Dragging: Differ between HTML5 drag and normal drag
                if self.is_html5_drag:
                    if self.is_inside_window(touch.x, touch.y):
                        modifiers = cefpython.EVENTFLAG_LEFT_MOUSE_BUTTON
                        self.cef_mouse_move(x, y, mouse_leave=False,
                                            modifiers=modifiers)
                        if self.is_html5_drag_leave:
                            self.cef_drag_target_enter(
                                self.html5_drag_data, x, y,
                                cefpython.DRAG_OPERATION_EVERY)
                            self.is_html5_drag_leave = False
                        self.cef_drag_target_drag_over(
                            x, y, cefpython.DRAG_OPERATION_EVERY)
                        self.update_drag_representation(touch.x, touch.y)
                    else:
                        if not self.is_html5_drag_leave:
                            self.is_html5_drag_leave = True
                            self.cef_drag_target_drag_leave()
                else:
                    if (
                        (abs(touch.dx) > 5 or abs(touch.dy) > 5) or
                        touch.is_dragging
                    ):
                        if touch.is_dragging:
                            modifiers = cefpython.EVENTFLAG_LEFT_MOUSE_BUTTON
                            self.cef_mouse_move(
                                x, y, mouse_leave=False,
                                modifiers=modifiers,
                            )
                        else:
                            self.cef_mouse_click(
                                x_start, y_start, cefpython.MOUSEBUTTON_LEFT,
                                mouse_up=False, click_count=1,
                            )
                            touch.is_dragging = True
        elif len(self._touches) == 2:
            # Scroll only if a minimal distance passed (could be right click)
            touch1, touch2 = self._touches[:2]
            dx = touch2.dx / 2. + touch1.dx / 2.
            dy = touch2.dy / 2. + touch1.dy / 2.
            if (abs(dx) > 5 or abs(dy) > 5) or touch.is_scrolling:
                # Check all touches for a certain state
                for _touch in self._touches:
                    if _touch.is_dragging:
                        # End the drag event by releasing the mouse button
                        self.cef_mouse_click(
                            _touch.ppos[0], _touch.ppos[1],
                            cefpython.MOUSEBUTTON_LEFT, mouse_up=True,
                            click_count=1,
                        )
                        _touch.is_dragging = False
                    # Set touch state to scrolling
                    _touch.is_scrolling = True
                self.cef_mouse_wheel(
                    touch.x, self.height-touch.pos[1], dx, -dy,
                )
        return True

    def on_touch_up(self, touch, *kwargs):
        if touch.grab_current is not self:
            return

        y = self.height-touch.pos[1] + self.pos[1]
        x = touch.x - self.pos[0]

        if self.is_html5_drag:
            if (
                self.is_html5_drag_leave or
                not self.is_inside_window(touch.x, touch.y)
            ):
                # See comment in is_inside_web_view() - x/y at borders
                # should be treated as outside of web view.
                x = touch.x
                if x == 0:
                    x = -1
                if x == self.width-1:
                    x = self.width
                if y == 0:
                    y = -1
                if y == self.height-1:
                    y = self.height
                self.cef_drag_source_ended_at(x, y,
                                              self.current_drag_operation)
                self.drag_ended()
            else:
                self.cef_drag_target_drop(touch.x, y)
                self.cef_drag_source_ended_at(touch.x, y,
                                              self.current_drag_operation)
                self.drag_ended()

        else:
            if len(self._touches) == 2:
                if not touch.is_scrolling:
                    # Right click (mouse down, mouse up)
                    self._touches[0].is_right_click = True
                    self._touches[1].is_right_click = True
                    self.cef_mouse_click(
                        x, y, cefpython.MOUSEBUTTON_RIGHT,
                        mouse_up=False, click_count=1,
                    )
                    self.cef_mouse_click(
                        x, y, cefpython.MOUSEBUTTON_RIGHT,
                        mouse_up=True, click_count=1,
                    )
            else:
                if touch.is_dragging:
                    # Drag end (mouse up)
                    self.cef_mouse_click(
                        touch.ppos[0], self.height-touch.ppos[1] + self.pos[1],
                        cefpython.MOUSEBUTTON_LEFT,
                        mouse_up=True, click_count=1,
                    )
                elif not touch.is_right_click and not touch.is_scrolling:
                    # Left click (mouse down, mouse up)
                    count = 1
                    if touch.is_double_tap:
                        count = 2
                    self.cef_mouse_click(
                        x, y,
                        cefpython.MOUSEBUTTON_LEFT,
                        mouse_up=False, click_count=count,
                    )
                    self.cef_mouse_click(
                        x, y,
                        cefpython.MOUSEBUTTON_LEFT,
                        mouse_up=True, click_count=count,
                    )

        self._touches.remove(touch)
        touch.ungrab(self)
        return True

    def cef_mouse_click(self, x, y, modifier, mouse_up, click_count):
        """ We do not call the functions of cefpython browser directly.
        This way we can overwrite this (cef_mouse_click) function to bind
        further actions (e.g. when a mouse click happens) in applications which
        use cefbrowser / garden.cefpython as a module.
        """
        self._browser.SendMouseClickEvent(
            x, y, modifier, mouseUp=mouse_up, clickCount=click_count)

    def cef_mouse_move(self, x, y, mouse_leave, modifiers):
        """ See cef_mouse_click """
        self._browser.SendMouseMoveEvent(x, y, mouseLeave=mouse_leave,
                                         modifiers=modifiers)

    def cef_mouse_wheel(self, x, y, dx, dy):
        """ See cef_mouse_click """
        self._browser.SendMouseWheelEvent(x, y, dx, dy)

    def cef_drag_target_enter(self, drag_data, x, y, operation):
        """ See cef_mouse_click """
        self._browser.DragTargetDragEnter(drag_data, x, y,
                                          operation)

    def cef_drag_target_drag_over(self, x, y, operation):
        """ See cef_mouse_click """
        self._browser.DragTargetDragOver(x, y, operation)

    def cef_drag_target_drag_leave(self):
        """ See cef_mouse_click """
        self._browser.DragTargetDragLeave()

    def cef_drag_target_drop(self, x, y):
        """ See cef_mouse_click """
        self._browser.DragTargetDrop(x, y)

    def cef_drag_source_ended_at(self, x, y, operation):
        """ See cef_mouse_click """
        self._browser.DragSourceEndedAt(x, y, operation)

    def cef_drag_source_system_drag_ended(self):
        """ See cef_mouse_click """
        self._browser.DragSourceSystemDragEnded()

    def is_inside_window(self, x, y):
        # When mouse is out of app window Kivy still generates move events
        # at the borders with x=0, x=width-1, y=0, y=height-1.
        if (0 < x < Window.width-1) and (0 < y < Window.height-1):
            return True
        return False

    def update_drag_representation(self, x, y):
        """ Displays the representation of the drag under the touch.
        """
        if self.is_html5_drag:
            if self.html5_drag_representation not in self.children:
                image = self.html5_drag_data.GetImage()
                width = image.GetWidth()
                height = image.GetHeight()
                abuffer = image.GetAsBitmap(
                    1.0,
                    cefpython.CEF_COLOR_TYPE_BGRA_8888,
                    cefpython.CEF_ALPHA_TYPE_PREMULTIPLIED)
                texture = Texture.create(size=(width, height))
                texture.blit_buffer(abuffer, colorfmt='bgra',
                                    bufferfmt='ubyte')
                texture.flip_vertical()
                self.html5_drag_representation.size = (width, height)
                self.html5_drag_representation.texture = texture
                self.add_widget(self.html5_drag_representation)
            self.html5_drag_representation.center = (x, y)
        else:
            self.remove_widget(self.html5_drag_representation)

    def drag_ended(self):
        self.is_html5_drag = False
        self.is_html5_drag_leave = False
        self.current_html5_drag_operation = cefpython.DRAG_OPERATION_NONE
        self.update_drag_representation(None, None)
        self.cef_drag_source_system_drag_ended()


class CEFBrowserPopup(Widget):
    rx = NumericProperty(0)
    ry = NumericProperty(0)
    rpos = ReferenceListProperty(rx, ry)

    def __init__(self, browser_widget, *largs, **dargs):
        super(CEFBrowserPopup, self).__init__()
        self.browser_widget = browser_widget
        self.__rect = None
        self._texture = Texture.create(
            size=self.size, colorfmt="rgba", bufferfmt="ubyte")
        self._texture.flip_vertical()
        with self.canvas:
            Color(1, 1, 1)
            self.__rect = Rectangle(
                pos=self.pos, size=self.size, texture=self._texture)
        self.bind(rpos=self._realign)
        self.bind(size=self._realign)
        browser_widget.bind(pos=self._realign)
        browser_widget.bind(size=self._realign)

    def _realign(self, *largs):
        self.x = self.rx + self.browser_widget.x
        self.y = self.browser_widget.height - self.ry - self.height + \
            self.browser_widget.y
        ts = self._texture.size
        ss = self.size
        schg = (ts[0] != ss[0] or ts[1] != ss[1])
        if schg:
            self._texture = Texture.create(
                size=self.size, colorfmt="rgba", bufferfmt="ubyte")
            self._texture.flip_vertical()
        if self.__rect:
            with self.canvas:
                Color(1, 1, 1)
                self.__rect.pos = self.pos
                if schg:
                    self.__rect.size = self.size
            if schg:
                self._update_rect()

    def _update_rect(self):
        if self.__rect:
            self.__rect.texture = self._texture


class CEFBrowserJSFunctionProxy:
    def __init__(self, browser_widget, key, *largs):
        self.browser_widget = browser_widget
        self.key = key

    def __call__(self, *largs):
        js_code = str(self.key)+"("
        first = True
        for arg in largs:
            if not first:
                js_code += ", "
            js_code += json.dumps(arg)
            first = False
        js_code += ");"
        frame = self.browser_widget._browser.GetMainFrame()
        frame.ExecuteJavascript(js_code)


class CEFBrowserJSProxy:
    def __init__(self, browser_widget, *largs):
        self.browser_widget = browser_widget
        self.__js_bindings_dict = {
            "__kivy__keyboard_update":
                browser_widget._keyboard_update,
            "__kivy__selection_update":
                browser_widget._selection_bubble._update,
        }
        self.__js_bindings = None

    def _inject(self):
        # When browser.Navigate() is called, some bug appears in CEF
        # that makes CefRenderProcessHandler::OnBrowserDestroyed()
        # is being called. This destroys the javascript bindings in
        # the Render process. We have to make the js bindings again,
        # after the call to Navigate() when OnLoadingStateChange()
        # is called with isLoading=False. Problem reported here:
        # http://www.magpcss.org/ceforum/viewtopic.php?f=6&t=11009
        if not self.__js_bindings:
            self.__js_bindings = cefpython.JavascriptBindings(
                bindToFrames=True, bindToPopups=True)
            for k in self.__js_bindings_dict:
                self.__js_bindings.SetFunction(k, self.__js_bindings_dict[k])
            self.browser_widget._browser.SetJavascriptBindings(
                self.__js_bindings)
        else:
            self.__js_bindings.Rebind()

    def bind(self, **dargs):
        self.__js_bindings_dict.update(dargs)
        self.__js_bindings = None
        self._inject()

    def __getattr__(self, key):
        return CEFBrowserJSFunctionProxy(self.browser_widget, key)


class CEFBrowserCutCopyPasteBubble(Bubble):
    def __init__(self, browser_widget, *largs, **dargs):
        super(CEFBrowserCutCopyPasteBubble, self).__init__(**dargs)
        self.browser_widget = browser_widget
        self.size_hint = (None, None)
        self.size = (160, 80)
        self.cutbut = BubbleButton(text="Cut")
        self.cutbut.bind(on_press=self.on_cut)
        self.add_widget(self.cutbut)
        self.copybut = BubbleButton(text="Copy")
        self.copybut.bind(on_press=self.on_copy)
        self.add_widget(self.copybut)
        self.pastebut = BubbleButton(text="Paste")
        self.pastebut.bind(on_press=self.on_paste)
        self.add_widget(self.pastebut)
        self._options = {}
        self._rect = [0, 0, 0, 0]
        self._text = ""

    def _update(self, options, rect, text):
        """
        :param options: dict with keys `shown`, `can_cut`, `can_copy`,
            `can_paste`
        :param rect: [x,y,width,height] of the selection
        :param text: Text representation of selection content
        """
        if 'enable-copy-paste' not in CEFBrowser._flags:
            return
        # print(
        #     "SEL",
        #     self.browser_widget.url,
        #     options,
        #     rect,
        #     text,
        #     self.browser_widget.parent,
        # )
        if not self.browser_widget.parent:
            options["shown"] = False
        self.pos = (
            self.browser_widget.x + rect[0] + (rect[2] - self.width) / 2,
            self.browser_widget.y + self.browser_widget.height - rect[1],
        )
        shown = ("shown" in options and options["shown"])
        if shown and not self.parent:
            Window.add_widget(self)
        if not shown and self.parent:
            Window.remove_widget(self)
        self.cutbut.disabled = not (
            "can_cut" in options and options["can_cut"])
        self.copybut.disabled = not (
            "can_copy" in options and options["can_copy"])
        self.pastebut.disabled = not (
            "can_paste" in options and options["can_paste"])
        self._options = options
        self._rect = rect
        self._text = text

    def on_cut(self, *largs):
        print("CUT", largs, self._text)
        self.on_copy()

    def on_copy(self, *largs):
        Clipboard.put(self._text, "UTF8_STRING")
        Clipboard.put(self._text, "TEXT")
        Clipboard.put(self._text, "STRING")
        Clipboard.put(self._text, "text/plain")

    def on_paste(self, *largs):
        t = False
        for type in Clipboard.get_types():
            if type in ("UTF8_STRING", "TEXT", "STRING", "text/plain"):
                try:
                    t = Clipboard.get(type)
                    break
                except:
                    pass
        print("PASTE", t)


class ClientHandler:
    browser_widgets = {}
    pending_popups = {}

    def __init__(self, *largs):
        self.browser_widgets = {}

    # DisplayHandler TODO: OnContentsSizeChange, OnFaviconURLChange,
    # OnNavStateChange

    def OnAddressChange(self, browser, frame, url):  # noqa: N802
        if browser.GetMainFrame() == frame:
            self.browser_widgets[browser].url = url
        else:
            pass
            # print("TODO: Address changed in Frame")

    def OnTitleChange(self, browser, title):  # noqa: N802
        self.browser_widgets[browser].title = title

    def OnTooltip(self, text_out):  # noqa: N802
        text_out.append("")
        return True

    def OnStatusMessage(self, browser, value):  # noqa: N802
        Logger.info("CEFBrowser: Status: %s", value)

    def OnConsoleMessage(self, browser, message, source, line):  # noqa: N802
        Logger.info("CEFBrowser: Console: %s - %s(%i)", message, source, line)
        return True  # We handled it

    # DownloadHandler

    # FocusHandler

    def OnTakeFocus(self, browser, next_component):  # noqa: N802
        pass

    def OnSetFocus(self, browser, source):  # noqa: N802
        pass

    def OnGotFocus(self, browser):  # noqa: N802
        pass

    # JavascriptDialogHandler
    active_js_dialog = None

    def _js_continue(self, callback, allow, user_input):
        self._active_js_dialog = None
        callback.Continue(allow, user_input)

    def OnJavascriptDialog(  # noqa: N802
        self,
        browser,
        origin_url,
        dialog_type,
        message_text,
        default_prompt_text,
        callback,
        suppress_message_out,
    ):
        dialog_types = {
            cefpython.JSDIALOGTYPE_ALERT:
                ["alert", CEFBrowser._js_alert],
            cefpython.JSDIALOGTYPE_CONFIRM:
                ["confirm", CEFBrowser._js_confirm],
            cefpython.JSDIALOGTYPE_PROMPT:
                ["prompt", CEFBrowser._js_prompt],
        }
        # print(
        #     "OnJavascriptDialog",
        #     browser,
        #     origin_url,
        #     accept_lang,
        #     dialog_types[dialog_type][0],
        #     message_text,
        #     default_prompt_text,
        #     callback,
        #     suppress_message,
        #     largs,
        # )
        p = dialog_types[dialog_type][1]
        p.text = message_text
        p.js_continue = partial(self._js_continue, callback)
        p.default_prompt_text = default_prompt_text
        p.open()
        self.active_js_dialog = p
        return True

    def OnBeforeUnloadJavascriptDialog(  # noqa: N802
        self,
        browser,
        message_text,
        is_reload,
        callback,
    ):
        p = CEFBrowser._js_confirm
        p.text = message_text
        p.js_continue = partial(self._js_continue, callback)
        p.default_prompt_text = ""
        p.open()
        self.active_js_dialog = p
        return True

    def OnResetJavascriptDialogState(self, browser):  # noqa: N802
        if self._active_js_dialog:
            self._active_js_dialog.dismiss()

    def OnJavascriptDialogClosed(self, browser):  # noqa: N802
        pass

    # KeyboardHandler

    def OnPreKeyEvent(  # noqa: N802
        self,
        browser,
        event,
        event_handle,
        is_keyboard_shortcut_out,
    ):
        return False

    def OnKeyEvent(self, browser, event, event_handle):  # noqa: N802
        return False

    # LifeSpanHandler

    def OnBeforePopup(  # noqa: N802
        self,
        browser,
        frame,
        target_url,
        target_frame_name,
        target_disposition,
        user_gesture,
        popup_features,
        window_info_out,
        client,
        browser_settings_out,
        no_javascript_access_out,
    ):
        Logger.debug("CEFBrowser: OnBeforePopup")
        Logger.debug("\tBrowser: %s", browser)
        Logger.debug("\tFrame: %s", frame)
        Logger.debug("\tURL: %s", target_url)
        Logger.debug("\tFrame Name: %s", target_frame_name)
        Logger.debug("\tPopup Features: %s", popup_features)
        Logger.debug("\tWindow Info: %s", window_info_out)
        Logger.debug("\tClient: %s", client)
        Logger.debug("\tBrowser Settings: %s", browser_settings_out)
        Logger.debug("\tNo JavaScript Access: %s", no_javascript_access_out)
        bw = self.browser_widgets[browser]
        if hasattr(bw.popup_policy, "__call__"):
            try:
                allow_popup = bw.popup_policy(bw, target_url)
                Logger.info(
                    "CEFBrowser: Popup policy handler " +
                    ("allowed" if allow_popup else "blocked") +
                    " popup",
                )
            except Exception as err:
                Logger.warning(
                    "CEFBrowser: Popup policy handler failed with error:", err)
                allow_popup = False
        else:
            Logger.info(
                "CEFBrowser: No Popup policy handler detected. " +
                "Default is block.",
            )
            allow_popup = False
        if allow_popup:
            r = random.randint(1, 2**31-1)
            wi = cefpython.WindowInfo()
            wi.SetAsChild(0, [0, 0, 0, 0])
            wi.SetAsOffscreen(r)
            window_info_out.append(wi)
            browser_settings_out.append({})
            self.pending_popups[r] = browser
            return False
        else:
            return True

    def _OnAfterCreated(self, browser):  # noqa: N802
        # print(
        #     "On After Created",
        #     browser,
        #     browser.IsPopup(),
        #     browser.GetIdentifier(),
        #     browser.GetWindowHandle(),
        #     browser.GetOpenerWindowHandle(),
        # )
        if browser.IsPopup():
            wh = browser.GetWindowHandle()
            cb = CEFBrowser(browser=browser)
            bw = False
            if wh in client_handler.pending_popups:
                parent_browser = client_handler.pending_popups[wh]
                if parent_browser in client_handler.browser_widgets:
                    bw = client_handler.browser_widgets[parent_browser]
            if not bw:
                bw = client_handler.browser_widgets[
                    client_handler.browser_widgets.iterkeys().next()]
            if hasattr(bw.popup_handler, "__call__"):
                try:
                    bw.popup_handler(bw, cb)
                except Exception as err:
                    Logger.warning(
                        "CEFBrowser: Popup handler failed with error: %s", err)
            else:
                Logger.info("CEFBrowser: No Popup handler detected.")
            if not cb.parent:
                Logger.warning(
                    "CEFBrowser: Popup handler did not add the " +
                    "popup_browser to the widget tree. Adding it to Window.",
                )
                Window.add_widget(cb)

    """
    def RunModal(self, browser, *largs):  # noqa: N802
        Logger.debug("CEFBrowser: RunModal")
        Logger.debug("\tBrowser: %s", browser)
        Logger.debug("\tRemaining Args: %s", largs)
        return False
    """
    def DoClose(self, browser):  # noqa: N802
        bw = self.browser_widgets[browser]
        bw.focus = False
        if bw._selection_bubble.parent:
            bw._selection_bubble.parent.remove_widget(bw._selection_bubble)
        if hasattr(bw.close_handler, "__call__"):
            try:
                bw.close_handler(bw)
            except Exception as err:
                Logger.warning(
                    "CEFBrowser: Close handler failed with error: %s", err)
        try:
            bw.parent.remove_widget(bw)
        except:
            pass
        del self.browser_widgets[browser]
        return False

    def OnBeforeClose(self, browser):  # noqa: N802
        Logger.info("On Before Close")

    # LoadHandler

    def OnLoadingStateChange(  # noqa: N802
        self,
        browser,
        is_loading,
        can_go_back,
        can_go_forward,
    ):
        bw = self.browser_widgets[browser]
        bw.is_loading = is_loading
        bw.can_go_back = can_go_back
        bw.can_go_forward = can_go_forward
        if not is_loading:
            bw.js._inject()

    def OnLoadStart(self, browser, frame):  # noqa: N802
        bw = self.browser_widgets[browser]
        bw.dispatch("on_load_start", frame)
        bw.focus = False
        if bw:
            bw._browser.SendFocusEvent(True)
            js_code = """

// Dirty Bugfixes

window.print = function () {
    console.log("Print dialog blocked");
};

window.addEventListener('load', function () {
    document.querySelectorAll('input[type=file]').forEach(function (elem) {
        elem.onclick = function () {
            return false;
        }
    });
});


// Keyboard management

var __kivy__activeKeyboardElement = false;
var __kivy__activeKeyboardElementSince = false;
var __kivy__activeKeyboardElementSelection = false;
var __kivy__updateRectTimer = false;
var __kivy__lastRect = [];

function __kivy__isKeyboardElement(elem) {
    try {
        var tag = elem.tagName.toUpperCase();
        if (tag=="INPUT") return (["TEXT", "PASSWORD", "DATE", "DATETIME", \
            "DATETIME-LOCAL", "EMAIL", "MONTH", "NUMBER", "SEARCH", "TEL", \
            "TIME", "URL", "WEEK"\
        ].indexOf(elem.type.toUpperCase())!=-1);
        else if (tag=="TEXTAREA") return true;
        else {
            var tmp = elem;
            while (tmp && tmp.contentEditable=="inherit") {
                tmp = tmp.parentElement;
            }
            if (tmp && tmp.contentEditable) return true;
        }
    } catch (err) {}
    return false;
}

function __kivy__getAttributes(elem) {
    var attributes = {};
    var atts = elem.attributes;
    if (atts) {
        var n = atts.length;
        for (var i=0; i < n; i++) {
            var att = atts[i];
            attributes[att.nodeName] = att.nodeValue;
        }
    }
    return attributes;
}

// This takes into account frame position in parent frame recursively
function __kivy__getRect(elem) {
    var w = window;
    var lrect = [0,0,0,0];
    while (elem && w) {
        try {
            var rect = elem.getBoundingClientRect();
            lrect[0] += rect.left;
            lrect[1] += rect.top;
            if (lrect[2]==0) lrect[2] = rect.width;
            if (lrect[3]==0) lrect[3] = rect.height;
            elem = w.frameElement;
            w = w.parent;
        } catch (err) {
            elem = false;
        }
    }
    return lrect;
}

window.addEventListener("focus", function (e) {
    var ike = __kivy__isKeyboardElement(e.target);
    __kivy__activeKeyboardElement = (ike?e.target:false);
    __kivy__activeKeyboardElementSince = new Date().getTime();
    __kivy__activeKeyboardElementSelection = false;
    __kivy__lastRect = __kivy__getRect(e.target);
    var attributes = __kivy__getAttributes(e.target);
    __kivy__keyboard_update(ike, __kivy__lastRect, attributes);
    __kivy__updateSelection();
}, true);

window.addEventListener("blur", function (e) {
    __kivy__keyboard_update(false, [], {});
    __kivy__activeKeyboardElement = false;
    __kivy__activeKeyboardElementSince = new Date().getTime();
    __kivy__activeKeyboardElementSelection = false;
    __kivy__lastRect = [];
    __kivy__updateSelection();
}, true);

function __kivy__updateRect() {
    if (__kivy__updateRectTimer) window.clearTimeout(__kivy__updateRectTimer);
    if (__kivy__activeKeyboardElement) {
        var lrect = __kivy__getRect(__kivy__activeKeyboardElement);
        if (!(\
            __kivy__lastRect && lrect.length==4 && \
            __kivy__lastRect.length==4 && \
            lrect[0]==__kivy__lastRect[0] && \
            lrect[1]==__kivy__lastRect[1] && \
            lrect[2]==__kivy__lastRect[2] && \
            lrect[3]==__kivy__lastRect[3] \
        )) {
            __kivy__keyboard_update(true, lrect, false);
            __kivy__lastRect = lrect;
        }
    }
    __kivy__updateRectTimer = window.setTimeout(__kivy__updateRect, 1000);
}
window.addEventListener("scroll", function (e) {
    if (__kivy__updateRectTimer) window.clearTimeout(__kivy__updateRectTimer);
    __kivy__updateRectTimer = window.setTimeout(__kivy__updateRect, 25);
}, true);
window.addEventListener("click", function (e) {
    if (\
        e.target == __kivy__activeKeyboardElement && \
        750 < (new Date().getTime() - __kivy__activeKeyboardElementSince)\
    ) {
        // TODO: only if selection stays the same
        __kivy__activeKeyboardElementSelection = true;
        __kivy__updateSelection();
    }
}, true);

function __kivy__on_escape() {
    if (__kivy__activeKeyboardElement) __kivy__activeKeyboardElement.blur();
    if (document.activeElement) document.activeElement.blur();
}
//var ae = document.activeElement;
//if (ae) {
//    ae.blur();
//    ae.focus();
//}
__kivy__updateRectTimer = window.setTimeout(__kivy__updateRect, 1000);


// Selection (Cut, Copy, Paste) management

function __kivy__updateSelection() {
    if (__kivy__activeKeyboardElement) {
        var lrect = __kivy__getRect(__kivy__activeKeyboardElement);
        var sstart = __kivy__activeKeyboardElement.selectionStart;
        var send = __kivy__activeKeyboardElement.selectionEnd;
        __kivy__selection_update({\
            "shown":(__kivy__activeKeyboardElementSelection || send!=sstart),\
            "can_cut":(send!=sstart),\
            "can_copy":(send!=sstart),\
            "can_paste":true\
        }, lrect, __kivy__activeKeyboardElement.value.substr(\
            sstart, send-sstart));
    } else {
        try {
            var s = window.getSelection();
            var r = s.getRangeAt(0);
            if (\
                r.startContainer==r.endContainer && \
                r.startOffset==r.endOffset\
            ) { // No selection
                __kivy__selection_update({"shown":false}, [0,0,0,0], "");
            } else {
                var lrect = __kivy__getRect(r);
                __kivy__selection_update({\
                    "shown":true,\
                    "can_cut":false,\
                    "can_copy":true,\
                    "can_paste":false\
                }, lrect, s.toString());
            }
        } catch (err) {
            __kivy__selection_update({"shown":false}, [0,0,0,0], "");
        }
    }
}

document.addEventListener("selectionchange", function (e) {
    __kivy__updateSelection();
});

"""
            frame.ExecuteJavascript(js_code)

    def OnLoadEnd(self, browser, frame, http_code):  # noqa: N802
        bw = self.browser_widgets[browser]
        bw.dispatch("on_load_end", frame, http_code)
        # browser.SetZoomLevel(2.0) # this works at this point

    def OnLoadError(  # noqa: N802
        self,
        browser,
        frame,
        error_code,
        error_text_out,
        failed_url,
    ):
        bw = self.browser_widgets[browser]
        bw.dispatch(
            "on_load_error", frame, error_code, error_text_out, failed_url)

    # RenderHandler

    def GetRootScreenRect(self, browser, rect_out):  # noqa: N802
        return False

    def GetViewRect(self, browser, rect_out):  # noqa: N802
        width, height = self.browser_widgets[browser]._texture.size
        rect_out.append(0)
        rect_out.append(0)
        rect_out.append(width)
        rect_out.append(height)
        return True

    def GetScreenRect(self, browser, rect_out):  # noqa: N802
        return False

    def GetScreenPoint(  # noqa: N802
        self,
        browser,
        view_x,
        view_y,
        screen_coordinates_out,
    ):
        return False

    def OnPopupShow(self, browser, show):  # noqa: N802
        bw = self.browser_widgets[browser]
        bw.remove_widget(bw._popup)
        if show:
            bw.add_widget(bw._popup)

    def OnPopupSize(self, browser, rect_out):  # noqa: N802
        bw = self.browser_widgets[browser]
        bw._popup.rpos = (rect_out[0], rect_out[1])
        bw._popup.size = (rect_out[2], rect_out[3])

    def OnPaint(  # noqa: N802
        self,
        browser,
        element_type,
        dirty_rects,
        paint_buffer,
        width,
        height,
    ):
        # print("ON PAINT", browser, time.time())
        if 'enable-fps' in CEFBrowser._flags:
            if not hasattr(self, 'lastPaints'):
                self.lastPaints = []
            self.lastPaints.append(time.time())
            while 10 < len(self.lastPaints):
                self.lastPaints.pop(0)
            if 1 < len(self.lastPaints):
                Logger.debug(
                    "CEFBrowser: FPS: %f",
                    len(self.lastPaints) /
                    (self.lastPaints[-1] - self.lastPaints[0]),
                )
        try:
            pmvfm = ctypes.pythonapi.PyMemoryView_FromMemory
            pmvfm.restype = ctypes.py_object
            pmvfm.argtypes = (ctypes.c_void_p, ctypes.c_int64, ctypes.c_int)
            view = pmvfm(paint_buffer.GetIntPointer(), width*height*4, 0x200)
        except AttributeError:
            """
            # The following code gives a segmentation fault:
            view = buffer('')
            pbfi = ctypes.pythonapi.PyBuffer_FillInfo
            pbfi.restype = ctypes.c_int
            pbfi.argtypes = (ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
                ctypes.c_ssize_t, ctypes.c_int, ctypes.c_int)
            res = pbfi(
                id(view), None, buf.GetIntPointer(), width*height*4, 0, 0)
            print(pbfi, res)
            """
            view = paint_buffer.GetString(mode="bgra", origin="top-left")
        bw = self.browser_widgets[browser]
        if element_type != cefpython.PET_VIEW:
            if (
                bw._popup._texture.width * bw._popup._texture.height * 4 !=
                width*height*4
            ):
                return True  # prevent segfault
            bw._popup._texture.blit_buffer(
                view, colorfmt="bgra", bufferfmt="ubyte")
            bw._popup._update_rect()
            return True
        if bw._texture.width * bw._texture.height * 4 != width*height * 4:
            return True  # prevent segfault
        bw._texture.blit_buffer(view, colorfmt="bgra", bufferfmt="ubyte")
        bw._update_rect()
        return True

    def OnCursorChange(self, browser, cursor):  # noqa: N802
        pass

    def OnScrollOffsetChanged(self, browser):  # noqa: N802
        pass

    def StartDragging(  # noqa: N802
        self,
        browser,
        drag_data,
        allowed_ops,
        x,
        y,
    ):
        """Succession of d&d calls:
        -   DragTargetDragEnter
        -   DragTargetDragOver - in touch move event
        -   DragTargetDragLeave - optional
        -   DragSourceSystemDragEnded - optional, to cancel dragging
        -   DragTargetDrop - on mouse up
        -   DragSourceEndedAt - on mouse up
        -   DragSourceSystemDragEnded - on mouse up"""
        # Logger.debug("~~ StartDragging")
        bw = self.browser_widgets[browser]
        bw._browser.DragTargetDragEnter(
            drag_data, x, y, cefpython.DRAG_OPERATION_EVERY)
        bw.is_html5_drag = True
        bw.is_html5_drag_leave = False
        bw.html5_drag_data = drag_data
        bw.current_html5_drag_operation = cefpython.DRAG_OPERATION_NONE
        bw.update_drag_representation(x, y)
        return True

    def UpdateDragCursor(self, browser, operation):  # noqa: N802
        self.browser_widgets[browser].current_drag_operation = operation

    # RequestHandler

    def OnBeforeBrowse(  # noqa: N802
        self,
        browser,
        frame,
        request,
        is_redirect,
    ):
        frame.ExecuteJavascript("try {__kivy__on_escape();} catch (err) {}")

    def OnBeforeResourceLoad(self, browser, frame, request):  # noqa: N802
        pass

    def GetResourceHandler(self, browser, frame, request):  # noqa: N802
        pass

    def OnResourceRedirect(  # noqa: N802
        self,
        browser,
        frame,
        old_url,
        new_url_out,
        request,
        response,
    ):
        pass

    def GetAuthCredentials(  # noqa: N802
        self,
        browser,
        frame,
        is_proxy,
        host,
        port,
        realm,
        scheme,
        callback,
    ):
        Logger.debug("GetAuthCredentials: "
                       "is_proxy: %s, host: %s, port: %s, "
                       "realm: %s, scheme: %s"
                       % (is_proxy, host, port, realm, scheme))
        ad = CEFBrowser._auth_dialog
        ad.host = host
        ad.callback = callback
        ad.scheme = scheme
        ad.open()
        return True

    def OnQuotaRequest(  # noqa: N802
        self,
        browser,
        origin_url,
        new_size,
        callback,
    ):
        pass

    def GetCookieManager(self, browser, main_url):  # noqa: N802
        cookie_manager = cefpython.CookieManager.GetGlobalManager()
        if cookie_manager:
            return cookie_manager
        else:
            Logger.warning("No cookie manager found!")

    def OnProtocolExecution(  # noqa: N802
        self,
        browser,
        url,
        allow_execution_out,
    ):
        pass

    def _OnBeforePluginLoad(  # noqa: N802
        self,
        browser,
        mime_type,
        plugin_url,
        is_main_frame,
        top_origin_url,
        plugin_info,
    ):
        return False

    def _OnCertificateError(  # noqa: N802
        self,
        cert_error,
        request_url,
        callback,
    ):
        Logger.warning("OnCertificateError %s %s %s" %
                       (cert_error, request_url, callback))
        if CEFBrowser.certificate_error_handler:
            try:
                res = CEFBrowser.certificate_error_handler(
                    CEFBrowser(), cert_error, request_url)
                if res:
                    callback.Continue(True)
                    return
            except Exception as err:
                Logger.warning(
                    "CEFBrowser: Error in certificate error handler.\n%s", err)

    def OnRendererProcessTerminated(self, browser, status):  # noqa: N802
        pass

    def OnPluginCrashed(self, browser, plugin_path):  # noqa: N802
        pass

    # RessourceHandler
    """
    def ProcessRequest(self, request, callback):  # noqa: N802
        callback.Continue()
        return True

    def GetResponseHeaders(  # noqa: N802
        self,
        response,
        response_length_out,
        redirect_url_out,
    ):
        pass

    def ReadResponse(  # noqa: N802
        self,
        data_out,
        bytes_to_read,
        bytes_read_out,
        callback,
    ):
        pass

    def CanGetCookie(self, cookie):  # noqa: N802
        return True

    def CanSetCookie(self, cookie):  # noqa: N802
        return True
    """
    # V8ContextHandler
    """
    def OnContextCreated(self, browser, frame):  # noqa: N802
        pass

    def OnContextReleased(self, browser, frame):  # noqa: N802
        pass
    """


client_handler = ClientHandler()


cefpython.SetGlobalClientCallback(
    "OnAfterCreated", client_handler._OnAfterCreated)

cefpython.SetGlobalClientCallback(
    "OnCertificateError", client_handler._OnCertificateError)

Builder.load_file(os.path.join(
    os.path.realpath(os.path.dirname(__file__)),
    "cefbrowser.kv",
))
CEFBrowser._js_alert = Factory.CEFBrowserJSAlert()
CEFBrowser._js_confirm = Factory.CEFBrowserJSConfirm()
CEFBrowser._js_prompt = Factory.CEFBrowserJSPrompt()
CEFBrowser._auth_dialog = Factory.CEFBrowserAuthDialog()


if __name__ == "__main__":
    import os
    from kivy.app import App
    from kivy.clock import Clock
    from kivy.uix.button import Button
    from kivy.uix.textinput import TextInput
    cef_test_url = "file://"+os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "test.html",
    )
    CEFBrowser.update_flags({'enable-copy-paste': True, 'enable-fps': True})

    class CEFBrowserApp(App):
        def timeout(self, *largs):
            self.cb1.url = cef_test_url

        def build(self):
            class FocusButton(FocusBehavior, Button):
                pass
            wid = Window.width/2
            hei = Window.height
            ti1 = TextInput(
                text="ti1", pos=(0, hei-50), size=(wid-1, 50))
            ti2 = TextInput(
                text="ti2", pos=(wid+1, hei-50), size=(wid-1, 50))
            fb1 = FocusButton(
                text="ti1", pos=(0, hei-100), size=(wid-1, 50))
            fb2 = FocusButton(
                text="ti2", pos=(wid+1, hei-100), size=(wid-1, 50))

            def url_handler(self, url):
                print("URL HANDLER", url)

            def title_handler(self, title):
                print("TITLE HANDLER", title)

            def close_handler(self):
                print("CLOSE HANDLER")

            def popup_policy_handler(self, popup_url):
                print("POPUP POLICY HANDLER", popup_url)
                return True

            def popup_handler(self, popup_browser):
                print("POPUP HANDLER", popup_browser)
                pw = None
                for key in client_handler.browser_widgets:
                    pw = client_handler.browser_widgets[key].parent
                    if pw:
                        break
                popup_browser.pos = (Window.width/4, Window.height/4)
                popup_browser.size = (Window.width/2, Window.height/2)
                popup_browser.popup_handler = popup_handler
                popup_browser.close_handler = close_handler
                pw.add_widget(popup_browser)

            self.cb1 = CEFBrowser(
                url="http://jegger.ch/datapool/app/test_popup.html",
                pos=(0, 0), size=(wid-1, hei-100),
            )
            self.cb1.popup_policy = popup_policy_handler
            self.cb1.popup_handler = popup_handler
            self.cb1.close_handler = close_handler
            self.cb1.bind(url=url_handler)
            self.cb1.bind(title=title_handler)
            self.cb2 = CEFBrowser(
                url="https://rentouch.ch/",
                pos=(wid+1, 0), size=(wid-1, hei-100),
            )
            self.cb2.popup_policy = popup_policy_handler
            self.cb2.popup_handler = popup_handler
            self.cb2.close_handler = close_handler
            # http://jegger.ch/datapool/app/test_popup.html
            # http://jegger.ch/datapool/app/test_events.html
            # https://rally1.rallydev.com/
            w = Widget()
            w.add_widget(self.cb1)
            w.add_widget(self.cb2)
            w.add_widget(fb1)
            w.add_widget(fb2)
            w.add_widget(ti1)
            w.add_widget(ti2)
            Clock.schedule_once(self.timeout, 10)
            return w

    CEFBrowserApp().run()

    cefpython.Shutdown()
