from serpent.utilities import SerpentError, is_windows

from serpent.config import config

if is_windows():
    import win32api
else:
    import mss

import time
import subprocess
import shlex
import signal
import atexit

try:
    from serpent.dashboard.cefbrowser.cefbrowser import CEFBrowser

    from kivy.config import Config

    from kivy.app import App
    from kivy.core.window import Window

    from kivy.uix.widget import Widget
    from kivy.uix.image import Image
    from kivy.uix.label import Label

    from kivy.uix.floatlayout import FloatLayout
    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.boxlayout import BoxLayout

    from kivy.clock import Clock
except ImportError:
    raise SerpentError("Setup has not been been performed for the Dashboard module. Please run 'serpent setup dashboard'")


class DashboardApp(App):
    def __init__(self, width=None, height=None):
        super().__init__()

        self.display_width, self.display_height = self._determine_fullscreen_resolution()

        if width is not None and height is not None:
            self.width = width
            self.height = height
        else:
            self.width = self.display_width
            self.height = self.display_height

        self.configure()

        self.crossbar_process = None
        self.start_crossbar()

        time.sleep(3)

        self.analytics_publisher_process = None
        self.start_analytics_publisher()

        self.dashboard_api_process = None
        self.start_dashboard_api()

        self.root = None

    def configure(self):
        Config.set("graphics", "left", 0)
        Config.set("graphics", "top", 0)

        Config.set("graphics", "width", self.display_width)
        Config.set("graphics", "height", self.display_height)

        Config.set("graphics", "borderless", 1)
        Config.set("graphics", "resizable", 0)

        Config.set('input', 'mouse', 'mouse,disable_multitouch')

        Config.write()

    def build(self):
        self.title = "Serpent.AI Dashboard"
        self.icon = "dashboard/serpent.png"

        Window.clearcolor = (0.1373, 0.1922, 0.2510, 1)

        self.root = DashboardRootWidget(self.display_width, self.display_height, self.width, self.height)

        return self.root

    def start_crossbar(self):
        if self.crossbar_process is not None:
            self.stop_crossbar()

        crossbar_command = f"crossbar start --config dashboard/crossbar.json"

        self.crossbar_process = subprocess.Popen(shlex.split(crossbar_command))

        signal.signal(signal.SIGINT, self._handle_signal_crossbar)
        signal.signal(signal.SIGTERM, self._handle_signal_crossbar)

        atexit.register(self._handle_signal_crossbar, 15, None, False)

    def stop_crossbar(self):
        if self.crossbar_process is None:
            return None

        self.crossbar_process.kill()
        self.crossbar_process = None

        atexit.unregister(self._handle_signal_crossbar)

    def start_analytics_publisher(self):
        if self.analytics_publisher_process is not None:
            self.stop_analytics_publisher_process()

        analytics_publisher_command = "python dashboard/analytics_component.py"

        self.analytics_publisher_process = subprocess.Popen(shlex.split(analytics_publisher_command))

        signal.signal(signal.SIGINT, self._handle_signal_analytics_publisher)
        signal.signal(signal.SIGTERM, self._handle_signal_analytics_publisher)

        atexit.register(self._handle_signal_analytics_publisher, 15, None, False)

    def stop_analytics_publisher(self):
        if self.analytics_publisher_process is None:
            return None

        self.analytics_publisher_process.kill()
        self.analytics_publisher_process = None

        atexit.unregister(self._handle_signal_analytics_publisher)

    def start_dashboard_api(self):
        if self.dashboard_api_process is not None:
            self.stop_dashboard_api()

        dashboard_api_command = f"python dashboard/dashboard_api_component.py"

        self.dashboard_api_process = subprocess.Popen(shlex.split(dashboard_api_command))

        signal.signal(signal.SIGINT, self._handle_signal_dashboard_api)
        signal.signal(signal.SIGTERM, self._handle_signal_dashboard_api)

        atexit.register(self._handle_signal_dashboard_api, 15, None, False)

    def stop_dashboard_api(self):
        if self.dashboard_api_process is None:
            return None

        self.dashboard_api_process.kill()
        self.dashboard_api_process = None

        atexit.unregister(self._handle_signal_dashboard_api)

    def _determine_fullscreen_resolution(self):
        if is_windows():
            return [win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)]
        else:
            monitors = mss.mss().monitors
            return monitors[0]["width"], monitors[0]["height"]

    def _handle_signal_crossbar(self, signum=15, frame=None, do_exit=True):
        if self.crossbar_process is not None:
            if self.crossbar_process.poll() is None:
                self.crossbar_process.send_signal(signum)

                if do_exit:
                    exit()

    def _handle_signal_analytics_publisher(self, signum=15, frame=None, do_exit=True):
        if self.analytics_publisher_process is not None:
            if self.analytics_publisher_process.poll() is None:
                self.analytics_publisher_process.send_signal(signum)

                if do_exit:
                    exit()

    def _handle_signal_dashboard_api(self, signum=15, frame=None, do_exit=True):
        if self.dashboard_api_process is not None:
            if self.dashboard_api_process.poll() is None:
                self.dashboard_api_process.send_signal(signum)

                if do_exit:
                    exit()


class DashboardRootWidget(Widget):
    def __init__(self, display_width, display_height, width, height):
        super().__init__()

        self.size = (display_width, display_height)

        self.browser = None

        self.initialize_background_image(width, height)
        self.initialize_browser(width, height)

    def initialize_background_image(self, width, height):
        background_image = Image(source="dashboard/serpent.png")

        background_image.size = (height, height)
        background_image.opacity = 0.1
        background_image.pos = ((width / 2) - (height / 2), self.size[1] - height)

        self.add_widget(background_image)

    def initialize_browser(self, width, height):
        self.browser = CEFBrowser(url="http://dashboard.serpent.ai/dashboards")

        self.browser.size = (width, height)
        self.browser.pos = (0, self.size[1] - height)

        self.add_widget(self.browser)

if __name__ == "__main__":
    DashboardApp().run()
