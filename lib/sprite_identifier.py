
class SpriteIdentifier:
    def __init__(self):
        self.sprites = dict()

    def identify(self, sprite, mode="SIGNATURE_COLORS", score_threshold=75):
        if mode == "SIGNATURE_COLORS":
            return self.identify_by_signature_colors(sprite, score_threshold=score_threshold)
        elif mode == "CONSTELLATION_OF_PIXELS":
            return self.identify_by_constellation_of_pixels(sprite, score_threshold=score_threshold)

    def identify_by_signature_colors(self, query_sprite, score_threshold=0):
        top_sprite_score = 0
        top_sprite_match = None

        for sprite_name, sprite in self.sprites.items():
            for sprite_signature_colors in sprite.signature_colors:
                for query_sprite_signature_colors in query_sprite.signature_colors:
                    signature_color_score = len(query_sprite_signature_colors & sprite_signature_colors)

                    if signature_color_score > top_sprite_score and round((signature_color_score / len(sprite_signature_colors)) * 100.0, 2) >= score_threshold:
                        top_sprite_score = signature_color_score
                        top_sprite_match = sprite_name

        return top_sprite_match or "UNKNOWN"

    def identify_by_constellation_of_pixels(self, query_sprite, score_threshold=0):
        top_sprite_score = 0
        top_sprite_match = None

        for sprite_name, sprite in self.sprites.items():
            for constellation_of_pixels in sprite.constellation_of_pixels:
                for i in range(query_sprite.image_data.shape[3]):
                    query_sprite_image = query_sprite.image_data[..., i]

                    constellation_of_pixels_score = 0

                    for pixel_coordinates, pixel_color in constellation_of_pixels.items():
                        if tuple(query_sprite_image[pixel_coordinates[0], pixel_coordinates[1], :]) == pixel_color:
                            constellation_of_pixels_score += 1

                    if constellation_of_pixels_score > top_sprite_score and round((constellation_of_pixels_score / len(constellation_of_pixels)) * 100.0, 2) > score_threshold:
                        top_sprite_score = constellation_of_pixels_score
                        top_sprite_match = sprite_name

        return top_sprite_match or "UNKNOWN"

    def register(self, sprite):
        self.sprites[sprite.name] = sprite
