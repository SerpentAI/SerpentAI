import numpy as np

import random
import uuid


class SpriteError(BaseException):
    pass


class Sprite:

    def __init__(self, name, image_data=None):
        if not isinstance(image_data, np.ndarray):
            raise SpriteError("'image_data' needs to be a 4D instance of ndarray...")

        if not len(image_data.shape) == 4:
            raise SpriteError("'image_data' ndarray needs to be 4D...")

        self.name = name
        self.image_data = image_data
        self.image_shape = image_data.shape[:2]

    def sample_pixels(self, quantity=5, iterations=1, seed=None):
        if seed is None:
            seed = self._generate_seed()

        random.seed(seed)

        samples = list()

        for i in range(quantity):
            samples.append(list())

            for ii in range(iterations):
                samples[i].append(list())

                for iii in range(self.image_data.shape[3]):
                    y = random.randint(0, self.image_data.shape[0] - 1)
                    x = random.randint(0, self.image_data.shape[1] - 1)

                    pixel = self.image_data[y, x, :, iii]
                    samples[i][ii].append(tuple(pixel) + (y, x))

        return samples

    def append_image_data(self, image_data):
        images = list()

        for i in range(self.image_data.shape[3]):
            images.append((self.image_data[:, :, :, i])[:, :, :, np.newaxis])

        images.append(image_data)

        self.image_data = np.squeeze(np.stack(images, axis=3))

    def _generate_seed(self):
        return str(uuid.uuid4())