from serpent.visual_debugger.visual_debugger import VisualDebugger

import numpy as np


class GameFrameBufferError(BaseException):
    pass


class GameFrameBuffer:

    def __init__(self, size=5):
        self.size = size
        self.frames = list()

    @property
    def full(self):
        return len(self.frames) >= self.size

    @property
    def previous_game_frame(self):
        return self.frames[0] if len(self.frames) else None

    def add_game_frame(self, game_frame):
        if self.full:
            self.frames = [game_frame] + self.frames[:-1]
        else:
            self.frames = [game_frame] + self.frames

    def to_visual_debugger(self):
        visual_debugger = VisualDebugger()

        for i, game_frame in enumerate(self.frames):
            visual_debugger.store_image_data(
                np.array(game_frame.frame * 255, dtype="uint8"),
                game_frame.frame.shape,
                f"frame_{i + 1}"
            )
