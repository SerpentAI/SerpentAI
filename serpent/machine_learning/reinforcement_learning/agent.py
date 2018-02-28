

class Agent:

    def __init__(self, name, game_inputs=None, callbacks=None):
        self.name = name

        if game_inputs is None:
            raise SerpentError("'game_inputs' should be a dict...")

        # TODO: Support multiple actions
        self.game_inputs = game_inputs
        self.game_inputs_mapping = self._generate_game_inputs_mapping()

        self.callbacks = callbacks or dict()

        self.current_state = None

        self.current_reward = 0
        self.cumulative_reward = 0

    def generate_action(self, state, **kwargs):
        raise NotImplementedError()

    def observe(self, reward=0, **kwargs):
        if self.callbacks.get("before_observe") is not None:
            self.callbacks["before_observe"]()

        self.current_state = None

        self.current_reward = reward
        self.cumulative_reward += reward

        if self.callbacks.get("after_observe") is not None:
            self.callbacks["after_observe"]()

    def reset(self, **kwargs):
        self.current_state = None

        self.current_reward = 0
        self.cumulative_reward = 0

    def _generate_game_inputs_mapping(self):
        mapping = dict()

        for index, key in enumerate(self.game_inputs):
            mapping[index] = key

        return mapping
