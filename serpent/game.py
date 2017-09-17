import warnings
warnings.simplefilter("ignore")

import offshoot

import subprocess
import signal
import shlex
import time
import sys
import os, os.path
import atexit

from serpent.game_agent import GameAgent

from serpent.game_launchers.steam_game_launcher import SteamGameLauncher
from serpent.game_launchers.executable_game_launcher import ExecutableGameLauncher

from serpent.window_controller import WindowController
from serpent.input_controller import InputController

from serpent.frame_grabber import FrameGrabber
from serpent.game_frame_limiter import GameFrameLimiter

from serpent.sprite import Sprite

import serpent.utilities

import skimage.io
import skimage.color

import numpy as np

from redis import StrictRedis

from serpent.config import config


class GameError(BaseException):
    pass


class Game(offshoot.Pluggable):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config = config.get(f"{self.__class__.__name__}Plugin")

        self.platform = kwargs.get("platform")

        self.window_id = None
        self.window_name = kwargs.get("window_name")
        self.window_geometry = None

        self.window_controller = WindowController()

        self.is_launched = False

        self.frame_grabber_process = None
        self.game_frame_limiter = GameFrameLimiter(fps=self.config.get("fps", 4))

        self.api_class = None
        self.api_instance = None

        self.sprites = self._discover_sprites()

        self.redis_client = StrictRedis(**config["redis"])

        self.kwargs = kwargs

    @property
    @offshoot.forbidden
    def game_launcher(self):
        return self.game_launchers.get(self.platform)

    @property
    @offshoot.forbidden
    def game_launchers(self):
        return {
            "steam": SteamGameLauncher,
            "executable": ExecutableGameLauncher
        }

    @property
    @offshoot.expected
    def screen_regions(self):
        raise NotImplementedError()

    @property
    @offshoot.expected
    def ocr_presets(self):
        raise NotImplementedError()

    @property
    @offshoot.forbidden
    def api(self):
        if self.api_instance is None:
            self.api_instance = self.api_class(game=self)
        else:
            return self.api_instance

    @property
    @offshoot.forbidden
    def is_focused(self):
        return self.window_controller.is_window_focused(self.window_id)

    @offshoot.forbidden
    def launch(self, dry_run=False):
        self.before_launch()

        if not dry_run:
            self.game_launcher().launch(**self.kwargs)

        self.after_launch()

    def before_launch(self):
        pass

    def after_launch(self):
        self.is_launched = True

        time.sleep(5)

        self.window_id = self.window_controller.locate_window(self.window_name)

        self.window_controller.move_window(self.window_id, 0, 0)
        self.window_controller.focus_window(self.window_id)

        self.window_geometry = self.extract_window_geometry()
        print(self.window_geometry)

    def play(self, game_agent_class_name=None, frame_handler=None, **kwargs):
        if not self.is_launched:
            raise GameError(f"Game '{self.__class__.__name__}' is not running...")

        game_agent_class = offshoot.discover("GameAgent").get(game_agent_class_name, GameAgent)

        if game_agent_class is None:
            raise GameError("The provided Game Agent class name does not map to an existing class...")

        game_agent = game_agent_class(
            game=self,
            input_controller=InputController(game=self)
        )

        self.start_frame_grabber()
        self.redis_client.delete(config["frame_grabber"]["redis_key"])

        while self.redis_client.llen(config["frame_grabber"]["redis_key"]) == 0:
            time.sleep(0.1)

        self.window_controller.focus_window(self.window_id)

        while True:
            self.game_frame_limiter.start()

            game_frame = self.grab_latest_frame()
            try:
                if self.is_focused:
                    game_agent.on_game_frame(game_frame, frame_handler=frame_handler, **kwargs)
                else:
                    serpent.utilities.clear_terminal()
                    print("PAUSED")

                    time.sleep(1)
            except Exception as e:
                raise e
                # print(e)
                # time.sleep(0.1)

            self.game_frame_limiter.stop_and_delay()

    @offshoot.forbidden
    def extract_window_geometry(self):
        if self.is_launched:
            return self.window_controller.get_window_geometry(self.window_id)

        return None

    @offshoot.forbidden
    def start_frame_grabber(self):
        if not self.is_launched:
            raise GameError(f"Game '{self.__class__.__name__}' is not running...")

        if self.frame_grabber_process is not None:
            self.stop_frame_grabber()

        frame_grabber_command = f"serpent grab_frames {self.window_geometry['width']} {self.window_geometry['height']} {self.window_geometry['x_offset']} {self.window_geometry['y_offset']}"
        self.frame_grabber_process = subprocess.Popen(shlex.split(frame_grabber_command))

        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

        atexit.register(self._handle_signal, 15, None, False)

    @offshoot.forbidden
    def stop_frame_grabber(self):
        if self.frame_grabber_process is None:
            return None

        self.frame_grabber_process.kill()
        self.frame_grabber_process = None

        atexit.unregister(self._handle_signal)

    @offshoot.forbidden
    def grab_latest_frame(self):
        game_frame_buffer = FrameGrabber.get_frames(
            [0],
            (
                self.window_geometry.get("height"),
                self.window_geometry.get("width"),
                3
            )
        )

        return game_frame_buffer.frames[0]

    def _discover_sprites(self):
        plugin_path = offshoot.config["file_paths"]["plugins"]
        sprites = dict()

        sprite_path = f"{plugin_path}/{self.__class__.__name__}Plugin/files/data/sprites"

        if os.path.isdir(sprite_path):
            files = os.scandir(sprite_path)

            for file in files:
                if file.name.endswith(".png"):
                    sprite_name = "_".join(file.name.split("/")[-1].split("_")[:-1]).replace(".png", "").upper()

                    sprite_image_data = skimage.io.imread(f"{sprite_path}/{file.name}")
                    sprite_image_data = sprite_image_data[..., np.newaxis]

                    if sprite_name not in sprites:
                        sprite = Sprite(sprite_name, image_data=sprite_image_data)
                        sprites[sprite_name] = sprite
                    else:
                        sprites[sprite_name].append_image_data(sprite_image_data)

        return sprites

    def _handle_signal(self, signum=15, frame=None, do_exit=True):
        if self.frame_grabber_process is not None:
            if self.frame_grabber_process.poll() is None:
                self.frame_grabber_process.send_signal(signum)

                if do_exit:
                    exit()
