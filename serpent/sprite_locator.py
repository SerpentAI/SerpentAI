from serpent.sprite import Sprite
import serpent.cv
import numpy as np


class SpriteLocator:

    def __init__(self, **kwargs):
        pass

    def locate(self, sprite=None, game_frame=None, screen_region=None, use_global_location=True):
        """
        Locates the sprite within the defined game frame

        Parameters
            sprite: The sprite to find\n
            game_frame: The frame to search within\n
            screen_region: (optional) region within which to search within the frame\n
            use_global_location: (optional) if using a region, whether to return global location or local to region

        Returns
            Tuple of location of the sprite
        """
        constellation_of_pixel_images = sprite.generate_constellation_of_pixels_images()
        location = None
        frame = game_frame.frame

        if screen_region is not None:
            frame = serpent.cv.extract_region_from_image(frame, screen_region)

        for i in range(len(constellation_of_pixel_images)):
            constellation_of_pixels_item = list(sprite.constellation_of_pixels[i].items())[0]

            query_coordinates = constellation_of_pixels_item[0]
            query_rgb = constellation_of_pixels_item[1]

            rgb_coordinates = Sprite.locate_color(query_rgb, image=frame)

            rgb_coordinates = list(map(lambda yx: (yx[0] - query_coordinates[0], yx[1] - query_coordinates[1]), rgb_coordinates))

            maximum_y = frame.shape[0] - constellation_of_pixel_images[i].shape[0]
            maximum_x = frame.shape[1] - constellation_of_pixel_images[i].shape[1]

            for y, x in rgb_coordinates:
                if y < 0 or x < 0 or y > maximum_y or x > maximum_x:
                    continue

                for yx, rgb in sprite.constellation_of_pixels[i].items():
                    if tuple(frame[y + yx[0], x + yx[1], :]) != rgb:
                        break
                else:
                    location = (
                        y,
                        x,
                        y + constellation_of_pixel_images[i].shape[0],
                        x + constellation_of_pixel_images[i].shape[1]
                    )

        if location is not None and screen_region is not None and use_global_location:
            location = (
                location[0] + screen_region[0],
                location[1] + screen_region[1],
                location[2] + screen_region[0],
                location[3] + screen_region[1]
            )

        return location
