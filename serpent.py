#!/usr/bin/env python
import sys
import shutil

import offshoot

from lib.utilities import clear_terminal

from lib.machine_learning.context_classification.context_classifier import ContextClassifier

game_class_mapping = offshoot.discover("Game")
game_agent_class_mapping = offshoot.discover("GameAgent")

valid_commands = ["launch", "play", "generate", "activate", "deactivate", "train", "capture"]


def execute():
    command = sys.argv[1]

    if command not in valid_commands:
        raise Exception("'%s' is not a valid Serpent command." % command)

    command_function_mapping[command](*sys.argv[2:])


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

    game_name = input("What is the name of the game? (Titleized, No Spaces i.e. AwesomeGame): \n")
    game_platform = input("How is the game launched? (One of: 'steam', 'executable'): \n")

    if game_name in [None, ""]:
        raise Exception("Invalid game name.")

    if game_platform not in ["steam", "executable"]:
        raise Exception("Invalid game platform.")

    prepare_game_plugin(game_name, game_platform)


def generate_game_agent_plugin():
    clear_terminal()

    game_agent_name = input("What is the name of the game agent? (Titleized, No Spaces i.e. AwesomeGameAgent): \n")

    if game_agent_name in [None, ""]:
        raise Exception("Invalid game agent name.")

    prepare_game_agent_plugin(game_agent_name)


def prepare_game_plugin(game_name, game_platform):
    plugin_destination_path = f"{offshoot.config['file_paths']['plugins']}/Serpent{game_name}GamePlugin"

    shutil.copytree("templates/SerpentGamePlugin", plugin_destination_path)

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

    shutil.copytree("templates/SerpentGameAgentPlugin", plugin_destination_path)

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
    ContextClassifier.executable_train(epochs=int(epochs))

command_function_mapping = {
    "launch": launch,
    "play": play,
    "generate": generate,
    "train": train,
    "capture": capture
}

if __name__ == "__main__":
    execute()
