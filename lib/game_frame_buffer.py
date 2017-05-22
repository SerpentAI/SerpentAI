
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
