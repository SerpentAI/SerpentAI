import skimage.measure


class SpriteIdentifier:
    def __init__(self):
        self.sprites = dict()

    def identify(self, sprite, mode="SIGNATURE_COLORS", score_threshold=75, debug=False):
        if mode == "SIGNATURE_COLORS":
            return self.identify_by_signature_colors(sprite, score_threshold=score_threshold, debug=debug)
        elif mode == "CONSTELLATION_OF_PIXELS":
            return self.identify_by_constellation_of_pixels(sprite, score_threshold=score_threshold, debug=debug)
        elif mode == "SSIM":
            return self.identify_by_ssim(sprite, score_threshold=score_threshold, debug=debug)

    def identify_by_signature_colors(self, query_sprite, score_threshold=0, debug=False):
        top_sprite_score = 0
        top_sprite_match = None

        for sprite_name, sprite in self.sprites.items():
            for sprite_signature_colors in sprite.signature_colors:
                for query_sprite_signature_colors in query_sprite.signature_colors:
                    signature_color_score = int((len(query_sprite_signature_colors & sprite_signature_colors) / len(sprite_signature_colors)) * 100)

                    if debug:
                        print(sprite_name, signature_color_score)

                    if signature_color_score > top_sprite_score:
                        top_sprite_score = signature_color_score
                        top_sprite_match = sprite_name

        return top_sprite_match if top_sprite_score >= score_threshold else "UNKNOWN"

    def identify_by_constellation_of_pixels(self, query_sprite, score_threshold=0, debug=False):
        top_sprite_score = 0
        top_sprite_match = None

        for sprite_name, sprite in self.sprites.items():
            if sprite.image_shape != query_sprite.image_shape:
                continue

            for constellation_of_pixels in sprite.constellation_of_pixels:
                for i in range(query_sprite.image_data.shape[3]):
                    query_sprite_image = query_sprite.image_data[..., i]

                    constellation_of_pixels_score = 0

                    for pixel_coordinates, pixel_color in constellation_of_pixels.items():
                        if tuple(query_sprite_image[pixel_coordinates[0], pixel_coordinates[1], :][:3]) == pixel_color:
                            constellation_of_pixels_score += 1

                    constellation_of_pixels_score = int((constellation_of_pixels_score / len(constellation_of_pixels)) * 100)

                    if debug:
                        print(sprite_name, constellation_of_pixels_score)

                    if constellation_of_pixels_score > top_sprite_score:
                        top_sprite_score = constellation_of_pixels_score
                        top_sprite_match = sprite_name

        return top_sprite_match if top_sprite_score >= score_threshold else "UNKNOWN"

    def identify_by_ssim(self, query_sprite, score_threshold=0, debug=False):
        top_sprite_score = 0
        top_sprite_match = None

        for sprite_name, sprite in self.sprites.items():
            if sprite.image_data[..., 0].shape[:2] == query_sprite.image_data[..., 0].shape[:2]:
                for i in range(sprite.image_data.shape[3]):
                    for ii in range(query_sprite.image_data.shape[3]):
                        sprite_image = sprite.image_data[..., :3, i]
                        query_sprite_image = query_sprite.image_data[..., :3, ii]

                        ssim_score = int(skimage.measure.compare_ssim(query_sprite_image, sprite_image, multichannel=True) * 100)

                        if debug:
                            print(sprite_name, ssim_score)

                        if ssim_score > top_sprite_score:
                            top_sprite_score = ssim_score
                            top_sprite_match = sprite_name
            else:
                if debug:
                    print(f"The shape of '{sprite_name}' does not match the query sprite's shape. Skipping!")

        return top_sprite_match if top_sprite_score >= score_threshold else "UNKNOWN"

    def register(self, sprite):
        self.sprites[sprite.name] = sprite
