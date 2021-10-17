import asyncio

from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
from autobahn.wamp import auth

from elasticsearch import Elasticsearch

from serpent.config import config

import uuid


class AnalyticsElasticsearchComponent:
    @classmethod
    def run(cls):
        print(f"Starting {cls.__name__}...")

        url = "ws://%s:%s" % (config["analytics"]["host"], config["analytics"]["port"])

        runner = ApplicationRunner(url=url, realm=config["analytics"]["realm"])
        runner.run(AnalyticsElasticsearchWAMPComponent)


class AnalyticsElasticsearchWAMPComponent(ApplicationSession):
    def __init__(self, c=None):
        super().__init__(c)

        self.es_client = Elasticsearch(hosts=config["elasticsearch"]["hosts"])
        self.event_buffer = list()

    def onConnect(self):
        self.join(config["analytics"]["realm"], ["wampcra"], config["analytics"]["auth"]["username"])

    def onDisconnect(self):
        print("Disconnected from Crossbar!")

    def onChallenge(self, challenge):
        secret = config["analytics"]["auth"]["password"]
        signature = auth.compute_wcs(secret.encode('utf8'), challenge.extra['challenge'].encode('utf8'))

        return signature.decode('ascii')

    async def onJoin(self, details):

        async def on_event_message(event):
            if not isinstance(event, dict):
                return None

            event["uuid"] = str(uuid.uuid4())

            self.es_client.index(
                index=f"serpent:{config['analytics']['topic']}:events".lower(),
                doc_type="event",
                body=event,
                id=event["uuid"]
            )

        self.subscribe(
            on_event_message,
            config["analytics"]["topic"]
        )
