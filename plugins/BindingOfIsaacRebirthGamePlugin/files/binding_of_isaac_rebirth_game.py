from lib.game import Game
from lib.config import config

import offshoot


class BindingOfIsaacRebirthGame(Game):

    def __init__(self, **kwargs):
        kwargs["platform"] = "steam"

        kwargs["app_id"] = "250900"
        kwargs["app_args"] = {
            "set-stage-type": 0,
            "set-stage": 1,
            "load-room": "maze002.xml"
        }

        kwargs["window_name"] = "Binding of Isaac: Afterbirth"

        super().__init__(**kwargs)

    @property
    def screen_regions(self):
        return dict(
            MENU_NEW_GAME=(126, 322, 164, 357),
            CHARACTER_SELECT_DIFFICULTY_NORMAL=(258, 720, 282, 737),
            CHARACTER_SELECT_DIFFICULTY_HARD=(298, 716, 322, 735),
            HUD_HEALTH=(33, 121, 102, 333),
            HUD_COINS=(71, 28, 91, 57),
            HUD_BOMBS=(118, 67, 141, 117),
            HUD_KEYS=(142, 67, 167, 117),
            HUD_ITEM_ACQUIRED=(81, 167, 113, 787),
            HUD_MAP=(32, 800, 125, 910),
            HUD_MAP_CENTER=(71, 845, 85, 861),
            HUD_HEART_1=(12, 84, 32, 106),
            HUD_HEART_2=(12, 108, 32, 130),
            HUD_HEART_3=(12, 132, 32, 154),
            HUD_HEART_4=(12, 156, 32, 178),
            HUD_HEART_5=(12, 180, 32, 202),
            HUD_HEART_6=(12, 204, 32, 226),
            HUD_HEART_7=(32, 84, 52, 106),
            HUD_HEART_8=(32, 108, 52, 130),
            HUD_HEART_9=(32, 132, 52, 154),
            HUD_HEART_10=(32, 156, 52, 178),
            HUD_HEART_11=(32, 180, 52, 202),
            HUD_HEART_12=(32, 204, 52, 226),
            HUD_BOSS_HP=(519, 371, 522, 592),
            HUD_BOSS_SKULL=(496, 340, 529, 373),
            GAME_ISAAC_DOOR_TOP=(43, 435, 134, 524),
            GAME_ISAAC_DOOR_RIGHT=(202, 760, 307, 825),
            GAME_ISAAC_DOOR_BOTTOM=(359, 435, 444, 524),
            GAME_ISAAC_DOOR_LEFT=(202, 138, 307, 198)
        )