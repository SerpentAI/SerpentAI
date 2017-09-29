from serpent.game_launcher import GameLauncher, GameLauncherException

import sys
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

        if sys.platform in ["linux", "linux2"]:
            webbrowser.get(self.web_browsers.get(browser.name)).open_new(url)
        elif sys.platform == "darwin":
            webbrowser.get(self.web_browsers.get(browser.name)).open_new(url)
        elif sys.platform == "win32":
            webbrowser.get(self.web_browsers.get(browser.name)).open_new(url)

