from lib.game import Game

from .api.api import MyGameAPI

from lib.utilities import Singleton


class SerpentGame(Game, metaclass=Singleton):

    def __init__(self, **kwargs):
        kwargs["platform"] = "PLATFORM"

        kwargs["window_name"] = "WINDOW_NAME"

        kwargs["app_id"] = "APP_ID"
        kwargs["app_args"] = None
        kwargs["executable_path"] = "EXECUTABLE_PATH"

        super().__init__(**kwargs)

        self.api_class = MyGameAPI
        self.api_instance = None

    @property
    def screen_regions(self):
        regions = {

        }

        return regions
