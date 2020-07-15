from serpent.input_controller import InputController

from serpent.utilities import SerpentError

import itertools


class GameAPI:
    instance = None

    def __init__(self, game=None):
        self.game = game

        if not self.game.is_launched:
            self.game.launch(dry_run=True)

        self.input_controller = InputController(game=game, backend=game.input_controller)

        self.game_inputs = dict()

        self.__class__.instance = self

    def combine_game_inputs(self, combination):
        """ Combine game input axes in a single flattened collection

        Args:
        combination [list] -- A combination of valid game input axis keys
        """

        # Validation
        if not isinstance(combination, list):
            raise SerpentError("'combination' needs to be a list")

        for entry in combination:
            if isinstance(entry, list):
                for entry_item in entry:
                    if entry_item not in self.game_inputs:
                        raise SerpentError("'combination' entries need to be valid members of self.game_input...")
            else:
                if entry not in self.game_inputs:
                    raise SerpentError("'combination' entries need to be valid members of self.game_input...")

        # Concatenate Grouped Axes (if needed)
        game_input_axes = list()

        for entry in combination:
            if isinstance(entry, str):
                game_input_axes.append(self.game_inputs[entry])
            elif isinstance(entry, list):
                concatenated_game_input_axis = dict()

                for entry_item in entry:
                    concatenated_game_input_axis = {**concatenated_game_input_axis, **self.game_inputs[entry_item]}

                game_input_axes.append(concatenated_game_input_axis)

        # Combine Game Inputs
        game_inputs = dict()

        if not len(game_input_axes):
            return game_inputs

        for keys in itertools.product(*game_input_axes):
            compound_label = list()
            game_input = list()

            for index, key in enumerate(keys):
                compound_label.append(key)
                game_input += game_input_axes[index][key]

            game_inputs[" - ".join(compound_label)] = game_input

        return game_inputs
