from .game_minimap_cell import GameMinimapCell

import skimage.io

import numpy as np

from lib.visual_debugger.visual_debugger import VisualDebugger
visual_debugger = VisualDebugger()


class GameMinimap:

    def __init__(self, minimap_image=None):
        self.minimap_image = None
        self.minimap_cells = None

        plugin_data_path = "plugins/BindingOfIsaacRebirthGameAgentPlugin/files/data"

        self.minimap_room_types = [
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

        self.update(minimap_image)

    def update(self, minimap_image):
        self.minimap_image = minimap_image
        self.minimap_cells = GameMinimapCell.divide_minimap(minimap_image)

        for i, minimap_cell in enumerate(self.minimap_cells):
            visual_debugger.store_image_data(
                np.array(minimap_cell.image_data * 255, dtype="uint8"),
                minimap_cell.image_data.shape,
                f"minimap_{i}"
            )

    @property
    def center(self):
        return self.minimap_cells[12]

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