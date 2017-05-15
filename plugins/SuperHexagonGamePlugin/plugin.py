import offshoot


class SuperHexagonGamePlugin(offshoot.Plugin):
    name = "SuperHexagonGamePlugin"
    version = "0.1.0"

    libraries = []

    files = [
        {"path": "super_hexagon_game.py", "pluggable": "Game"}
    ]

    config = {
        "frame_rate": 10
    }

    @classmethod
    def on_install(cls):
        print("\n\n%s was installed successfully!" % cls.__name__)

    @classmethod
    def on_uninstall(cls):
        print("\n\n%s was uninstalled successfully!" % cls.__name__)


if __name__ == "__main__":
    offshoot.executable_hook(SuperHexagonGamePlugin)
