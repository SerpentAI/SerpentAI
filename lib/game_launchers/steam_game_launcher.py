from lib.game_launcher import GameLauncher, GameLauncherException

import sys
import shlex
import subprocess


class SteamGameLauncher(GameLauncher):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def launch(self, **kwargs):
        app_id = kwargs.get("app_id")

        if app_id is None:
            raise GameLauncherException("An 'app_id' kwarg is required...")

        if sys.platform in ["linux", "linux2"]:
            subprocess.call(shlex.split(f"xdg-open steam://run/{app_id}"))
        elif sys.platform == "darwin":
            subprocess.call(shlex.split(f"open steam://run/{app_id}"))
        elif sys.platform == "windows":
            pass  # ???
