from serpent.input_controller import InputController, MouseButton

from serpent.config import config

from redis import StrictRedis

import pickle


class ClientInputController(InputController):

    def __init__(self, game=None, **kwargs):
        self.game = game
        self.redis_client = StrictRedis(**config["redis"])

    # Keyboard Actions
    def handle_keys(self, key_collection, **kwargs):
        payload = ("handle_keys", key_collection, kwargs)
        self.redis_client.lpush(config["input_controller"]["redis_key"], pickle.dumps(payload))

    def tap_keys(self, keys, duration=0.05, **kwargs):
        payload = ("tap_keys", keys, duration, kwargs)
        self.redis_client.lpush(config["input_controller"]["redis_key"], pickle.dumps(payload))

    def tap_key(self, key, duration=0.05, **kwargs):
        payload = ("tap_key", key, duration, kwargs)
        self.redis_client.lpush(config["input_controller"]["redis_key"], pickle.dumps(payload))

    def press_keys(self, keys, **kwargs):
        payload = ("press_keys", keys, kwargs)
        self.redis_client.lpush(config["input_controller"]["redis_key"], pickle.dumps(payload))

    def press_key(self, key, **kwargs):
        payload = ("press_key", key, kwargs)
        self.redis_client.lpush(config["input_controller"]["redis_key"], pickle.dumps(payload))

    def release_keys(self, keys, **kwargs):
        payload = ("release_keys", keys, kwargs)
        self.redis_client.lpush(config["input_controller"]["redis_key"], pickle.dumps(payload))

    def release_key(self, key, **kwargs):
        payload = ("release_key", key, kwargs)
        self.redis_client.lpush(config["input_controller"]["redis_key"], pickle.dumps(payload))

    def type_string(self, string, duration=0.05, **kwargs):
        payload = ("type_string", string, duration, kwargs)
        self.redis_client.lpush(config["input_controller"]["redis_key"], pickle.dumps(payload))

    # Mouse Actions
    def move(self, x=None, y=None, duration=0.25, absolute=True, **kwargs):
        payload = ("move", x, y, duration, absolute, kwargs)
        self.redis_client.lpush(config["input_controller"]["redis_key"], pickle.dumps(payload))

    def click_down(self, button=MouseButton.LEFT, **kwargs):
        payload = ("click_down", button, kwargs)
        self.redis_client.lpush(config["input_controller"]["redis_key"], pickle.dumps(payload))

    def click_up(self, button=MouseButton.LEFT, **kwargs):
        payload = ("click_up", button, kwargs)
        self.redis_client.lpush(config["input_controller"]["redis_key"], pickle.dumps(payload))

    def click(self, button=MouseButton.LEFT, duration=0.25, **kwargs):
        payload = ("click", button, duration, kwargs)
        self.redis_client.lpush(config["input_controller"]["redis_key"], pickle.dumps(payload))

    def click_screen_region(self, button=MouseButton.LEFT, screen_region=None, **kwargs):
        payload = ("click_screen_region", button, screen_region, kwargs)
        self.redis_client.lpush(config["input_controller"]["redis_key"], pickle.dumps(payload))

    def click_sprite(self, button=MouseButton.LEFT, sprite=None, game_frame=None, **kwargs):
        payload = ("click_sprite", button, sprite, game_frame, kwargs)
        self.redis_client.lpush(config["input_controller"]["redis_key"], pickle.dumps(payload))

    # Requires the Serpent OCR module
    def click_string(self, query_string, button=MouseButton.LEFT, game_frame=None, fuzziness=2, ocr_preset=None, **kwargs):
        payload = ("click_string", query_string, button, game_frame, fuzziness, ocr_preset, kwargs)
        self.redis_client.lpush(config["input_controller"]["redis_key"], pickle.dumps(payload))

    def drag(self, button=MouseButton.LEFT, x0=None, y0=None, x1=None, y1=None, duration=1, **kwargs):
        payload = ("drag", button, x0, y0, x1, y1, duration, kwargs)
        self.redis_client.lpush(config["input_controller"]["redis_key"], pickle.dumps(payload))

    def drag_screen_region_to_screen_region(self, button=MouseButton.LEFT, start_screen_region=None, end_screen_region=None, duration=1, **kwargs):
        payload = ("drag_screen_region_to_screen_region", button, start_screen_region, end_screen_region, duration, kwargs)
        self.redis_client.lpush(config["input_controller"]["redis_key"], pickle.dumps(payload))

    def scroll(self, clicks=1, direction="DOWN", **kwargs):
        payload = ("scroll", clicks, direction, kwargs)
        self.redis_client.lpush(config["input_controller"]["redis_key"], pickle.dumps(payload))
