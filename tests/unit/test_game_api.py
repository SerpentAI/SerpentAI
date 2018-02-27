import pytest

from serpent.game_api import GameAPI
from serpent.game import Game

from serpent.input_controller import KeyboardKey

from serpent.utilities import SerpentError


class GameAPITest(GameAPI):

    def __init__(self, game=None):
        super().__init__(game=game)

        self.game_inputs = {
            "1": {
                "A": [KeyboardKey.KEY_A],
                "B": [KeyboardKey.KEY_B]
            },
            "2": {
                "C": [KeyboardKey.KEY_C],
                "D": [KeyboardKey.KEY_D]
            },
            "3": {
                "E": [KeyboardKey.KEY_E]
            }
        }


class GameTest(Game):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def after_launch(self):
        pass

    def _discover_sprites(self):
        pass


class TestGameAPI:
    def setup_method(self, method):
        self.game = GameTest()
        self.game_api = GameAPITest(game=self.game)

    def teardown_method(self, method):
        pass

    def test_combine_game_inputs_combination_should_only_accept_lists(self):
        with pytest.raises(SerpentError):
            self.game_api.combine_game_inputs(123)

        with pytest.raises(SerpentError):
            self.game_api.combine_game_inputs("1")

        self.game_api.combine_game_inputs([])

    def test_combine_game_inputs_combination_entries_should_contain_valid_game_input_keys(self):
        with pytest.raises(SerpentError):
            self.game_api.combine_game_inputs(["A", "B"])

        with pytest.raises(SerpentError):
            self.game_api.combine_game_inputs(["A", ["B", "C"]])

        with pytest.raises(SerpentError):
            self.game_api.combine_game_inputs(["1", "B"])

        self.game_api.combine_game_inputs(["1"])
        self.game_api.combine_game_inputs(["1", "2", "3"])
        self.game_api.combine_game_inputs(["1", ["2", "3"]])

    def test_combine_game_inputs_should_handle_valid_combinations(self):
        assert self.game_api.combine_game_inputs([]) == dict()

        assert self.game_api.combine_game_inputs(["1"]) == {
            "A": [KeyboardKey.KEY_A],
            "B": [KeyboardKey.KEY_B]
        }

        assert self.game_api.combine_game_inputs(["2"]) == {
            "C": [KeyboardKey.KEY_C],
            "D": [KeyboardKey.KEY_D]
        }

        assert self.game_api.combine_game_inputs(["3"]) == {
            "E": [KeyboardKey.KEY_E]
        }

        assert self.game_api.combine_game_inputs(["1", "2"]) == {
            "A - C": [KeyboardKey.KEY_A, KeyboardKey.KEY_C],
            "A - D": [KeyboardKey.KEY_A, KeyboardKey.KEY_D],
            "B - C": [KeyboardKey.KEY_B, KeyboardKey.KEY_C],
            "B - D": [KeyboardKey.KEY_B, KeyboardKey.KEY_D]
        }

        assert self.game_api.combine_game_inputs(["1", "3"]) == {
            "A - E": [KeyboardKey.KEY_A, KeyboardKey.KEY_E],
            "B - E": [KeyboardKey.KEY_B, KeyboardKey.KEY_E]
        }

        assert self.game_api.combine_game_inputs(["1", ["2", "3"]]) == {
            "A - C": [KeyboardKey.KEY_A, KeyboardKey.KEY_C],
            "A - D": [KeyboardKey.KEY_A, KeyboardKey.KEY_D],
            "A - E": [KeyboardKey.KEY_A, KeyboardKey.KEY_E],
            "B - C": [KeyboardKey.KEY_B, KeyboardKey.KEY_C],
            "B - D": [KeyboardKey.KEY_B, KeyboardKey.KEY_D],
            "B - E": [KeyboardKey.KEY_B, KeyboardKey.KEY_E]
        }

        assert self.game_api.combine_game_inputs(["1", "2", "3"]) == {
            "A - C - E": [KeyboardKey.KEY_A, KeyboardKey.KEY_C, KeyboardKey.KEY_E],
            "A - D - E": [KeyboardKey.KEY_A, KeyboardKey.KEY_D, KeyboardKey.KEY_E],
            "B - C - E": [KeyboardKey.KEY_B, KeyboardKey.KEY_C, KeyboardKey.KEY_E],
            "B - D - E": [KeyboardKey.KEY_B, KeyboardKey.KEY_D, KeyboardKey.KEY_E]
        }