from serpent.input_controller import InputController


class GameAPI:
    instance = None

    def __init__(self, game=None):
        self.game = game

        if not self.game.is_launched:
            self.game.launch(dry_run=True)

        self.input_controller = InputController(game=game)

        self.__class__.instance = self
