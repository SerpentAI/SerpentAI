import time
import collections

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
        self.recent_game_inputs = collections.deque(list(), maxlen=10)

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
        self.recent_game_inputs = None

        self.total_steps = 0

        self.episode = 0
        self.episode_steps = 0

        self.episode_maximum_steps = None

        self.episode_started_at = None

    def update_game_state(self):
        raise NotImplementedError()

    def perform_input(self, label, game_input):
        # TODO: Mouse support
        # TODO: Consider using sneakysnek events?

        self.input_controller.handle_keys(game_input)
        self.recent_game_inputs.appendleft(label)

        self.analytics_client.track(
            event_key="GAME_INPUT",
            data={
                "label": label,
                "inputs": [i.value for i in game_input]
            }
        )

    def clear_input(self):
        # TODO: Mouse support
        self.input_controller.handle_keys([])
