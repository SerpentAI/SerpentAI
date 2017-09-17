from serpent.game_launcher import GameLauncher, GameLauncherException

import sys
import shlex
import subprocess
import webbrowser


class SteamGameLauncher(GameLauncher):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def launch(self, **kwargs):
        app_id = kwargs.get("app_id")
        app_args = kwargs.get("app_args")

        if app_id is None:
            raise GameLauncherException("An 'app_id' kwarg is required...")

        protocol_string = f"steam://run/{app_id}"

        if app_args is not None:
            args_list = [f"--{k}={v}" for k, v in app_args.items()]
            protocol_string += "/en/" + " ".join(args_list)

        if sys.platform in ["linux", "linux2"]:
            subprocess.call(shlex.split(f"xdg-open '{protocol_string}'"))
        elif sys.platform == "darwin":
            subprocess.call(shlex.split(f"open '{protocol_string}'"))
        elif sys.platform == "win32":
            webbrowser.open(f"{protocol_string}")
