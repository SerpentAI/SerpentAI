import numpy as np

import random
import uuid


class SpriteError(BaseException):
    pass


class Sprite:

    def __init__(self, name, image_data=None, signature_colors=None, constellation_of_pixels=None, seed=None):
        if not isinstance(image_data, np.ndarray):
            raise SpriteError("'image_data' needs to be a 4D instance of ndarray...")

        if not len(image_data.shape) == 4:
            raise SpriteError("'image_data' ndarray needs to be 4D...")

        self.name = name
        self.image_data = image_data
        self.image_shape = image_data.shape[:2]

        self.seed = seed

        self.signature_colors = signature_colors or self._generate_signature_colors()
        self.constellation_of_pixels = constellation_of_pixels or self._generate_constellation_of_pixels(seed=self.seed)

    def append_image_data(self, image_data, signature_colors=None, constellation_of_pixels=None):
        images = list()

        for i in range(self.image_data.shape[3]):
            images.append((self.image_data[:, :, :, i])[:, :, :, np.newaxis])

        images.append(image_data)

        self.image_data = np.squeeze(np.stack(images, axis=3))

        if signature_colors is not None:
            self.signature_colors.append(signature_colors)
        else:
            self.signature_colors = self._generate_signature_colors()

        if constellation_of_pixels is not None:
            self.constellation_of_pixels.append(constellation_of_pixels)
        else:
            self.constellation_of_pixels = self._generate_constellation_of_pixels(seed=self.seed)

    def _generate_seed(self):
        return str(uuid.uuid4())

    def _generate_signature_colors(self):
        signature_colors = list()
        height, width, pixels, animation_states = self.image_data.shape

        for i in range(animation_states):
            values, counts = np.unique(self.image_data[..., i].reshape(width * height, 3), axis=0, return_counts=True)
            maximum_indices = np.argsort(counts)[::-1][:8]

            signature_colors.append(set(tuple(map(int, values[index])) for index in maximum_indices))

        return signature_colors

    def _generate_constellation_of_pixels(self, quantity=8, seed=None):
        if seed is None:
            seed = self._generate_seed()

        random.seed(seed)

        constellation_of_pixels = list()
        height, width, pixels, animation_states = self.image_data.shape

        for i in range(animation_states):
            constellation_of_pixels.append(dict())

            for ii in range(quantity):
                signature_color = random.choice(list(self.signature_colors[i]))
                signature_color_locations = Sprite.locate_color(signature_color, np.squeeze(self.image_data[:, :, :3, i]))

                y, x = random.choice(signature_color_locations)
                constellation_of_pixels[i][(y, x)] = signature_color

        return constellation_of_pixels

    @classmethod
    def locate_color(cls, color, image):
        color_indices = np.where(np.all(image[:, :, :3] == color, axis=-1))

        return list(zip(*color_indices)) if len(color_indices[0]) else None
