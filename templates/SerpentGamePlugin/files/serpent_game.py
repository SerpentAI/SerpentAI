from lib.game import Game

from .api import api


class SerpentGame(Game):

    def __init__(self, **kwargs):
        kwargs["platform"] = "PLATFORM"

        kwargs["window_name"] = "WINDOW_NAME"

        kwargs["app_id"] = "APP_ID"
        kwargs["app_args"] = None
        kwargs["executable_path"] = "EXECUTABLE_PATH"

        super().__init__(**kwargs)

        self.api = api

    @property
    def screen_regions(self):
        regions = {

        }

        return regions
