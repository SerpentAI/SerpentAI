import numpy as np

import random
import uuid


class SpriteError(BaseException):
    pass


class Sprite:

    def __init__(self, name, image_data=None, signature_colors=None, constellation_of_pixels=None):
        if not isinstance(image_data, np.ndarray):
            raise SpriteError("'image_data' needs to be a 4D instance of ndarray...")

        if not len(image_data.shape) == 4:
            raise SpriteError("'image_data' ndarray needs to be 4D...")

        self.name = name
        self.image_data = image_data
        self.image_shape = image_data.shape[:2]

        self.signature_colors = signature_colors or self._generate_signature_colors()

        self.constellation_of_pixels = constellation_of_pixels or self._generate_constellation_of_pixels()

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
            self.constellation_of_pixels = self._generate_constellation_of_pixels()

    def generate_constellation_of_pixels_images(self):
        constellation_of_pixel_images = list()

        for i in range(self.image_data.shape[3]):
            constellation_of_pixel_image = np.zeros(self.image_data[..., :3, 0].shape, dtype="uint8")

            for yx, rgb in self.constellation_of_pixels[0].items():
                constellation_of_pixel_image[yx[0], yx[1], :] = rgb

            constellation_of_pixel_images.append(constellation_of_pixel_image)

        return constellation_of_pixel_images

    def _generate_seed(self):
        return str(uuid.uuid4())

    def _generate_signature_colors(self, quantity=8):
        signature_colors = list()
        height, width, pixels, animation_states = self.image_data.shape

        for i in range(animation_states):
            values, counts = np.unique(self.image_data[..., i].reshape(width * height, pixels), axis=0, return_counts=True)

            if len(values[0]) == 3:
                maximum_indices = np.argsort(counts)[::-1][:quantity]
            elif len(values[0]) == 4:
                maximum_indices = list()

                for index in np.argsort(counts)[::-1]:
                    value = values[index]

                    if value[3] > 0:
                        maximum_indices.append(index)

                        if len(maximum_indices) == quantity:
                            break

            colors = [tuple(map(int, values[index][:3])) for index in maximum_indices]
            signature_colors.append(set(colors))

        return signature_colors

    def _generate_constellation_of_pixels(self, quantity=8):
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
        # TODO: Optimize for ms gain

        if image.shape[2] == 3:
            color_indices = np.where(np.all(image[:, :, :3] == color, axis=-1))
        elif image.shape[2] == 4:
            color_indices = np.where(np.all(image[:, :, :3] == (list(color) + [255]), axis=-1))

        return list(zip(*color_indices)) if len(color_indices[0]) else None
