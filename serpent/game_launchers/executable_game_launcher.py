from serpent.game_launcher import GameLauncher, GameLauncherException

import sys
import shlex
import subprocess

import psutil
import os


class ExecutableGameLauncher(GameLauncher):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def launch(self, **kwargs):
        executable_path = kwargs.get("executable_path")

        if executable_path is None:
            raise GameLauncherException("An 'executable_path' kwarg is required...")

        if sys.platform == "win32":
           for pid in psutil.pids():
                p = psutil.Process(pid)
                pname = os.path.basename(kwargs.get("executable_path"))
                if p.name() == pname:      
                    return p.pid
           
        return subprocess.Popen(shlex.split(executable_path)).pid

        