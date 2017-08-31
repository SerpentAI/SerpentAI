import numpy as np


class SpriteIdentifier:
    def __init__(self, pixel_quantity=10, iterations=1, match_threshold=0.8):
        self.pixel_quantity = pixel_quantity
        self.iterations = iterations

        self.minimum_matches = int(match_threshold * pixel_quantity)

        self.sprites = dict()
        self.sprite_shapes = dict()

    def identify(self, sprite, mode="SIGNATURE_COLORS"):
        if mode == "SIGNATURE_COLORS":
            return self.identify_by_signature_colors(sprite)
        elif mode == "CONSTELLATION_OF_PIXELS":
            return self.identify_by_constellation_of_pixels(sprite)

    def identify_by_signature_colors(self, query_sprite):
        top_sprite_score = 0
        top_sprite_match = None

        for shape, sprites in self.sprites.items():
            for sprite_name, sprite in sprites.items():
                for sprite_signature_colors in sprite[0].signature_colors:
                    for query_sprite_signature_colors in query_sprite.signature_colors:
                        signature_color_score = np.count_nonzero(sprite_signature_colors == query_sprite_signature_colors)

                        if signature_color_score > top_sprite_score:
                            top_sprite_score = signature_color_score
                            top_sprite_match = sprite_name

        return top_sprite_match or "UNKNOWN"

    def identify_by_constellation_of_pixels(self, sprite):
        # TODO: Rescued old code. Validate plz

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
