import skimage.measure
import skimage.io

import numpy as np


class GameMinimapCell:
    plugin_data_path = "plugins/BindingOfIsaacRebirthGameAgentPlugin/files/data"

    minimap_room_types = [
        (np.zeros(224).reshape(14, 16), "empty"),
        (skimage.io.imread(f"{plugin_data_path}/cell_room.png", as_grey=True), "room"),
        (skimage.io.imread(f"{plugin_data_path}/cell_locked.png", as_grey=True), "locked"),
        (skimage.io.imread(f"{plugin_data_path}/cell_treasure.png", as_grey=True), "treasure"),
        (skimage.io.imread(f"{plugin_data_path}/cell_boss.png", as_grey=True), "boss"),
        (skimage.io.imread(f"{plugin_data_path}/cell_shop.png", as_grey=True), "shop"),
        (skimage.io.imread(f"{plugin_data_path}/cell_room_bomb.png", as_grey=True), "room_bomb"),
        (skimage.io.imread(f"{plugin_data_path}/cell_room_coin.png", as_grey=True), "room_coin"),
        (skimage.io.imread(f"{plugin_data_path}/cell_room_heart.png", as_grey=True), "room_heart"),
        (skimage.io.imread(f"{plugin_data_path}/cell_room_key.png", as_grey=True), "room_key"),
        (skimage.io.imread(f"{plugin_data_path}/cell_room_pill.png", as_grey=True), "room_pill"),
        (skimage.io.imread(f"{plugin_data_path}/cell_room_trinket.png", as_grey=True), "room_trinket"),
        (skimage.io.imread(f"{plugin_data_path}/cell_curse.png", as_grey=True), "curse"),
        (skimage.io.imread(f"{plugin_data_path}/cell_sacrifice.png", as_grey=True), "sacrifice"),
        (skimage.io.imread(f"{plugin_data_path}/cell_miniboss.png", as_grey=True), "miniboss"),
        (skimage.io.imread(f"{plugin_data_path}/cell_secret.png", as_grey=True), "secret")
    ]

    def __init__(self, image_data=None):
        self.image_data = image_data
        self.room_type_label = None

    @property
    def room_type(self):
        if self.room_type_label is None:
            self.room_type_label = self.identify()

        return self.room_type_label

    def identify(self):
        room_type_ssims = [
            (skimage.measure.compare_ssim(
                np.array(self.image_data, dtype="uint8"),
                np.array(image * 255, dtype="uint8")
            ), room_type) for image, room_type in self.__class__.minimap_room_types
        ]

        ssim, room_type = max(room_type_ssims, key=lambda t: t[0])

        return room_type if ssim > 0.9 else "Unknown"

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
