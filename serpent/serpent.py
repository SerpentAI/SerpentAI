#!/usr/bin/env python
import os
import sys
import shutil
import subprocess
import shlex

import offshoot

from serpent.utilities import clear_terminal, display_serpent_logo

# Add the current working directory to sys.path to discover user plugins!
sys.path.insert(0, os.getcwd())

game_class_mapping = offshoot.discover("Game")
game_agent_class_mapping = offshoot.discover("GameAgent")

valid_commands = [
    "setup",
    "grab_frames",
    "launch",
    "play",
    "generate",
    "activate",
    "deactivate",
    "list",
    "train",
    "capture"
]


def execute():
    command = sys.argv[1]

    if command not in valid_commands:
        raise Exception("'%s' is not a valid Serpent command." % command)

    command_function_mapping[command](*sys.argv[2:])


def setup():
    clear_terminal()
    display_serpent_logo()
    print("")

    # Copy Config Templates
    print("Creating Configuration Files...")

    first_run = True

    for root, directories, files in os.walk(os.getcwd()):
        for file in files:
            if file == "offshoot.yml":
                first_run = False
                break

        if not first_run:
            break

    if not first_run:
        confirm = input("It appears that the setup process had already been performed. Are you sure you want to proceed? Some important files will be overwritten! (One of: 'YES', 'NO'):\n")

        if confirm not in ["YES", "NO"]:
            confirm = "NO"

        if confirm == "NO":
            sys.exit()

    shutil.rmtree(os.path.join(os.getcwd(), "config"), ignore_errors=True)

    shutil.copytree(
        os.path.join(os.path.dirname(__file__), "config"),
        os.path.join(os.getcwd(), "config")
    )

    # Copy Offshoot Files
    shutil.copy(
        os.path.join(os.path.dirname(__file__), "offshoot.yml"),
        os.path.join(os.getcwd(), "offshoot.yml")
    )

    shutil.copy(
        os.path.join(os.path.dirname(__file__), "offshoot.manifest.json"),
        os.path.join(os.getcwd(), "offshoot.manifest.json")
    )

    # Decide on CPU or GPU Tensorflow
    tensorflow_backend = input("\nWhich backend do you plan to use for Tensorflow (One of: 'CPU', 'GPU' - Note: GPU backend can only be used on NVIDIA GTX 600 series and up): \n")

    if tensorflow_backend not in ["CPU", "GPU"]:
        tensorflow_backend = "CPU"

    # Generate Platform-Specific requirements.txt
    if sys.platform in ["linux", "linux2"]:
        shutil.copy(
            os.path.join(os.path.dirname(__file__), "requirements.linux.txt"),
            os.path.join(os.getcwd(), "requirements.txt")
        )
    elif sys.platform == "darwin":
        raise Exception("Mac OS is not supported at the moment... :(")
    elif sys.platform == "win32":
        shutil.copy(
            os.path.join(os.path.dirname(__file__), "requirements.win32.txt"),
            os.path.join(os.getcwd(), "requirements.txt")
        )

    if tensorflow_backend == "CPU":
        with open(os.path.join(os.getcwd(), "requirements.txt"), "r") as f:
            contents = f.read()

        contents = contents.replace("tensorflow-gpu", "tensorflow")

        with open(os.path.join(os.getcwd(), "requirements.txt"), "w") as f:
            f.write(contents)

    # Install the dependencies
    print("Installing dependencies...")
    subprocess.call(shlex.split("pip install -r requirements.txt"))

    # Create Dataset Directories
    os.makedirs(os.path.join(os.getcwd(), "datasets/collect_frames"))
    os.makedirs(os.path.join(os.getcwd(), "datasets/collect_frames_for_context"))
    os.makedirs(os.path.join(os.getcwd(), "datasets/current"))


def grab_frames(width, height, x_offset, y_offset):
    from serpent.frame_grabber import FrameGrabber

    frame_grabber = FrameGrabber(
        width=int(width),
        height=int(height),
        x_offset=int(x_offset),
        y_offset=int(y_offset)
    )

    frame_grabber.start()


