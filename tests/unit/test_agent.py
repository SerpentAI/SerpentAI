import pytest

from serpent.machine_learning.reinforcement_learning.agent import Agent

from serpent.input_controller import KeyboardKey, KeyboardEvent, KeyboardEvents

from serpent.enums import InputControlTypes

from serpent.utilities import SerpentError


class AgentTest(Agent):

    def __init__(self, name, game_inputs=None, callbacks=None):
        super().__init__(name, game_inputs=game_inputs, callbacks=callbacks)


class TestAgent:
    def setup_method(self, method):
        self.agent_game_inputs_simple_discrete = AgentTest(
            "TEST",
            game_inputs=[
                {
                    "control_type": InputControlTypes.DISCRETE,
                    "inputs": {
                        "A": [KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_A)],
                        "B": [KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_B)]
                    }
                }
            ]
        )

        self.agent_game_inputs_complex_discrete = AgentTest(
            "TEST",
            game_inputs=[
                {
                    "control_type": InputControlTypes.DISCRETE,
                    "inputs": {
                        "A": [KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_A)],
                        "B": [KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_B)]
                    }
                },
                {
                    "control_type": InputControlTypes.DISCRETE,
                    "inputs": {
                        "C": [KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_C)],
                        "D": [KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_D)],
                        "E": [KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_E)]
                    }
                }
            ]
        )

        self.agent_game_inputs_complex_mixed = AgentTest(
            "TEST",
            game_inputs=[
                {
                    "name": "FIRST",
                    "control_type": InputControlTypes.DISCRETE,
                    "inputs": {
                        "A": [KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_A)],
                        "B": [KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_B)]
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

    def test_agent_should_only_accept_game_inputs_as_lists(self):
        with pytest.raises(SerpentError):
            AgentTest("TEST", game_inputs=None)

        with pytest.raises(SerpentError):
            AgentTest("TEST", game_inputs={})

        AgentTest("TEST", game_inputs=[])

    def test_agent_should_generate_game_input_mappings_with_a_single_discrete_space(self):
        assert self.agent_game_inputs_simple_discrete.game_inputs_mappings == [
            {0: "A", 1: "B"}
        ]

    def test_agent_should_generate_game_input_mappings_with_multiple_discrete_spaces(self):
        assert self.agent_game_inputs_complex_discrete.game_inputs_mappings == [
            {0: "A", 1: "B"},
            {0: "C", 1: "D", 2: "E"}
        ]

    def test_agent_should_generate_game_input_mappings_with_mixed_spaces(self):
        assert self.agent_game_inputs_complex_mixed.game_inputs_mappings == [
            {0: "A", 1: "B"},
            None,
            {0: "C", 1: "D", 2: "E"}
        ]
