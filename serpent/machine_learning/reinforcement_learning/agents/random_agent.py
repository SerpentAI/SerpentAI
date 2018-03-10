from serpent.machine_learning.reinforcement_learning.agent import Agent

from serpent.enums import InputControlTypes

import random


class RandomAgent(Agent):

    def __init__(self, name, game_inputs=None, callbacks=None, seed=None):
        super().__init__(name, game_inputs=game_inputs, callbacks=callbacks)

        if seed is not None:
            random.seed(seed)

    def generate_actions(self, state, **kwargs):
        actions = list()

        for game_inputs_item in self.game_inputs:
            if game_inputs_item["control_type"] == InputControlTypes.DISCRETE:
                label = random.choice(list(game_inputs_item["inputs"].keys()))
                action = game_inputs_item["inputs"][label]

                actions.append((label, action, None))
            elif game_inputs_item["control_type"] == InputControlTypes.CONTINUOUS:
                label = game_inputs_item["name"]
                action = game_inputs_item["inputs"]["events"]
                input_value = random.uniform(
                    game_inputs_item["inputs"]["minimum"],
                    game_inputs_item["inputs"]["maximum"]
                )

                actions.append((label, action, input_value))

        return actions
