from redis import StrictRedis
from datetime import datetime
from pprint import pprint

from serpent.config import config

import json


class AnalyticsClientError(BaseException):
    pass


class AnalyticsClient:

    def __init__(self, project_key=None):
        if project_key is None:
            raise AnalyticsClientError("'project_key' kwarg is expected...")

        self.project_key = project_key
        self.redis_client = StrictRedis(**config["redis"])

        self.broadcast = config["analytics"].get("broadcast", False)
        self.debug = config["analytics"].get("debug", False)

        self.event_whitelist = config["analytics"].get("event_whitelist")

    @property
    def redis_key(self):
        return f"SERPENT:{self.project_key}:EVENTS"

    def track(self, event_key=None, data=None, timestamp=None):
        if self.event_whitelist is None or event_key in self.event_whitelist:
            event = {
                "project_key": self.project_key,
                "event_key": event_key,
                "data": data,
                "timestamp": timestamp if timestamp is not None else datetime.utcnow().isoformat()
            }

            if self.debug:
                pprint(event)

            if self.broadcast:
                self.redis_client.lpush(self.redis_key, json.dumps(event))
