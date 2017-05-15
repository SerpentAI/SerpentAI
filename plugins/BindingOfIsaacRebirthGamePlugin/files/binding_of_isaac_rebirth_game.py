from lib.game import Game
from lib.config import config

import offshoot


class BindingOfIsaacRebirthGame(Game):

    def __init__(self, **kwargs):
        kwargs["platform"] = "steam"
        kwargs["app_id"] = "250900"

        kwargs["window_name"] = "Binding of Isaac: Rebirth"

        super().__init__(**kwargs)

    @property
    def screen_regions(self):
        return dict(
            MENU_NEW_GAME=(126, 322, 164, 357),
            CHARACTER_SELECT_DIFFICULTY_NORMAL=(258, 720, 282, 737),
            CHARACTER_SELECT_DIFFICULTY_HARD=(298, 716, 322, 735),
            HUD_HEALTH=(33, 121, 102, 333),
            HUD_COINS=(95, 67, 117, 117),
            HUD_BOMBS=(118, 67, 141, 117),
            HUD_KEYS=(142, 67, 167, 117),
            HUD_ITEM_ACQUIRED=(81, 167, 113, 787),
            HUD_MAP=(32, 800, 125, 910),
            HUD_MAP_CENTER=(71, 845, 85, 861)
        )