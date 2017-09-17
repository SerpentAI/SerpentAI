from redis import StrictRedis
from datetime import datetime

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

    @property
    def redis_key(self):
        return f"SERPENT:{self.project_key}:EVENTS"

    def track(self, event_key=None, data=None):
        event = {
            "project_key": self.project_key,
            "event_key": event_key,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }

        self.redis_client.lpush(self.redis_key, json.dumps(event))