def activate(plugin_name):
    subprocess.call(shlex.split(f"offshoot install {plugin_name}"))


def deactivate(plugin_name):
    subprocess.call(shlex.split(f"offshoot uninstall {plugin_name}"))


def list():
    plugin_names = set()

    for root, directories, files in os.walk(offshoot.config['file_paths']['plugins']):
        if root != offshoot.config['file_paths']['plugins']:
            break

        for directory in directories:
            plugin_names.add(directory)

    manifest_plugin_names = set()

    for plugin_name in offshoot.Manifest().list_plugins().keys():
        manifest_plugin_names.add(plugin_name)

    active_plugins = plugin_names & manifest_plugin_names
    inactive_plugins = plugin_names - manifest_plugin_names

    clear_terminal()

    print("ACTIVE Plugins:\n")
    print("\n".join(active_plugins or ["No active plugins..."]))

    print("\nINACTIVE Plugins:\n")
    print("\n".join(inactive_plugins or ["No inactive plugins..."]))


def launch(game_name):
    game_class_name = f"Serpent{game_name}Game"

    game = game_class_mapping.get(game_class_name)

    if game is None:
        raise Exception(f"Game '{game_name}' wasn't found. Make sure the plugin is installed.")

    game().launch()


def play(game_name, game_agent_name):
    game_class_name = f"Serpent{game_name}Game"

    game_class = game_class_mapping.get(game_class_name)

    if game_class is None:
        raise Exception(f"Game '{game_name}' wasn't found. Make sure the plugin is installed.")

    game = game_class()
    game.launch(dry_run=True)

    game_agent_class = game_agent_class_mapping.get(game_agent_name)

    if game_agent_class is None:
        raise Exception(f"Game Agent '{game_agent_name}' wasn't found. Make sure the plugin is installed.")

    game.play(game_agent_class_name=game_agent_name)


def generate(plugin_type):
    if plugin_type == "game":
        generate_game_plugin()
    elif plugin_type == "game_agent":
        generate_game_agent_plugin()
    else:
        raise Exception(f"'{plugin_type}' is not a valid plugin type...")


def train(training_type, *args):
    if training_type == "context":
        train_context(*args)


def capture(capture_type, game_name, interval=1, extra=None):
    game_class_name = f"Serpent{game_name}Game"

    game_class = game_class_mapping.get(game_class_name)

    if game_class is None:
        raise Exception(f"Game '{game_name}' wasn't found. Make sure the plugin is installed.")

    game = game_class()

    game.launch(dry_run=True)

    if capture_type not in ["frame", "context", "region"]:
        raise Exception("Invalid capture command.")

    if capture_type == "frame":
        game.play(frame_handler="COLLECT_FRAMES", interval=int(interval))
    elif capture_type == "context":
        game.play(frame_handler="COLLECT_FRAMES_FOR_CONTEXT", interval=int(interval), context=extra)
    elif capture_type == "region":
        game.play(frame_handler="COLLECT_FRAME_REGIONS", interval=int(interval), region=extra)


def generate_game_plugin():
    clear_terminal()
    display_serpent_logo()
    print("")

    game_name = input("What is the name of the game? (Titleized, No Spaces i.e. AwesomeGame): \n")
    game_platform = input("How is the game launched? (One of: 'steam', 'executable'): \n")

    if game_name in [None, ""]:
        raise Exception("Invalid game name.")

    if game_platform not in ["steam", "executable"]:
        raise Exception("Invalid game platform.")

    prepare_game_plugin(game_name, game_platform)


def generate_game_agent_plugin():
    clear_terminal()
    display_serpent_logo()
    print("")

    game_agent_name = input("What is the name of the game agent? (Titleized, No Spaces i.e. AwesomeGameAgent): \n")

    if game_agent_name in [None, ""]:
        raise Exception("Invalid game agent name.")

    prepare_game_agent_plugin(game_agent_name)


