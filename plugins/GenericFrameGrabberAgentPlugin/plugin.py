import offshoot


class GenericFrameGrabberAgentPlugin(offshoot.Plugin):
    name = "GenericFrameGrabberAgentPlugin"
    version = "0.1.0"

    libraries = []

    files = [
        {"path": "generic_frame_grabber_agent.py", "pluggable": "GameAgent"}
    ]

    config = {
        "frame_handler": "COLLECT_FRAMES_FOR_CONTEXT",
        "collect_frames_interval": 1
    }

    @classmethod
    def on_install(cls):
        print("\n\n%s was installed successfully!" % cls.__name__)

    @classmethod
    def on_uninstall(cls):
        print("\n\n%s was uninstalled successfully!" % cls.__name__)


if __name__ == "__main__":
    offshoot.executable_hook(GenericFrameGrabberAgentPlugin)
