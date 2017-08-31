import numpy as np

import random
import uuid


class SpriteError(BaseException):
    pass


class Sprite:

    def __init__(self, name, image_data=None, signature_colors=None):
        if not isinstance(image_data, np.ndarray):
            raise SpriteError("'image_data' needs to be a 4D instance of ndarray...")

        if not len(image_data.shape) == 4:
            raise SpriteError("'image_data' ndarray needs to be 4D...")

        self.name = name
        self.image_data = image_data
        self.image_shape = image_data.shape[:2]

        self.signature_colors = signature_colors or self._generate_signature_colors()

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
                    if self.signature_colors is not None:
                        signature_color = random.choice(self.signature_colors)
                        signature_color_locations = Sprite.locate_color(signature_color, np.squeeze(self.image_data[:, :, :3, iii]))

                        if signature_color_locations is not None:
                            y, x = random.choice(signature_color_locations)
                            samples[i][ii].append(tuple(signature_color) + (y, x))
                    else:
                        y = random.randint(0, self.image_data.shape[0] - 1)
                        x = random.randint(0, self.image_data.shape[1] - 1)

                        pixel = self.image_data[y, x, :, iii]
                        samples[i][ii].append(tuple(pixel) + (y, x))

        return samples

    def append_image_data(self, image_data, signature_colors=None):
        images = list()

        for i in range(self.image_data.shape[3]):
            images.append((self.image_data[:, :, :, i])[:, :, :, np.newaxis])

        images.append(image_data)

        self.image_data = np.squeeze(np.stack(images, axis=3))

        if signature_colors is not None:
            self.signature_colors.append(signature_colors)
        else:
            self.signature_colors = self._generate_signature_colors()

    def _generate_seed(self):
        return str(uuid.uuid4())

    def _generate_signature_colors(self):
        # TODO: Exclude RGB 0, 0, 0, from signature

        signature_colors = list()
        height, width, pixels, animation_states = self.image_data.shape

        for i in range(animation_states):
            values, counts = np.unique(self.image_data[..., i].reshape(width * height, 3), axis=0, return_counts=True)
            maximum_indices = np.argsort(counts)[::-1][:5]

            signature_colors.append([tuple(map(int, values[index])) for index in maximum_indices])

        return signature_colors

    @classmethod
    def locate_color(cls, color, image):
        color_indices = np.where(np.all(image[:, :, :3] == color, axis=-1))

        return list(zip(*color_indices)) if len(color_indices[0]) else None
