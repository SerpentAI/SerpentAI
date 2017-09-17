import asyncio

from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
from autobahn.wamp.types import RegisterOptions, SubscribeOptions
from autobahn.wamp import auth

from serpent.config import config

import aioredis
import json


class AnalyticsComponent:
    @classmethod
    def run(cls):
        print(f"Starting {cls.__name__}...")

        url = "ws://%s:%s" % (config["analytics"]["host"], config["analytics"]["port"])

        runner = ApplicationRunner(url=url, realm=config["analytics"]["realm"])
        runner.run(AnalyticsWAMPComponent)


class AnalyticsWAMPComponent(ApplicationSession):
    def __init__(self, c=None):
        super().__init__(c)

    def onConnect(self):
        self.join(config["analytics"]["realm"], ["wampcra"], config["analytics"]["auth"]["username"])

    def onDisconnect(self):
        print("Disconnected from Crossbar!")

    def onChallenge(self, challenge):
        secret = config["analytics"]["auth"]["password"]
        signature = auth.compute_wcs(secret.encode('utf8'), challenge.extra['challenge'].encode('utf8'))

        return signature.decode('ascii')

    async def onJoin(self, details):
        self.redis_client = await self._initialize_redis_client()

        while True:
            redis_key, event = await self.redis_client.brpop("SERPENT:AISAAC_MAZE:EVENTS")
            event = json.loads(event.decode("utf-8"))

            topic = event.pop("project_key")
            self.publish(topic, event)

    async def _initialize_redis_client(self):
        return await aioredis.create_redis(
            (config["redis"]["host"], config["redis"]["port"]),
            loop=asyncio.get_event_loop()
        )