def prepare_game_plugin(game_name, game_platform):
    plugin_destination_path = f"{offshoot.config['file_paths']['plugins']}/Serpent{game_name}GamePlugin"

    shutil.copytree(
        os.path.join(os.path.dirname(__file__), "templates/SerpentGamePlugin"),
        plugin_destination_path
    )

    # Plugin Definition
    with open(f"{plugin_destination_path}/plugin.py", "r") as f:
        contents = f.read()

    contents = contents.replace("SerpentGamePlugin", f"Serpent{game_name}GamePlugin")
    contents = contents.replace("serpent_game.py", f"serpent_{game_name}_game.py")

    with open(f"{plugin_destination_path}/plugin.py", "w") as f:
        f.write(contents)

    shutil.move(f"{plugin_destination_path}/files/serpent_game.py", f"{plugin_destination_path}/files/serpent_{game_name}_game.py")

    # Game
    with open(f"{plugin_destination_path}/files/serpent_{game_name}_game.py", "r") as f:
        contents = f.read()

    contents = contents.replace("SerpentGame", f"Serpent{game_name}Game")
    contents = contents.replace("MyGameAPI", f"{game_name}API")

    if game_platform == "steam":
        contents = contents.replace("PLATFORM", "steam")
        contents = contents.replace('kwargs["executable_path"] = "EXECUTABLE_PATH"', "")
    elif game_platform == "executable":
        contents = contents.replace("PLATFORM", "executable")
        contents = contents.replace('kwargs["app_id"] = "APP_ID"', "")
        contents = contents.replace('kwargs["app_args"] = "APP_ARGS"', "")

    with open(f"{plugin_destination_path}/files/serpent_{game_name}_game.py", "w") as f:
        f.write(contents)

    # Game API
    with open(f"{plugin_destination_path}/files/api/api.py", "r") as f:
        contents = f.read()

    contents = contents.replace("MyGameAPI", f"{game_name}API")

    with open(f"{plugin_destination_path}/files/api/api.py", "w") as f:
        f.write(contents)


def prepare_game_agent_plugin(game_agent_name):
    plugin_destination_path = f"{offshoot.config['file_paths']['plugins']}/Serpent{game_agent_name}GameAgentPlugin"

    shutil.copytree(
        os.path.join(os.path.dirname(__file__), "templates/SerpentGameAgentPlugin"),
        plugin_destination_path
    )

    with open(f"{plugin_destination_path}/plugin.py", "r") as f:
        contents = f.read()

    contents = contents.replace("SerpentGameAgentPlugin", f"Serpent{game_agent_name}GameAgentPlugin")
    contents = contents.replace("serpent_game_agent.py", f"serpent_{game_agent_name}_game_agent.py")

    with open(f"{plugin_destination_path}/plugin.py", "w") as f:
        f.write(contents)

    shutil.move(f"{plugin_destination_path}/files/serpent_game_agent.py", f"{plugin_destination_path}/files/serpent_{game_agent_name}_game_agent.py")

    with open(f"{plugin_destination_path}/files/serpent_{game_agent_name}_game_agent.py", "r") as f:
        contents = f.read()

    contents = contents.replace("SerpentGameAgent", f"Serpent{game_agent_name}GameAgent")

    with open(f"{plugin_destination_path}/files/serpent_{game_agent_name}_game_agent.py", "w") as f:
        f.write(contents)


def train_context(epochs=3):
    from serpent.machine_learning.context_classification.context_classifier import ContextClassifier
    ContextClassifier.executable_train(epochs=int(epochs))

command_function_mapping = {
    "setup": setup,
    "grab_frames": grab_frames,
    "activate": activate,
    "deactivate": deactivate,
    "list": list,
    "launch": launch,
    "play": play,
    "generate": generate,
    "train": train,
    "capture": capture
}

if __name__ == "__main__":
    execute()
