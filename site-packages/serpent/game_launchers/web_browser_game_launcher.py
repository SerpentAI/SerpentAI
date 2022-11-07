from serpent.game_launcher import GameLauncher, GameLauncherException

from serpent.utilities import is_linux, is_macos, is_windows

import enum
import webbrowser


class WebBrowser(enum.Enum):
    DEFAULT = 0
    CHROME = 1
    CHROMIUM = 2
    FIREFOX = 3
    OPERA = 4
    SAFARI = 5


class WebBrowserGameLauncher(GameLauncher):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def web_browsers(self):
        return {
            WebBrowser.DEFAULT.name: None,
            WebBrowser.CHROME.name: "chrome",
            WebBrowser.CHROMIUM.name: "chromium",
            WebBrowser.FIREFOX.name: "firefox",
            WebBrowser.OPERA.name: "opera",
            WebBrowser.SAFARI.name: "safari"
        }

    def launch(self, **kwargs):
        url = kwargs.get("url")
        browser = kwargs.get("browser") or WebBrowser.DEFAULT

        if url is None:
            raise GameLauncherException("An 'url' kwarg is required...")

        if is_linux():
            webbrowser.get(self.web_browsers.get(browser.name)).open_new(url)
        elif is_macos():
            webbrowser.get(self.web_browsers.get(browser.name)).open_new(url)
        elif is_windows():
            webbrowser.get(self.web_browsers.get(browser.name)).open_new(url)
