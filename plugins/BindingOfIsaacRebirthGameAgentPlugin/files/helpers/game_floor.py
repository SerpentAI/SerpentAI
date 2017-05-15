from .game_room import GameRoom
from .game_minimap_cell import GameMinimapCell

from lib.visual_debugger.visual_debugger import VisualDebugger

import matplotlib.pyplot as plt

visual_debugger = VisualDebugger()

import numpy as np


class GameFloor:
    def __init__(self, **kwargs):
        self.current_room = (0, 0)

        self.rooms = {
            (0, 0): GameRoom(is_explored=True)
        }