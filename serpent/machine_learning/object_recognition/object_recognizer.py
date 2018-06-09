import enum
import os

from serpent.utilities import SerpentError


class ObjectRecognizers(enum.Enum):
    LUMINOTH = 0


class ObjectRecognizer:
    algorithms = list()

    def __init__(self, name, backend=ObjectRecognizers.LUMINOTH, classes=None, model_path=None, **kwargs):
        self.name = name

        self.model_path = model_path
        self.model = None

        if self.model_path is not None:
            backend = self._auto_detect_backend()

        self.object_recognizer = self._initialize_object_recognizer(name, backend, classes, model_path, **kwargs)
        self.classes = self.object_recognizer.classes

    def train(self, **kwargs):
        self.object_recognizer.train(**kwargs)

    def predict(self, game_frame, **kwargs):
        return self.object_recognizer.predict(game_frame, **kwargs)

    def predict_directory(self, path, **kwargs):
        self.object_recognizer.predict_directory(path, **kwargs)

    def on_interrupt(self, *args):
        self.object_recognizer.on_interrupt(self, *args)

    def _initialize_object_recognizer(self, name, backend, classes, model_path, **kwargs):
        if backend == ObjectRecognizers.LUMINOTH:
            from serpent.machine_learning.object_recognition.object_recognizers.luminoth_object_recognizer import LuminothObjectRecognizer
            return LuminothObjectRecognizer(name, classes=classes, model_path=model_path, **kwargs)
        else:
            raise SerpentError("The specified backend is invalid!")

    def _auto_detect_backend(self):
        if os.path.exists(f"{self.model_path}/luminoth.yml"):
            return ObjectRecognizers.LUMINOTH

        return ObjectRecognizers.LUMINOTH
