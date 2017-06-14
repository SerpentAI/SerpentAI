from lib.machine_learning.context_classification.context_classifier import ContextClassifier

from lib.visual_debugger.visual_debugger import VisualDebugger

import os
import pickle

import skimage.io
import skimage.transform
import skimage.color
import skimage.filters

import numpy as np

import sklearn.svm

from lib.config import config


visual_debugger = VisualDebugger()


class SVMContextClassifier(ContextClassifier):

    def __init__(self):
        super().__init__()


    def train(self):
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

                    preprocessed_sample = self.preprocess_sample(sample)

                    visual_debugger.store_image_data(np.array(preprocessed_sample * 255, dtype="uint8"), preprocessed_sample.shape, bucket="svm_input")
                    visual_debugger.store_image_data(sample, sample.shape, bucket="original_frame")

                    data.append(preprocessed_sample.flatten())

        self.classifier = sklearn.svm.SVC(gamma=0.001, C=100)
        self.classifier.fit(data, targets)

    def validate(self, file_path):
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

                    predicted_class = self.classifier.predict(self.preprocess_sample(sample))

                    if predicted_class == current_label:
                        correct_sample_count += 1

                    print("\033c")
                    print(f"SVM Accuracy: {correct_sample_count / sample_count}")

    def predict(self, input_frame):
        preprocessed_frame = self.preprocess_sample(input_frame)
        visual_debugger.store_image_data(np.array(preprocessed_frame * 255, dtype="uint8"), preprocessed_frame.shape, bucket="svm_input")
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
