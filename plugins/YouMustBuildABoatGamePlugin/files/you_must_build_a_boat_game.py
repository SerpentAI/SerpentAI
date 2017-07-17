from lib.game import Game
from lib.config import config

import offshoot


class YouMustBuildABoatGame(Game):

    def __init__(self, **kwargs):
        kwargs["platform"] = "steam"

        kwargs["app_id"] = "290890"
        kwargs["app_args"] = None

        kwargs["window_name"] = "#ymbab"

        super().__init__(**kwargs)

    @property
    def screen_regions(self):
        return {
            "MENU_CONTINUE": (287, 351, 342, 620),
            "MENU_NEW_GAME": (350, 376, 385, 595),
            "MENU_LOAD_GAME": (394, 376, 429, 595),
            "MENU_SETTINGS": (438, 376, 473, 595),
            "MENU_QUIT": (482, 376, 517, 595)
        }
