from serpent.machine_learning.context_classification.context_classifier import ContextClassifier

from keras.preprocessing.image import ImageDataGenerator
from keras.applications.inception_v3 import InceptionV3, preprocess_input
from keras.layers import Dense, GlobalAveragePooling2D
from keras.models import Model, load_model

import skimage.transform

import numpy as np

import serpent.cv


class CNNInceptionV3ContextClassifier(ContextClassifier):

    def __init__(self, input_shape=None):
        super().__init__()
        self.input_shape = input_shape

        self.training_generator = None
        self.validation_generator = None

    def train(self, epochs=3):
        if self.training_generator is None or self.validation_generator is None:
            self.prepare_generators()

        base_model = InceptionV3(
            weights="imagenet",
            include_top=False,
            input_shape=self.input_shape
        )

        output = base_model.output
        output = GlobalAveragePooling2D()(output)
        output = Dense(1024, activation='relu')(output)

        predictions = Dense(len(self.training_generator.class_indices), activation='softmax')(output)
        self.classifier = Model(inputs=base_model.input, outputs=predictions)

        for layer in base_model.layers:
            layer.trainable = False

        self.classifier.compile(
            optimizer="rmsprop",
            loss="categorical_crossentropy",
            metrics=["accuracy"]
        )

        self.classifier.fit_generator(
            self.training_generator,
            samples_per_epoch=self.training_sample_count,
            nb_epoch=epochs,
            validation_data=self.validation_generator,
            nb_val_samples=self.validation_sample_count,
            class_weight="auto"
        )

    def validate(self):
        pass

    def predict(self, input_frame):
        if self.training_generator is None or self.validation_generator is None:
            self.prepare_generators()

        resized_input_frame = skimage.transform.resize(
            input_frame,
            self.input_shape,
            order=0
        )

        resized_input_frame = np.array(serpent.cv.scale_range(resized_input_frame, -1, 1), dtype="float32")

        class_mapping = self.training_generator.class_indices
        class_probabilities = self.classifier.predict(resized_input_frame[None, :, :, :])[0]

        max_probability_index = np.argmax(class_probabilities)
        max_probability = class_probabilities[max_probability_index]

        if max_probability < 0.5:
            return None

        for class_name, i in class_mapping.items():
            if i == max_probability_index:
                return class_name

    def save_classifier(self, file_path):
        if self.classifier is not None:
            self.classifier.save(file_path)

    def load_classifier(self, file_path):
        self.classifier = load_model(file_path)

    def prepare_generators(self):
        training_data_generator = ImageDataGenerator(preprocessing_function=preprocess_input)
        validation_data_generator = ImageDataGenerator(preprocessing_function=preprocess_input)

        self.training_generator = training_data_generator.flow_from_directory(
            "datasets/current/training",
            target_size=(self.input_shape[0], self.input_shape[1]),
            batch_size=32
        )

        self.validation_generator = validation_data_generator.flow_from_directory(
            "datasets/current/validation",
            target_size=(self.input_shape[0], self.input_shape[1]),
            batch_size=32
        )
