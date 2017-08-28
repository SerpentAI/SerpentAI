import numpy as np


class SpriteIdentifier:
    def __init__(self, pixel_quantity=10, iterations=1, match_threshold=0.8):
        self.pixel_quantity = pixel_quantity
        self.iterations = iterations

        self.minimum_matches = int(match_threshold * pixel_quantity)

        self.sprites = dict()
        self.sprite_shapes = dict()

    def identify(self, sprite):
        results = dict()

        for sprite_name, sprite_data in self.sprites.get(sprite.image_shape, dict()).items():
            results[sprite_name] = 0

            for i in range(0, sprite_data[1].shape[2]):
                for ii in range(0, sprite_data[1].shape[0]):
                    pixel = sprite_data[1][ii, 0, i, :3]
                    coordinates = sprite_data[1][ii, 0, i, 3:]

                    for iii in range(0, sprite.image_data.shape[3]):
                        sprite_pixel = sprite.image_data[coordinates[0], coordinates[1], :, iii]

                        if tuple(sprite_pixel) == tuple(pixel):
                            results[sprite_name] += 1

        max_result = max(results.items(), key=lambda r: r[1])

        return max_result[0] if max_result[1] >= self.minimum_matches else "UNKNOWN"

    def register(self, sprite):
        if sprite.image_shape not in self.sprites:
            self.sprites[sprite.image_shape] = dict()

        sprite_sample_pixels_array = np.array(
            sprite.sample_pixels(quantity=self.pixel_quantity, iterations=self.iterations))

        self.sprites[sprite.image_shape][sprite.name] = (
            sprite,
            sprite_sample_pixels_array
        )

        self.sprite_shapes[sprite.name] = sprite.image_shape
