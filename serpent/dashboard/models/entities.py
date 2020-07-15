from uuid import UUID, uuid4
from pony.orm import *

import os


db = Database()


class Dashboard(db.Entity):
    uuid = PrimaryKey(UUID, default=uuid4, auto=True)
    name = Optional(str)
    project_key = Optional(str)
    game_width = Optional(int)
    game_height = Optional(int)
    metrics = Set("Metric")

    @property
    def game_resolution(self):
        return self.game_width, self.game_height

    def as_list_json(self):
        return dict(
            uuid=str(self.uuid),
            name=self.name,
            project_key=self.project_key,
            game_resolution=self.game_resolution,
            metrics=len(self.metrics)
        )

    def as_json(self):
        return dict(
            uuid=str(self.uuid),
            name=self.name,
            project_key=self.project_key,
            game_resolution=self.game_resolution,
            metrics=[metric.as_json() for metric in self.metrics]
        )

    @db_session
    def save_layout(self, layout):
        for layout_item in layout:
            if layout_item["i"] == "game":
                continue

            metric = Metric.get(uuid=UUID(layout_item["i"]))

            if metric is not None:
                metric.set(
                    x=layout_item["x"],
                    y=layout_item["y"],
                    w=layout_item["w"],
                    h=layout_item["h"]
                )

        commit()

    @classmethod
    @db_session
    def create(cls, data):
        dashboard = Dashboard(
            name=data.get("name"),
            project_key=data.get("project_key"),
            game_width=data.get("game_width"),
            game_height=data.get("game_height")
        )

        commit()

        default_metrics = DefaultMetric.select(lambda dm: True)[:]

        for default_metric in default_metrics:
            metric = Metric(
                label=default_metric.label,
                display_type=default_metric.display_type,
                event=default_metric.event,
                event_key=default_metric.event_key,
                clear_event=default_metric.clear_event,
                x=default_metric.x,
                y=default_metric.y,
                w=default_metric.w,
                h=default_metric.h,
                dashboard=dashboard
            )

        commit()

        return dashboard


class Metric(db.Entity):
    uuid = PrimaryKey(UUID, default=uuid4, auto=True)
    label = Optional(str)
    display_type = Optional(str)
    event = Optional(str)
    event_key = Optional(str)
    clear_event = Optional(str, nullable=True)
    x = Optional(int)
    y = Optional(int)
    w = Optional(int)
    h = Optional(int)
    dashboard = Required("Dashboard")

    def as_json(self):
        return dict(
            uuid=str(self.uuid),
            label=self.label,
            display_type=self.display_type,
            event=self.event,
            event_key=self.event_key,
            clear_event=self.clear_event,
            x=self.x,
            y=self.y,
            w=self.w,
            h=self.h
        )


class DefaultMetric(db.Entity):
    uuid = PrimaryKey(UUID, default=uuid4, auto=True)
    label = Optional(str)
    display_type = Optional(str)
    event = Optional(str)
    event_key = Optional(str)
    clear_event = Optional(str, nullable=True)
    x = Optional(int)
    y = Optional(int)
    w = Optional(int)
    h = Optional(int)


try:
    db.bind(provider="sqlite", filename=f"{os.getcwd()}\\dashboard\\database.sqlite", create_db=True)

    db.generate_mapping(create_tables=True)
except Exception as e:
    print(e)
