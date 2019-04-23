from serpent.game_launcher import GameLauncher, GameLauncherException
from serpent.utilities import is_linux, is_macos, is_windows

import shlex
import subprocess


class ExecutableGameLauncher(GameLauncher):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def launch(self, **kwargs):
        executable_path = kwargs.get("executable_path")

        if executable_path is None:
            raise GameLauncherException("An 'executable_path' kwarg is required...")

        if is_linux():
            subprocess.Popen(executable_path)
        elif is_macos():
            subprocess.Popen(executable_path)
        elif is_windows():
            subprocess.Popen(executable_path)