import asyncio

from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
from autobahn.wamp.types import RegisterOptions, SubscribeOptions
from autobahn.wamp import auth

from serpent.config import config
from serpent.utilities import is_windows

from serpent.input_controller import InputController, InputControllers, KeyboardKey

import aioredis
import json
import pickle

import offshoot


class InputControllerComponent:
    @classmethod
    def run(cls):
        print(f"Starting {cls.__name__}...")

        url = "ws://%s:%s" % (config["crossbar"]["host"], config["crossbar"]["port"])

        runner = ApplicationRunner(url=url, realm=config["crossbar"]["realm"])
        runner.run(InputControllerWAMPComponent)


class InputControllerWAMPComponent(ApplicationSession):
    def __init__(self, c=None):
        super().__init__(c)

        self.redis_client = None
        self.input_controller = None
        

    def onConnect(self):
        self.join(config["crossbar"]["realm"], ["wampcra"], config["crossbar"]["auth"]["username"])

    def onDisconnect(self):
        print("Disconnected from Crossbar!")

    def onChallenge(self, challenge):
        secret = config["crossbar"]["auth"]["password"]
        signature = auth.compute_wcs(secret.encode('utf8'), challenge.extra['challenge'].encode('utf8'))

        return signature.decode('ascii')

    async def onJoin(self, details):
        self.redis_client = await self._initialize_redis_client()

        game_class_name = await self.redis_client.get("SERPENT:GAME")
        game_class = offshoot.discover("Game")[game_class_name.decode("utf-8")]

        game = game_class()
        game.launch(dry_run=True)

        backend_string=config["input_controller"]["backend"]

        backend = InputControllers.NATIVE_WIN32 if is_windows() else InputControllers.PYAUTOGUI

        if backend_string != "DEFAULT":
            try:
                backend = InputControllers[backend_string]
            except KeyError:
                pass

        self.input_controller = InputController(game=game, backend=backend)

        while True:
            payload = await self.redis_client.brpop(config["input_controller"]["redis_key"])
            payload = pickle.loads(payload[1])

            input_controller_func_string, *args, kwargs = payload
            getattr(self.input_controller, input_controller_func_string)(*args, **kwargs)

            await asyncio.sleep(0.01)

    async def _initialize_redis_client(self):
        return await aioredis.create_redis(
            (config["redis"]["host"], config["redis"]["port"]),
            loop=asyncio.get_event_loop()
        )


if __name__ == "__main__":
    InputControllerComponent.run()
