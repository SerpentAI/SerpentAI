import asyncio

from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
from autobahn.wamp.types import RegisterOptions, SubscribeOptions
from autobahn.wamp import auth

from serpent.config import config

from pony.orm import *
from serpent.dashboard.models import *

import json


class DashboardAPIComponent:
    @classmethod
    def run(cls):
        print(f"Starting {cls.__name__}...")

        url = "ws://%s:%s" % (config["crossbar"]["host"], config["crossbar"]["port"])

        runner = ApplicationRunner(url=url, realm=config["crossbar"]["realm"])
        runner.run(DashboardAPIWAMPComponent)


class DashboardAPIWAMPComponent(ApplicationSession):
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

        @db_session
        def list_dashboards():
            dashboards = Dashboard.select(lambda d: True).order_by(lambda d: d.name)[:]
            return {"dashboards": [dashboard.as_list_json() for dashboard in dashboards]}

        @db_session
        def fetch_dashboard(uuid):
            dashboard = Dashboard.get(uuid=UUID(uuid))

            if dashboard is None:
                return {"error": f"No Dashboard found with uuid '{uuid}'..."}

            return {"dashboard": dashboard.as_json()}

        @db_session
        def create_dashboard(dashboard_data):
            dashboard = Dashboard.get(name=dashboard_data.get("name"))

            if dashboard is not None:
                return {"error": f"A Dashboard with name '{dashboard.name}' already exists..."}

            dashboard = Dashboard.create(dashboard_data)

            return {"dashboard": dashboard.as_list_json()}

        @db_session
        def delete_dashboard(uuid):
            dashboard = Dashboard.get(uuid=UUID(uuid))

            if dashboard is None:
                return {"error": f"No Dashboard found with uuid '{uuid}'..."}

            dashboard.delete()

            commit()

            return {"dashboard": None}

        @db_session
        def create_dashboard_metric(dashboard_uuid, metric_data):
            dashboard = Dashboard.get(uuid=UUID(dashboard_uuid))

            if dashboard is None:
                return {"error": f"No Dashboard found with uuid '{dashboard_uuid}'..."}

            metric = Metric(**{
                **metric_data,
                "dashboard": dashboard,
                "x": 0,
                "y": 0,
                "w": 9,
                "h": 5
            })

            commit()

            return {"metric": metric.as_json()}

        @db_session
        def update_dashboard_metric(dashboard_uuid, metric_data):
            dashboard = Dashboard.get(uuid=UUID(dashboard_uuid))

            if dashboard is None:
                return {"error": f"No Dashboard found with uuid '{dashboard_uuid}'..."}

            metric_uuid = metric_data.pop("uuid")
            metric = Metric.get(uuid=UUID(metric_uuid))

            if metric is None:
                return {"error": f"No Metric found with uuid '{metric_uuid}'..."}

            metric.set(**metric_data)

            commit()

            return {"metric": metric.as_json()}

        @db_session
        def delete_dashboard_metric(uuid):
            metric = Metric.get(uuid=UUID(uuid))

            if metric is None:
                return {"error": f"No Dashboard Metric found with uuid '{uuid}'..."}

            metric.delete()

            commit()

            return {"metric": None}

        @db_session
        def save_dashboard_layout(uuid, layout):
            dashboard = Dashboard.get(uuid=UUID(uuid))

            if dashboard is None:
                return {"error": f"No Dashboard found with uuid '{uuid}'..."}

            dashboard.save_layout(layout)

            return {"dashboard": dashboard.as_json()}

        await self.register(list_dashboards, f"{config['crossbar']['realm']}.list_dashboards", options=RegisterOptions(invoke="roundrobin"))
        await self.register(fetch_dashboard, f"{config['crossbar']['realm']}.fetch_dashboard", options=RegisterOptions(invoke="roundrobin"))
        await self.register(create_dashboard, f"{config['crossbar']['realm']}.create_dashboard", options=RegisterOptions(invoke="roundrobin"))
        await self.register(delete_dashboard, f"{config['crossbar']['realm']}.delete_dashboard", options=RegisterOptions(invoke="roundrobin"))
        await self.register(create_dashboard_metric, f"{config['crossbar']['realm']}.create_dashboard_metric", options=RegisterOptions(invoke="roundrobin"))
        await self.register(update_dashboard_metric, f"{config['crossbar']['realm']}.update_dashboard_metric", options=RegisterOptions(invoke="roundrobin"))
        await self.register(delete_dashboard_metric, f"{config['crossbar']['realm']}.delete_dashboard_metric", options=RegisterOptions(invoke="roundrobin"))
        await self.register(save_dashboard_layout, f"{config['crossbar']['realm']}.save_dashboard_layout", options=RegisterOptions(invoke="roundrobin"))


if __name__ == "__main__":
    DashboardAPIComponent.run()
