from .game_minimap_cell import GameMinimapCell

import skimage.io
import skimage.measure

import numpy as np

from lib.visual_debugger.visual_debugger import VisualDebugger
visual_debugger = VisualDebugger()


class GameMinimap:

    def __init__(self, minimap_image=None):
        self.minimap_image = None
        self.minimap_cells = None

        self.previous_minimap_image = None
        self.update(minimap_image)

    def update(self, minimap_image):
        if self.minimap_image is not None:
            self.previous_minimap_image = self.minimap_image

        self.minimap_image = minimap_image
        self.minimap_cells = GameMinimapCell.divide_minimap(minimap_image)

        for i, minimap_cell in enumerate(self.minimap_cells):
            visual_debugger.store_image_data(
                np.array(minimap_cell.image_data * 255, dtype="uint8"),
                minimap_cell.image_data.shape,
                f"minimap_{i}"
            )

    @property
    def empty_minimap_image(self):
        return np.zeros(self.minimap_image.shape, dtype="bool")

    @property
    def center(self):
        return self.minimap_cells[12]

    def get_ssim(self, minimap_image=None):
        if minimap_image is None:
            minimap_image = self.previous_minimap_image if self.previous_minimap_image is not None else self.empty_minimap_image

        return skimage.measure.compare_ssim(self.minimap_image, minimap_image)

    def get_adjacent_cells(self, room_layout_type):
        if room_layout_type == "NORMAL_ROOM":
            return {
               (0, 1): self.minimap_cells[7],
               (1, 0): self.minimap_cells[13],
               (0, -1): self.minimap_cells[17],
               (-1, 0): self.minimap_cells[11]
            }
        elif room_layout_type == "BIG_SQUARE_ROOM":
            return {
                (0, 1): self.minimap_cells[7],
                (1, 1): self.minimap_cells[8],
                (2, 0): self.minimap_cells[14],
                (2, -1): self.minimap_cells[19],
                (0, -2): self.minimap_cells[22],
                (1, -2): self.minimap_cells[23],
                (-1, 0): self.minimap_cells[11],
                (-1, -1): self.minimap_cells[16],
            }
        else:
            return {
                (0, 1): self.minimap_cells[7],
                (1, 0): self.minimap_cells[13],
                (0, -1): self.minimap_cells[17],
                (-1, 0): self.minimap_cells[11]
            }
