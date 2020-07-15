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

        url = "ws://%s:%s" % (config["crossbar"]["host"], config["crossbar"]["port"])

        runner = ApplicationRunner(url=url, realm=config["crossbar"]["realm"])
        runner.run(AnalyticsWAMPComponent)


class AnalyticsWAMPComponent(ApplicationSession):
    def __init__(self, c=None):
        super().__init__(c)

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
        self.log_file = open(f"{config['analytics']['topic']}.json", "a")

        await self.redis_client.delete(f"SERPENT:{config['analytics']['topic']}:EVENTS")

        while True:
            redis_key, event = await self.redis_client.brpop(f"SERPENT:{config['analytics']['topic']}:EVENTS")

            event = event.decode("utf-8")
            event_parsed = json.loads(event)

            if event_parsed["event_key"] in config["analytics"]["persisted_events"] and event_parsed["is_persistable"]:
                self.log_file.write(f"{event}\n")
                self.log_file.flush()

            topic = event_parsed.pop("project_key")
            self.publish(topic, event_parsed)

    async def _initialize_redis_client(self):
        return await aioredis.create_redis(
            (config["redis"]["host"], config["redis"]["port"]),
            loop=asyncio.get_event_loop()
        )

if __name__ == "__main__":
    AnalyticsComponent.run()
