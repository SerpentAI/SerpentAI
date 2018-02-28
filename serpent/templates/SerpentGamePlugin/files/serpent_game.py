from serpent.game import Game

from .api.api import MyGameAPI

from serpent.utilities import Singleton

from serpent.game_launchers.web_browser_game_launcher import WebBrowser


class SerpentGame(Game, metaclass=Singleton):

    def __init__(self, **kwargs):
        kwargs["platform"] = "PLATFORM"

        kwargs["window_name"] = "WINDOW_NAME"

        kwargs["app_id"] = "APP_ID"
        kwargs["app_args"] = None
        kwargs["executable_path"] = "EXECUTABLE_PATH"
        kwargs["url"] = "URL"
        kwargs["browser"] = WebBrowser.DEFAULT

        super().__init__(**kwargs)

        self.api_class = MyGameAPI
        self.api_instance = None

        self.environments = dict()
        self.environment_data = dict()

    @property
    def screen_regions(self):
        regions = {
            "SAMPLE_REGION": (0, 0, 0, 0)
        }

        return regions
