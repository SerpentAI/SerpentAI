import pytest

from serpent.machine_learning.reinforcement_learning.agents.random_agent import RandomAgent

from serpent.input_controller import KeyboardKey, KeyboardEvent, KeyboardEvents

from serpent.enums import InputControlTypes

from serpent.utilities import SerpentError


class RandomAgentTest(RandomAgent):

    def __init__(self, name, game_inputs=None, callbacks=None, seed=None):
        super().__init__(name, game_inputs=game_inputs, callbacks=callbacks, seed=seed)


class TestRandomAgent:
    def setup_method(self, method):
        self.random_agent = RandomAgentTest(
            "TEST",
            game_inputs=[
                {
                    "name": "FIRST",
                    "control_type": InputControlTypes.DISCRETE,
                    "inputs": {
                        "A": [KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_A)],
                        "B": [KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_A)]
                    }
                },
                {   
                    "name": "SECOND",
                    "control_type": InputControlTypes.CONTINUOUS,
                    "inputs": {
                        "events": [KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_A)],
                        "minimum": 0.001,
                        "maximum": 1.0
                    }
                },
                {
                    "name": "THIRD",
                    "control_type": InputControlTypes.DISCRETE,
                    "inputs": {
                        "C": [KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_C)],
                        "D": [KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_D)],
                        "E": [KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_E)]
                    }
                }
            ]
        )

    def teardown_method(self, method):
        pass

    def test_random_agent_should_generate_valid_actions_for_both_input_control_types(self):
        actions = self.random_agent.generate_actions(None)

        assert isinstance(actions, list)
        assert len(actions) == 3

        assert actions[0][0] in ["A", "B"]
        assert isinstance(actions[0][1], list)
        assert isinstance(actions[0][1][0], KeyboardEvent)
        assert actions[0][1][0].keyboard_key in [KeyboardKey.KEY_A, KeyboardKey.KEY_B]

        assert actions[1][0] == "SECOND"
        assert isinstance(actions[1][1], list)
        assert isinstance(actions[1][1][0], KeyboardEvent)
        assert actions[1][1][0].keyboard_key == KeyboardKey.KEY_A

        assert isinstance(actions[1][2], float)
        assert actions[1][2] >= 0.001 and actions[1][2] <= 1.0

        assert actions[2][0] in ["C", "D", "E"]
        assert isinstance(actions[2][1], list)
        assert isinstance(actions[2][1][0], KeyboardEvent)
        assert actions[2][1][0].keyboard_key in [KeyboardKey.KEY_C, KeyboardKey.KEY_D, KeyboardKey.KEY_E]

