from serpent.sprite import Sprite


class SpriteLocator:

    def __init__(self, **kwargs):
        pass

    def locate(self, sprite=None, game_frame=None):
        constellation_of_pixel_images = sprite.generate_constellation_of_pixels_images()
        location = None

        for i in range(len(constellation_of_pixel_images)):
            constellation_of_pixels_item = list(sprite.constellation_of_pixels[i].items())[0]

            query_coordinates = constellation_of_pixels_item[0]
            query_rgb = constellation_of_pixels_item[1]

            rgb_coordinates = Sprite.locate_color(query_rgb, image=game_frame.frame)
            rgb_coordinates = list(map(lambda yx: (yx[0] - query_coordinates[0], yx[1] - query_coordinates[1]), rgb_coordinates))

            maximum_y = game_frame.frame.shape[0] - constellation_of_pixel_images[i].shape[0]
            maximum_x = game_frame.frame.shape[1] - constellation_of_pixel_images[i].shape[1]

            for y, x in rgb_coordinates:
                if y < 0 or x < 0 or y > maximum_y or x > maximum_x:
                    continue

                for yx, rgb in sprite.constellation_of_pixels[i].items():
                    if tuple(game_frame.frame[y + yx[0], x + yx[1], :]) != rgb:
                        break
                else:
                    location = (
                        y,
                        x,
                        y + constellation_of_pixel_images[i].shape[0],
                        x + constellation_of_pixel_images[i].shape[1]
                    )

        return location
