from serpent.game_api import GameAPI

from serpent.input_controller import KeyboardKey, KeyboardEvent, KeyboardEvents
from serpent.input_controller import MouseButton, MouseEvent, MouseEvents


class MyGameAPI(GameAPI):
    # A GameAPI is intended to contain functions and pieces of data that are applicable to the 
    # game and not agent or environment specific (e.g. Game inputs, Frame processing)

    def __init__(self, game=None):
        super().__init__(game=game)

        # SAMPLE - Replace with your own game inputs!
        self.game_inputs = {
            "MOVEMENT": {
                "MOVE UP": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_W)
                ],
                "MOVE LEFT": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_A)
                ],
                "MOVE DOWN": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_S)
                ],
                "MOVE RIGHT": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_D)
                ],
                "MOVE TOP-LEFT": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_W),
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_A)
                ],
                "MOVE TOP-RIGHT": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_W),
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_D)
                ],
                "MOVE DOWN-LEFT": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_S),
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_A)
                ],
                "MOVE DOWN-RIGHT": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_S),
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_D)
                ],
                "DON'T MOVE": []
            },
            "SHOOTING": {
                "SHOOT UP": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_UP)
                ],
                "SHOOT LEFT": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_LEFT)
                ],
                "SHOOT DOWN": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_DOWN)
                ],
                "SHOOT RIGHT": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_RIGHT)
                ],
                "DON'T SHOOT": []
            }
        }

    def my_api_function(self):
        pass

    class MyAPINamespace:

        @classmethod
        def my_namespaced_api_function(cls):
            api = MyGameAPI.instance
