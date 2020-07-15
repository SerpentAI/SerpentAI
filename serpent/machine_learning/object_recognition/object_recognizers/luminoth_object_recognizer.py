import os
import yaml
import json
import subprocess
import shlex
import time

import tensorflow as tf

from luminoth.tools.dataset.readers.object_detection import ObjectDetectionReader
from luminoth.tools.dataset.writers.object_detection_writer import ObjectDetectionWriter

from luminoth.tools.checkpoint import get_checkpoint_config

from luminoth.utils.dataset import read_xml, read_image
from luminoth.utils.config import get_config

from luminoth.utils.predicting import PredictorNetwork

from luminoth.train import run as luminoth_train
from luminoth.predict import predict_image as luminoth_predict

from serpent.machine_learning.object_recognition.object_recognizer import ObjectRecognizer

from serpent.utilities import SerpentError


class LuminothObjectRecognizer(ObjectRecognizer):
    algorithms = ["ssd", "fasterrcnn"]

    def __init__(self, name, algorithm="ssd", classes=None, model_path=None, **kwargs):
        self.name = name

        self.model_path = model_path
        self.model = None

        if self.model_path is not None:
            self.classes = self._load_classes()

            self.algorithm = None
            self.model = self._load_model()
        else:
            if algorithm not in self.__class__.algorithms:
                raise SerpentError(f"Algorithm '{algorithm}' not implemented in {self.__class__.__name__}")

            self.algorithm = algorithm
            self.classes = classes

    def train(self, **kwargs):
        self.convert_annotations_to_tfrecords()

        config = self._generate_train_luminoth_config(**kwargs)
        luminoth_train(config, environment="local")

    def predict(self, game_frame, **kwargs):
        image = game_frame.to_pil()

        before = time.time() 
        objects = self.model.predict_image(image)
        after = time.time()

        return objects, after - before

    def predict_directory(self, path, **kwargs):
        image_file_names = list()

        for root, directories, files in os.walk(path):
            if root == path:
                for file in files:
                    if file.endswith(".png"):
                        image_file_names.append(file)

        if not os.path.exists("datasets/predicted"):
            os.mkdir("datasets/predicted")

        for i, image_file_name in enumerate(image_file_names):
            image_path = f"{path}/{image_file_name}"
            save_path = f"datasets/predicted/{str(i + 1).zfill(6)}.png"

            luminoth_predict(self.model, image_path, save_path=save_path)

        # Attempt to make a video if FFMPEG is in PATH
        try:
            subprocess.call(shlex.split("ffmpeg -framerate 10 -i datasets/predicted/%06d.png  -c:v libx264 -r 30 -pix_fmt yuv420p datasets/predicted/predicted.mp4"))
        except Exception:
            pass

    def on_interrupt(self, *args):
        print("")

        print("TRAINING INTERRUPTED!")

        print("")

        print("TO ADD YOUR MODEL IN YOUR GAME AGENT PLUGIN:")
        print("Copy the 'object_recognition' directory in 'datasets' to your game agent's 'ml_models' directory")
        print(f"Copy 'classes.json', 'luminoth.yml' and optionally 'train.tfrecords' in 'datasets' to your game agent's 'ml_models/object_recognition/{self.name}' directory")

        print("")

        print("TO RESUME TRAINING LATER:")
        print("Leave everything where it is and run the same 'serpent train object' command")

        print("")

        import sys
        sys.exit()

    def convert_annotations_to_tfrecords(self):
        labelimg_reader = LabelImgReader(None, None, classes=self.classes)

        object_detection_writer = ObjectDetectionWriter(
            labelimg_reader,
            "datasets",
            "train"
        )

        object_detection_writer.save()

    def _generate_train_luminoth_config(self, **kwargs):
        config = {
            "train": {
                "run_name": self.name,
                "job_dir": "datasets/object_recognition"
            },
            "dataset": {
                "type": "object_detection",
                "dir": "datasets"
            },
            "model": {
                "type": self.algorithm,
                "network": {
                    "num_classes": len(self.classes)
                }
            }
        }

        if not os.path.exists("datasets/object_recognition"):
            os.mkdir("datasets/object_recognition")

        with open("datasets/luminoth.yml", "w") as f:
            f.write(yaml.dump(config))

        return get_config("datasets/luminoth.yml")

    def _generate_predict_luminoth_config(self, **kwargs):
        if self.algorithm is None:
            with open(f"{self.model_path}/luminoth.yml") as f:
                config = yaml.load(f)

            self.algorithm = config["model"]["type"]

        config = {
            "train": {
                "run_name": self.name,
                "job_dir": self.model_path.replace(f"/{self.name}", "")
            },
            "dataset": {
                "type": "object_detection",
                "dir": self.model_path
            },
            "model": {
                "type": self.algorithm,
                "network": {
                    "num_classes": len(self.classes)
                }
            }
        }

        with open(f"{self.model_path}/luminoth.predict.yml", "w") as f:
            f.write(yaml.dump(config))

    def _load_classes(self):
        with open(f"{self.model_path}/classes.json", "r") as f:
            classes = json.loads(f.read())

        return classes

    def _load_model(self):
        config_path = f"{self.model_path}/luminoth.predict.yml"

        if not os.path.exists(config_path):
            self._generate_predict_luminoth_config()

        config = get_config(config_path)

        return PredictorNetwork(config)


class LabelImgReader(ObjectDetectionReader):
    def __init__(self, data_dir, split, **kwargs):
        super().__init__(**kwargs)

        self.provided_classes = kwargs.get("classes")

        self.yielded_records = 0
        self.errors = 0

    def get_total(self):
        return len(list(self._get_record_names()))

    def get_classes(self):
        return self.provided_classes

    def _get_record_names(self):
        for root, directories, files in os.walk("datasets/annotations"):
            if root == "datasets/annotations":
                for file in files:
                    if not file.endswith(".xml"):
                        continue

                    yield file.replace(".xml", "")

    def iterate(self):
        for image_id in self._get_record_names():
            if self._stop_iteration():
                return

            try:
                annotation_path = f"datasets/annotations/{image_id}.xml"
                annotation = read_xml(annotation_path)

                image = read_image(annotation["path"])
            except tf.errors.NotFoundError:
                tf.logging.debug(f"Error reading image or annotation for '{image_id}'.")
                self.errors += 1

                continue

            gt_boxes = list()

            for obj in annotation["object"]:
                try:
                    label_id = self.classes.index(obj["name"])
                except ValueError:
                    continue

                gt_boxes.append({
                    "label": label_id,
                    "xmin": obj["bndbox"]["xmin"],
                    "ymin": obj["bndbox"]["ymin"],
                    "xmax": obj["bndbox"]["xmax"],
                    "ymax": obj["bndbox"]["ymax"],
                })

            if len(gt_boxes) == 0:
                continue

            self.yielded_records += 1

            yield {
                "width": annotation["size"]["width"],
                "height": annotation["size"]["height"],
                "depth": annotation["size"]["depth"],
                "filename": annotation["filename"],
                "image_raw": image,
                "gt_boxes": gt_boxes,
            }
