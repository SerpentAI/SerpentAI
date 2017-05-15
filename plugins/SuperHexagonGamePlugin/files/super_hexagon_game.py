from lib.game import Game
from lib.config import config

import offshoot


class SuperHexagonGame(Game):

    def __init__(self, **kwargs):
        kwargs["platform"] = "steam"
        kwargs["app_id"] = "221640"

        kwargs["window_name"] = "Super Hexagon"
        kwargs["frame_rate"] = config["SuperHexagonGamePlugin"].get("frame_rate") or 10

        super().__init__(**kwargs)

    @property
    def screen_regions(self):
        return dict(
            SPLASH_ACTIONS=(349, 260, 391, 507),
            GAME_HUD_TIME=(0, 562, 52, 768),
            GAME_PLAYER_AREA=(129, 264, 366, 513),
            DEATH_TIME_LAST=(158, 600, 207, 768)
        )