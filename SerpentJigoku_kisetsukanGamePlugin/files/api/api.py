from serpent.game_api import GameAPI

from serpent.input_controller import KeyboardEvent, KeyboardEvents, KeyboardKey

class Jigoku_kisetsukanAPI(GameAPI):

    def __init__(self, game=None):
        super().__init__(game=game)
        
        self.game_inputs = {
            "MOVEMENT": {
                "UP": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_UP)
                ],
                "LEFT": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_LEFT)
                ],
                "DOWN": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_DOWN)
                ],
                "RIGHT": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_RIGHT)
                ],
                "UP-LEFT": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_UP),
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_LEFT)
                ],
                "UP-RIGHT": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_UP),
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_RIGHT)
                ],
                "DOWN-LEFT": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_DOWN),
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_LEFT)
                ],
                "DOWN-RIGHT": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_DOWN),
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_RIGHT)
                ],
                "UP-FOCUS": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_UP),
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_LEFT_SHIFT)
                ],
                "LEFT-FOCUS": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_LEFT),
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_LEFT_SHIFT)
                ],
                "DOWN-FOCUS": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_DOWN),
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_LEFT_SHIFT)
                ],
                "RIGHT-FOCUS": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_RIGHT),
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_LEFT_SHIFT)
                ],
                "UP-LEFT-FOCUS": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_UP),
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_LEFT),
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_LEFT_SHIFT)
                ],
                "UP-RIGHT-FOCUS": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_UP),
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_RIGHT),
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_LEFT_SHIFT)
                ],
                "DOWN-LEFT-FOCUS": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_DOWN),
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_LEFT),
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_LEFT_SHIFT)
                ],
                "DOWN-RIGHT-FOCUS": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_DOWN),
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_RIGHT),
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_LEFT_SHIFT)
                ],
                "DON'T MOVE": []
            },
            "SHOOTING": {
                "SHOOT": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_Z)
                ],
                "SHOOT-FOCUS": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_Z),
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_LEFT_SHIFT)
                ],
                "AURA": [
                    KeyboardEvent(KeyboardEvents.DOWN, KeyboardKey.KEY_X)
                    ],
                "DON'T SHOOT": []
            }
        }


    def my_api_function(self):
        pass

    class MyAPINamespace:

        @classmethod
        def my_namespaced_api_function(cls):
            api = Jigoku_kisetsukanAPI.instance