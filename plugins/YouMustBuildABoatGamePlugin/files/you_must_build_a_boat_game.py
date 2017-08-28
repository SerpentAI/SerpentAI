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
        regions = {
            "MENU_CONTINUE": (287, 351, 342, 620),
            "MENU_NEW_GAME": (350, 376, 385, 595),
            "MENU_LOAD_GAME": (394, 376, 429, 595),
            "MENU_SETTINGS": (438, 376, 473, 595),
            "MENU_QUIT": (482, 376, 517, 595),
            "GAME_ABOVE_BOARD": (69, 342, 193, 1023),
            "GAME_OVER_RUN_AGAIN": (600, 250, 673, 509)
        }

        rows = ["A", "B", "C", "D", "E", "F"]
        columns = [1, 2, 3, 4, 5, 6, 7, 8]

        start_x = 348
        start_y = 197

        for i, row in enumerate(rows):
            for ii, column in enumerate(columns):
                coordinates = f"{row}{column}"

                regions[f"GAME_BOARD_{coordinates}"] = (
                    start_y + (i * 84),
                    start_x + (ii * 84),
                    start_y + 79 + (i * 84),
                    start_x + 79 + (ii * 84),
                )

        return regions
