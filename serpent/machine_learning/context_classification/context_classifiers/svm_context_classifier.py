from serpent.machine_learning.context_classification.context_classifier import ContextClassifier

from serpent.visual_debugger.visual_debugger import VisualDebugger

import os
import pickle
import subprocess

import skimage.io
import skimage.transform
import skimage.color
import skimage.filters

import numpy as np

import sklearn.svm

from serpent.config import config


visual_debugger = VisualDebugger()


class SVMContextClassifier(ContextClassifier):

    def __init__(self, input_shape=None):
        super().__init__()
        self.input_shape = input_shape

    def train(self, epochs=3, preprocessing_func=None):
        data = list()
        targets = list()

        for root, dirs, files in os.walk("datasets/current/training"):
            if root != "datasets/current/training":
                current_label = root.split("/")[-1]

                for file in files:
                    if not file.endswith(".png"):
                        continue

                    file_path = f"{root}/{file}"
                    sample = skimage.io.imread(file_path)

                    targets.append(current_label)

                    preprocessed_sample = preprocessing_func(sample) if preprocessing_func is not None else self.preprocess_sample(sample)

                    visual_debugger.store_image_data(np.array(preprocessed_sample * 255, dtype="uint8"), preprocessed_sample.shape, bucket="svm_input")
                    visual_debugger.store_image_data(sample, sample.shape, bucket="original_frame")

                    if preprocessed_sample.dtype != "uint8":
                        preprocessed_sample = np.array(preprocessed_sample * 255, dtype="uint8")

                    data.append(preprocessed_sample.flatten())

        self.classifier = sklearn.svm.SVC(gamma=0.001, C=100)
        self.classifier.fit(data, targets)

    def validate(self, preprocessing_func=None, file_path=None):
        if self.classifier is None:
            self.load_classifier(file_path)

        sample_count = 0
        correct_sample_count = 0

        for root, dirs, files in os.walk("datasets/current/validation"):
            if root != "datasets/current/validation":
                current_label = root.split("/")[-1]

                for file in files:
                    if not file.endswith(".png"):
                        continue

                    sample_count += 1

                    file_path = f"{root}/{file}"
                    sample = skimage.io.imread(file_path)

                    predicted_class = self.predict(sample, preprocessing_func=preprocessing_func)

                    if predicted_class == current_label:
                        correct_sample_count += 1

                    subprocess.call(["clear"])
                    print(f"SVM Accuracy: {correct_sample_count / sample_count}")

    def predict(self, input_frame, preprocessing_func=None):
        preprocessed_frame = preprocessing_func(input_frame) if preprocessing_func is not None else self.preprocess_sample(input_frame)

        if preprocessed_frame.dtype != "uint8":
            preprocessed_frame = np.array(preprocessed_frame * 255, dtype="uint8")

        return self.classifier.predict([preprocessed_frame.flatten()])[0]

    def save_classifier(self, file_path):
        serialized_classifier = pickle.dumps(self.classifier)

        with open(file_path, "wb") as f:
            f.write(serialized_classifier)

    def load_classifier(self, file_path):
        with open(file_path, "rb") as f:
            self.classifier = pickle.loads(f.read())

    def preprocess_sample(self, sample):
        gray_sample = np.array(skimage.color.rgb2gray(sample) * 255, dtype="uint8")

        threshold = skimage.filters.threshold_local(gray_sample, 21)
        bw_sample = gray_sample > threshold

        return skimage.transform.resize(bw_sample, (60, 96), mode="reflect", order=0)
