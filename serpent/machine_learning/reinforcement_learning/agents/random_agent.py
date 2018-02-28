from serpent.machine_learning.reinforcement_learning.agent import Agent

import random


class RandomAgent(Agent):

    def __init__(self, name, game_inputs=None, callbacks=None, seed=None):
        super().__init__(name, game_inputs=game_inputs, callbacks=callbacks)

        if seed is not None:
            random.seed(seed)

    def generate_action(self, state, **kwargs):
        label = random.choice(list(self.game_inputs.keys()))
        return label, self.game_inputs[label]
