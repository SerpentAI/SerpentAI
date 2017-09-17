from serpent.game_launcher import GameLauncher, GameLauncherException

import sys
import shlex
import subprocess


class ExecutableGameLauncher(GameLauncher):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def launch(self, **kwargs):
        executable_path = kwargs.get("executable_path")

        if executable_path is None:
            raise GameLauncherException("An 'executable_path' kwarg is required...")

        if sys.platform in ["linux", "linux2"]:
            subprocess.Popen(shlex.split(executable_path))
        elif sys.platform == "darwin":
            subprocess.Popen(shlex.split(executable_path))
        elif sys.platform == "win32":
            subprocess.Popen(shlex.split(executable_path))