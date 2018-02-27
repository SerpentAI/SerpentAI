import time
import collections


class Environment:

    def __init__(self, name, game_api=None, input_controller=None):
        self.name = name

        self.game_api = game_api
        self.input_controller = input_controller

        self.game_state = dict()

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

    def new_episode(self, maximum_steps=None, reset=False):
        self.recent_game_inputs = collections.deque(list(), maxlen=10)

        self.episode_steps = 0
        self.episode_maximum_steps = maximum_steps

        self.episode_started_at = time.time()

        if not reset:
            self.episode += 1

    def episode_step(self):
        self.episode_steps += 1
        self.total_steps += 1

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

    def clear_input(self):
        # TODO: Mouse support
        self.input_controller.handle_keys([])
