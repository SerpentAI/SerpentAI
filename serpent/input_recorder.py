import pickle
import keyboard

from redis import StrictRedis

from serpent.config import config

from serpent.input_controller import keyboard_module_scan_code_mapping


redis_client = StrictRedis(**config["redis"])


class InputRecorder:

    redis_key = config["input_recorder"]["redis_key"]
    redis_key_pause = f"{redis_key}:PAUSED"
    redis_key_stop = f"{redis_key}:STOPPED"

    def __init__(self):
        self.active_keys = set()

        self.redis_key = self.__class__.redis_key
        self.redis_key_pause = self.__class__.redis_key_pause
        self.redis_key_stop = self.__class__.redis_key_stop
        
        redis_client.delete(self.redis_key)

    def start(self):
        keyboard.hook(self._on_keyboard_event)

        while True:
            pass

    def stop(self):
        keyboard.unhook(self._on_keyboard_event)

    def _on_keyboard_event(self, keyboard_event):
        if redis_client.get(self.redis_key_pause) == b"1":
            return None

        if redis_client.get(self.redis_key_stop) == b"1":
            self.stop()
            return None

        key_name = keyboard_module_scan_code_mapping.get(keyboard_event.scan_code)

        if keyboard_event.event_type == "down":
            if key_name.name in self.active_keys:
                return None

            self.active_keys.add(key_name.name)
        elif keyboard_event.event_type == "up":
            if key_name.name in self.active_keys:
                self.active_keys.remove(key_name.name)

        event = {"name": f"{key_name.name}-{keyboard_event.event_type.upper()}", "timestamp": keyboard_event.time}
        event = pickle.dumps(event)

        redis_client.rpush(config["input_recorder"]["redis_key"], event)

    @classmethod
    def pause_input_recording(cls):
        redis_client.set(cls.redis_key_pause, 1)

    @classmethod
    def resume_input_recording(cls):
        redis_client.set(cls.redis_key_pause, 0)

    @classmethod
    def stop_input_recording(cls):
        redis_client.set(cls.redis_key_stop, 1)
