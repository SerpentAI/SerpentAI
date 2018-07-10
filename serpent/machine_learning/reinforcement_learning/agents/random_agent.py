from serpent.machine_learning.reinforcement_learning.agent import Agent

from serpent.enums import InputControlTypes

import random
import enum


class RandomAgentModes(enum.Enum):
    OBSERVE = 0


class RandomAgent(Agent):

    def __init__(self, name, game_inputs=None, callbacks=None, seed=None):
        super().__init__(name, game_inputs=game_inputs, callbacks=callbacks)

        if seed is not None:
            random.seed(seed)

        self.mode = RandomAgentModes.OBSERVE

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

                size = 1

                if "size" in game_inputs_item["inputs"]:
                    size = game_inputs_item["inputs"]["size"]

                if size == 1:
                    input_value = random.uniform(
                        game_inputs_item["inputs"]["minimum"],
                        game_inputs_item["inputs"]["maximum"]
                    )
                else:
                    input_value = list()

                    for i in range(size):
                        input_value.append(
                            random.uniform(
                                game_inputs_item["inputs"]["minimum"],
                                game_inputs_item["inputs"]["maximum"]
                            )
                        )

                actions.append((label, action, input_value))

        for action in actions:
            self.analytics_client.track(
                event_key="AGENT_ACTION",
                data={
                    "label": action[0],
                    "action": [str(a) for a in action[1]],
                    "input_value": action[2]
                }
            )

        return actions
