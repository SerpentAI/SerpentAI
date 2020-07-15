from serpent.game import Game

from .api.api import MyGameAPI

from serpent.utilities import SerpentError, Singleton

from serpent.game_launchers.web_browser_game_launcher import WebBrowser

import time


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

    def after_launch(self):
        self.is_launched = True

        current_attempt = 1

        while current_attempt <= 100:
            self.window_id = self.window_controller.locate_window(self.window_name)

            if self.window_id not in [0, "0"]:
                break

            time.sleep(0.1)

        time.sleep(0.5)

        if self.window_id in [0, "0"]:
            raise SerpentError("Game window not found...")

        self.window_controller.move_window(self.window_id, 0, 0)

        self.dashboard_window_id = self.window_controller.locate_window("Serpent.AI Dashboard")

        # TODO: Test on Linux
        if self.dashboard_window_id is not None and self.dashboard_window_id not in [0, "0"]:
            self.window_controller.bring_window_to_top(self.dashboard_window_id)

        self.window_controller.focus_window(self.window_id)

        self.window_geometry = self.extract_window_geometry()

        print(self.window_geometry)
