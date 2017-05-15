import lib.datasets

import os


class ContextClassifier:
    """
        Tools to train a context classifier.
        Assumes populated directories-as-labels in datasets/collect_frames_for_context
    """

    def __init__(self, **kwargs):
        self.classifier = None

    @property
    def training_sample_count(self):
        sample_count = 0

        for root, dirs, files in os.walk("datasets/current/training"):
            sample_count += len(files)

        return sample_count

    @property
    def validation_sample_count(self):
        sample_count = 0

        for root, dirs, files in os.walk("datasets/current/validation"):
            sample_count += len(files)

        return sample_count

    @staticmethod
    def create_training_and_validation_sets(validation_set_probability=0.1, seed=None):
        class_directories = None

        for root, dirs, files in os.walk("datasets/collect_frames_for_context"):
            class_directories = [f"{root}/{d}" for d in dirs]
            break

        lib.datasets.create_training_and_validation_sets(
            class_directories,
            validation_set_probability=validation_set_probability,
            seed=seed
        )

    def train(self):
        raise NotImplementedError()

    def validate(self):
        raise NotImplementedError()

    def predict(self, input_frame):
        raise NotImplementedError()

    def save_classifier(self, file_path):
        raise NotImplementedError()

    def load_classifier(self, file_path):
        raise NotImplementedError()

    @classmethod
    def available_implementations(cls):
        return [
            "SVMContextClassifier",
            "CNNInceptionV3ContextClassifier"
        ]
