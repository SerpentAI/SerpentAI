import offshoot


class YouMustBuildABoatGameAgentPlugin(offshoot.Plugin):
    name = "YouMustBuildABoatGameAgentPlugin"
    version = "0.1.0"

    libraries = []

    files = [
        {"path": "you_must_build_a_boat_game_agent.py", "pluggable": "GameAgent"}
    ]

    config = {
        "frame_handler": "PLAY",
        "sfx_path": "/home/serpent/SFX"
    }

    @classmethod
    def on_install(cls):
        print("\n\n%s was installed successfully!" % cls.__name__)

    @classmethod
    def on_uninstall(cls):
        print("\n\n%s was uninstalled successfully!" % cls.__name__)


if __name__ == "__main__":
    offshoot.executable_hook(YouMustBuildABoatGameAgentPlugin)
