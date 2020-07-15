from serpent.dashboard.models import *

default_metrics = [
    dict(
        label="Episode",
        display_type="NUMBER",
        event="NEW_EPISODE",
        event_key="episode",
        x=0,
        y=0,
        w=9,
        h=5
    ),
    dict(
        label="Episode Steps",
        display_type="NUMBER",
        event="EPISODE_STEP",
        event_key="episode_step",
        x=0,
        y=0,
        w=9,
        h=5
    ),
    dict(
        label="Total Steps",
        display_type="NUMBER",
        event="EPISODE_STEP",
        event_key="total_steps",
        x=0,
        y=0,
        w=9,
        h=5
    ),
    dict(
        label="Reward",
        display_type="NUMBER",
        event="REWARD",
        event_key="reward",
        x=0,
        y=0,
        w=9,
        h=5
    ),
    dict(
        label="Episode Reward",
        display_type="NUMBER",
        event="REWARD",
        event_key="total_reward",
        x=0,
        y=0,
        w=9,
        h=5
    ),
    dict(
        label="Rewards",
        display_type="LINE_CHART",
        event="REWARD",
        event_key="reward",
        clear_event="NEW_EPISODE",
        x=0,
        y=0,
        w=27,
        h=5
    ),
    dict(
        label="Episode Rewards",
        display_type="LINE_CHART",
        event="TOTAL_REWARD",
        event_key="reward",
        x=0,
        y=0,
        w=27,
        h=5
    )
]

with db_session:
    for metric in default_metrics:
        default_metric = DefaultMetric.get(label=metric.get("label"))

        if default_metric is None:
            DefaultMetric(**metric)

    commit()
