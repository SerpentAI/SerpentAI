import serpent.datasets

import os
import random

import skimage.io


class ContextClassifierError(BaseException):
    pass


class ContextClassifier:
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

        serpent.datasets.create_training_and_validation_sets(
            class_directories,
            validation_set_probability=validation_set_probability,
            seed=seed
        )

    def train(self, epochs=3):
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

    @classmethod
    def executable_train(cls, epochs=3, classifier="CNNInceptionV3ContextClassifier"):
        context_paths = list()

        for root, directories, files in os.walk("datasets/collect_frames_for_context".replace("/", os.sep)):
            if root != "datasets/collect_frames_for_context".replace("/", os.sep):
                break

            for directory in directories:
                context_paths.append(f"datasets/collect_frames_for_context/{directory}".replace("/", os.sep))

        if not len(context_paths):
            raise ContextClassifierError("No Context Frames found in 'datasets/collect_frames_for_datasets'...")

        serpent.datasets.create_training_and_validation_sets(context_paths)

        context_classifier_class = cls.context_classifier_mapping().get(classifier)

        if context_classifier_class is not None:
            context_path = random.choice(context_paths)
            frame_path = None

            for root, directories, files in os.walk(context_path):
                for file in files:
                    if file.endswith(".png"):
                        frame_path = f"{context_path}/{file}"
                        break

                if frame_path is not None:
                    break

            frame = skimage.io.imread(frame_path)

            context_classifier = context_classifier_class(input_shape=frame.shape)

            context_classifier.train(epochs=epochs)
            context_classifier.validate()

            context_classifier.save_classifier("datasets/context_classifier.model")
            print("Success! Model was saved to 'datasets/context_classifier.model'")

    @classmethod
    def context_classifier_mapping(cls):
        from serpent.machine_learning.context_classification.context_classifiers.svm_context_classifier import SVMContextClassifier
        from serpent.machine_learning.context_classification.context_classifiers.cnn_inception_v3_context_classifier import CNNInceptionV3ContextClassifier

        return {
            "SVMContextClassifier": SVMContextClassifier,
            "CNNInceptionV3ContextClassifier": CNNInceptionV3ContextClassifier
        }

