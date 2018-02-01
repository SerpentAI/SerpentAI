import pickle
import time

from redis import StrictRedis

from serpent.config import config

from serpent.input_controller import keyboard_module_scan_code_mapping
from serpent.utilities import is_windows

from sneakysnek.recorder import Recorder
from sneakysnek.keyboard_event import KeyboardEvent, KeyboardEvents
from sneakysnek.mouse_event import MouseEvent, MouseEvents


redis_client = StrictRedis(**config["redis"])


class InputRecorder:

    redis_key = config["input_recorder"]["redis_key"]
    redis_key_pause = f"{redis_key}:PAUSED"
    redis_key_stop = f"{redis_key}:STOPPED"

    def __init__(self):
        self.active_keys = set()
        self.recorder = None

        self.redis_key = self.__class__.redis_key
        self.redis_key_pause = self.__class__.redis_key_pause
        self.redis_key_stop = self.__class__.redis_key_stop
        
        redis_client.delete(self.redis_key)
        redis_client.delete(self.redis_key_pause)
        redis_client.delete(self.redis_key_stop)

    def start(self):
        self.recorder = Recorder.record(self._on_input_event)

        while True:
            time.sleep(1)

    def stop(self):
        self.recorder.stop()

    def _on_input_event(self, event):
        if redis_client.get(self.redis_key_pause) == b"1":
            return None

        if redis_client.get(self.redis_key_stop) == b"1":
            self.stop()
            return None

        if isinstance(event, KeyboardEvent):
            if event.event == KeyboardEvents.DOWN:
                if event.keyboard_key.name in self.active_keys:
                    return None

                self.active_keys.add(event.keyboard_key.name)
            elif event.event == KeyboardEvents.UP:
                if event.keyboard_key.name in self.active_keys:
                    self.active_keys.remove(event.keyboard_key.name)

            event = {
                "type": "keyboard",
                "name": f"{event.keyboard_key.name}-{event.event.value.upper()}", 
                "timestamp": event.timestamp
            }

            print(event)
            event = pickle.dumps(event)

            redis_client.rpush(config["input_recorder"]["redis_key"], event)
        elif isinstance(event, MouseEvent):
            event = {
                "type": "mouse",
                "name": event.event.name,
                "button": event.button.name if event.button else None,
                "direction": event.direction if event.direction else None,
                "velocity": event.velocity if event.velocity else None,
                "x": event.x,
                "y": event.y,
                "timestamp": event.timestamp
            }

            print(event)
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
