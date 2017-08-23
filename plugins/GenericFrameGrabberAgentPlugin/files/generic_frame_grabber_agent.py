from lib.game_agent import GameAgent
from lib.config import config

class GenericFrameGrabberAgent(GameAgent):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.captured_frame_count = 0
        self.original_handler = self.frame_handlers["COLLECT_FRAMES_FOR_CONTEXT"]
        self.frame_handlers["COLLECT_FRAMES_FOR_CONTEXT"] = self.handle_capture


    def handle_capture(self, frame):
        self.original_handler(frame)
        self.captured_frame_count += 1
        print("\033c")
        context_name = config["frame_handlers"]["COLLECT_FRAMES_FOR_CONTEXT"]["context"]
        print(f"CAPTURED FRAME: {self.captured_frame_count} for '{context_name}'")