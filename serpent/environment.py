import time
import collections

from serpent.input_controller import KeyboardEvent, KeyboardEvents
from serpent.input_controller import MouseEvent, MouseEvents

from serpent.config import config

from serpent.analytics_client import AnalyticsClient


class Environment:

    def __init__(self, name, game_api=None, input_controller=None):
        self.name = name

        self.game_api = game_api
        self.input_controller = input_controller

        self.game_state = dict()

        self.analytics_client = AnalyticsClient(project_key=config["analytics"]["topic"])

        self.reset()

    @property
    def episode_duration(self):
        return time.time() - self.episode_started_at

    @property
    def episode_over(self):
        if self.episode_maximum_steps is not None:
            return self.episode_steps >= self.episode_maximum_steps
        else:
            return False

    @property
    def new_episode_data(self):
        return dict()

    @property
    def end_episode_data(self):
        return dict()

    def new_episode(self, maximum_steps=None, reset=False):
        self.episode_steps = 0
        self.episode_maximum_steps = maximum_steps

        self.episode_started_at = time.time()

        if not reset:
            self.episode += 1

        self.analytics_client.track(
            event_key="NEW_EPISODE",
            data={
                "episode": self.episode,
                "episode_data": self.new_episode_data,
                "maximum_steps": self.episode_maximum_steps
            }
        )

    def end_episode(self):
        self.analytics_client.track(
            event_key="END_EPISODE",
            data={
                "episode": self.episode,
                "episode_data": self.end_episode_data,
                "episode_steps": self.episode_steps,
                "maximum_steps": self.episode_maximum_steps
            }
        )

    def episode_step(self):
        self.episode_steps += 1
        self.total_steps += 1

        self.analytics_client.track(
            event_key="EPISODE_STEP",
            data={
                "episode": self.episode,
                "episode_step": self.episode_steps,
                "total_steps": self.total_steps
            }
        )

    def reset(self):
        self.total_steps = 0

        self.episode = 0
        self.episode_steps = 0

        self.episode_maximum_steps = None

        self.episode_started_at = None

    def update_game_state(self):
        raise NotImplementedError()

    def perform_input(self, actions):
        discrete_keyboard_keys = set()
        discrete_keyboard_labels = set()

        continuous_keyboard_events = list()

        for label, game_input, value in actions:
            if not len(game_input):
                continue

            # Discrete Space
            if value is None:
                for game_input_item in game_input:
                    if isinstance(game_input_item, KeyboardEvent):
                        if game_input_item.event == KeyboardEvents.DOWN:
                            discrete_keyboard_keys.add(game_input_item.keyboard_key)
                            discrete_keyboard_labels.add(label)
                    # TODO: Mouse Support
                    elif isinstance(game_input_item, MouseEvent):
                        pass
            # Continuous Space
            else:
                if isinstance(game_input[0], KeyboardEvent):
                    continuous_keyboard_events.append((label, game_input, value))
                elif isinstance(game_input[0], MouseEvent):
                    pass

        # Perform Discrete Keyboard Actions
        if len(discrete_keyboard_keys):
            self.input_controller.handle_keys(list(keyboard_keys))

            self.analytics_client.track(
                event_key="GAME_INPUT",
                data={
                    "keyboard": {
                        "type": "DISCRETE",
                        "label": " - ".join(sorted(discrete_keyboard_labels)),
                        "inputs": sorted([keyboard_key.value for keyboard_key in discrete_keyboard_keys])
                    },
                    "mouse": {}
                }
            )

        # Perform Continuous Keyboard Actions (Blocking! Need async input controller...)
        for label, events, duration in continuous_keyboard_events:
            self.input_controller.tap_keys(
                [event.keyboard_key for event in events],
                duration=duration
            )

            self.analytics_client.track(
                event_key="GAME_INPUT",
                data={
                    "keyboard": {
                        "type": "CONTINUOUS",
                        "label": label,
                        "inputs": sorted([event.keyboard_key.value for event in events]),
                        "duration": duration
                    },
                    "mouse": {}
                }
            )

    def clear_input(self):
        # TODO: Mouse support
        self.input_controller.handle_keys([])
