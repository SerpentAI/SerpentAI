import skimage.measure

import numpy as np


class GameMinimapCell:

    def __init__(self, image_data=None):
        self.image_data = image_data

    def identify(self, room_types):
        room_type_ssims = [
            (skimage.measure.compare_ssim(
                np.array(self.image_data, dtype="uint8"),
                np.array(image * 255, dtype="uint8")
            ), room_type) for image, room_type in room_types
        ]

        ssim, room_type = max(room_type_ssims, key=lambda t: t[0])

        return room_type if ssim > 0.9 else None

    @classmethod
    def divide_minimap(cls, minimap_bw_image):
        minimap_cell_shape = (14, 16)

        max_x = 5
        max_y = 5

        current_x = 1
        current_y = 1

        minimap_cells = list()

        while current_x <= max_x and current_y <= max_y:
            y0 = current_y * minimap_cell_shape[0] - minimap_cell_shape[0] + 1
            x0 = current_x * minimap_cell_shape[1] - minimap_cell_shape[1] + 1
            y1 = current_y * minimap_cell_shape[0] + 1
            x1 = current_x * minimap_cell_shape[1] + 1

            minimap_cells.append(cls(image_data=minimap_bw_image[y0:y1, x0:x1]))

            current_x += 1

            if current_x > max_x:
                current_x = 1
                current_y += 1

        return minimap_cells
