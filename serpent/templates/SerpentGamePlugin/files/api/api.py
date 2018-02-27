from serpent.game_api import GameAPI

from serpent.input_controller import KeyboardKey


class MyGameAPI(GameAPI):
    # A GameAPI is intended to contain functions and pieces of data that are applicable to the 
    # game and not agent or environment specific (e.g. Game inputs, Frame processing)

    def __init__(self, game=None):
        super().__init__(game=game)

        # SAMPLE - Replace with your own game inputs!
        self.game_inputs = {
            "MOVEMENT": {
                "MOVE UP": [KeyboardKey.KEY_W],
                "MOVE LEFT": [KeyboardKey.KEY_A],
                "MOVE DOWN": [KeyboardKey.KEY_S],
                "MOVE RIGHT": [KeyboardKey.KEY_D],
                "MOVE TOP-LEFT": [KeyboardKey.KEY_W, KeyboardKey.KEY_A],
                "MOVE TOP-RIGHT": [KeyboardKey.KEY_W, KeyboardKey.KEY_D],
                "MOVE DOWN-LEFT": [KeyboardKey.KEY_S, KeyboardKey.KEY_A],
                "MOVE DOWN-RIGHT": [KeyboardKey.KEY_S, KeyboardKey.KEY_D],
                "DON'T MOVE": []
            },
            "SHOOTING": {
                "SHOOT UP": [KeyboardKey.KEY_UP],
                "SHOOT LEFT": [KeyboardKey.KEY_LEFT],
                "SHOOT DOWN": [KeyboardKey.KEY_DOWN],
                "SHOOT RIGHT": [KeyboardKey.KEY_RIGHT],
                "DON'T SHOOT": []
            }
        }

    def my_api_function(self):
        pass

    class MyAPINamespace:

        @classmethod
        def my_namespaced_api_function(cls):
            api = MyGameAPI.instance
