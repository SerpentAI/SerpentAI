import warnings

warnings.filterwarnings("ignore")  # Silence warnings in CLI

import os
import pathlib
import shutil
import subprocess

# Some imports are inline in CLI commands to keep initialization times low

import click

from serpent.utilities import (
    clear_terminal,
    display_serpent_logo,
    is_windows,
    is_linux,
)


# On Windows, disable the Fortran CTRL-C handler that gets installed with SciPy
if is_windows:
    os.environ["FOR_DISABLE_CONSOLE_CTRL_HANDLER"] = "T"

VERSION = "2020.2.1"


@click.command(help="Perform Serpent.AI setup")
def setup():
    clear_terminal()
    display_serpent_logo()

    print("")
    print("Serpent.AI Setup")
    print("")

    data_path = _get_data_path()
    source_path = pathlib.Path(__file__).parent

    if data_path.exists():
        confirm = input(
            """It appears this machine has already been set up to use Serpent.AI.
Do you want to continue and remove all previous data? 
(One of: 'YES', 'NO') """
        )

        if confirm.lower() != "yes":
            return

        print("")
        print("Removing previous data...")
        print("")

        shutil.rmtree(data_path, ignore_errors=True)

    print("Creating Serpent.AI data directory...")
    data_path.mkdir()

    print("Populating Serpent.AI data directory...")

    data_path.joinpath("plugins/games").mkdir(parents=True, exist_ok=True)
    data_path.joinpath("plugins/game_agents").mkdir(parents=True, exist_ok=True)
    data_path.joinpath("plugins/rl_agents").mkdir(parents=True, exist_ok=True)

    data_path.joinpath("game_agents").mkdir()

    # TODO: Also copy bundled official plugins once we have them

    shutil.copy(
        source_path.joinpath("serpent/config/config.json"),
        data_path.joinpath("config.json"),
    )

    print("")
    print("Serpent.AI Setup Complete!")


@click.command(help="Update Serpent.AI to the latest version")
def update():
    import shlex

    clear_terminal()
    display_serpent_logo()
    print("")

    print("Updating Serpent.AI to the latest version...")
    print("")

    subprocess.call(shlex.split("pip install --upgrade SerpentAI"))

    # TODO: Handle files that were created with the setup commands
    #       and have likely been modified by the user. This is probably
    #       not an easy task.

    print("")
    print("Update Successful!")


@click.command(help="Launch the Serpent.AI GUI")
def gui():
    # TODO: Implement
    pass


@click.command(help="Download additional tools and modules")
@click.argument("module")
def download(module):
    valid_modules = ("tesseract",)

    if module not in valid_modules:
        print(f"'{module}' is not a valid download module...")
        return

    if module == "tesseract":
        if is_windows():
            print(f"Downloading module 'tesseract' to tools directory...")
            _download_module(
                "https://github.com/SerpentAI/SerpentAI/releases/download/optional/tesseract_4.00.00a_win_amd64.zip",
                pathlib.Path("tools/tesseract.zip"),
            )
        elif is_linux():
            print(
                "Downloading module 'tesseract' not supported on Linux. Please install Tesseract with your package manager."
            )


@click.command(help="Download and install a plugin from GitHub")
def download_plugin():
    # TODO: Implement
    pass


@click.command(help="Open the plugin directory")
def show_plugins():
    # TODO: Implement
    pass


@click.command(help="List all installed plugins")
def plugins():
    # TODO: Implement
    pass


@click.command(help="List the installed game plugins")
def games():
    # TODO: Implement
    pass


@click.command(help="List the installed game agent plugins")
def game_agents():
    # TODO: Implement
    pass


@click.command(help="List the installed reinforcement learning agent plugins")
def rl_agents():
    # TODO: Implement
    pass


@click.command(help="Display instructions from a game plugin")
def game_instructions():
    # TODO: Implement
    pass


@click.command(help="Launch a game")
def launch():
    # TODO: Implement
    pass


@click.command(help="Train a game agent")
def train():
    # TODO: Implement
    pass


@click.command(help="Play a game using a game agent")
def play():
    # TODO: Implement
    pass


@click.command(help="Record inputs while playing a game")
def record():
    # TODO: Implement
    pass


# SDK
# These commands are aimed at developers wanting to create plugins for Serpent.AI
@click.command(help="SDK - Perform Serpent.AI SDK setup in the current directory")
def sdk_setup():
    import serpent.ocr

    clear_terminal()
    display_serpent_logo()

    print("")
    print("Serpent.AI SDK Setup")
    print("")

    # First, check for required 3rd-party tools
    print("Checking for required 3rd-party tools...")

    have_tesseract = serpent.ocr.is_tesseract_available()

    print(f"Tesseract: {'FOUND' if have_tesseract else 'NOT FOUND'}")
    print("")

    if not have_tesseract:
        print("No Tesseract executable could be found... Setup cannot continue.")
        print("")

        if is_windows():
            print(
                "For an easy installation of Tesseract, run 'serpent download tesseract"
            )

    # Has setup already been performed?
    if pathlib.Path(".serpent-sdk").is_file():
        confirm = input(
            """The current directory has already been set up to use the Serpent.AI SDK.
Do you want to continue and potentially overwrite important files? 
(One of: 'YES', 'NO') """
        )

        if confirm.lower() != "yes":
            return

    current_path = pathlib.Path.cwd()
    source_path = pathlib.Path(__file__).parent

    # Config
    config_path = pathlib.Path("config_sdk.json")

    if config_path.is_file():
        config_path.unlink()

    shutil.copy(source_path.joinpath("serpent/config/config_sdk.json"), config_path)

    # Plugins
    plugins_path = current_path.joinpath("plugins")

    if plugins_path.is_dir():
        shutil.rmtree(plugins_path, ignore_errors=True)

    current_path.joinpath("plugins/games").mkdir(parents=True, exist_ok=True)
    current_path.joinpath("plugins/game_agents").mkdir(parents=True, exist_ok=True)
    current_path.joinpath("plugins/rl_agents").mkdir(parents=True, exist_ok=True)

    # Datasets
    datasets_path = current_path.joinpath("datasets")

    if datasets_path.is_dir():
        shutil.rmtree(datasets_path, ignore_errors=True)

    current_path.joinpath("datasets/frames").mkdir(parents=True, exist_ok=True)
    current_path.joinpath("datasets/recordings").mkdir(parents=True, exist_ok=True)

    # Dot File
    open(".serpent-sdk", "w").close()

    print("")
    print("Serpent.AI SDK Setup Complete!")


@click.command(help="SDK - Find the window name of a game")
def sdk_window_name():
    # TODO: Implement
    pass


@click.command(help="SDK - CUDA test for Serpent.AI")
def sdk_test_cuda():
    import torch

    # TODO: Try to also detect incompatible hardware. This likely just detects if CUDA
    #       is bundled with the installed PyTorch version
    if torch.cuda.is_available():
        print("Success! CUDA can be used by Serpent.AI")
    else:
        print("Failure! CUDA cannot be used by Serpent.AI")


@click.command(help="SDK - Test Serpent.AI input capture")
def sdk_test_input_capture():
    # TODO: Implement
    pass


@click.command(help="SDK - Capture game frames")
def sdk_capture():
    # TODO: Implement
    pass


@click.command(help="SDK - Generate skeleton for a game plugin")
def sdk_generate_game_plugin():
    # TODO: Implement
    pass


@click.command(help="SDK - Generate skeleton for a game agent plugin")
def sdk_generate_game_agent_plugin():
    # TODO: Implement
    pass


@click.command(help="SDK - Generate skeleton for a RL agent plugin")
def sdk_generate_rl_agent_plugin():
    # TODO: Implement
    pass


@click.command(help="SDK - Package game plugin to .spg file")
def sdk_package_game_plugin():
    # TODO: Implement
    pass


@click.command(help="SDK - Package game agent plugin to .spga file")
def sdk_package_game_agent_plugin():
    # TODO: Implement
    pass


@click.command(help="SDK - Package RL agent plugin to .sprla file")
def sdk_package_rl_agent_plugin():
    # TODO: Implement
    pass


@click.command(help="SDK - Install a plugin on the system")
def sdk_install_plugin():
    # TODO: Implement
    pass


@click.command(help="SDK - Uninstall a plugin from the system")
def sdk_uninstall_plugin():
    # TODO: Implement
    pass


def _download_module(url, file_path):
    import requests
    import tqdm

    path = file_path.parent
    path.mkdir(parents=True, exist_ok=True)

    r = requests.get(url, stream=True)

    with open(file_path, "wb") as f:
        progress = tqdm.tqdm(
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            total=int(r.headers["Content-Length"]),
        )

        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                progress.update(len(chunk))
                f.write(chunk)

        progress.close()

    if str(file_path.as_posix()).endswith(".zip"):
        import zipfile

        with zipfile.ZipFile(file_path, "r") as z:
            z.extractall(path)

        file_path.unlink()

    print("Download complete!")


def _get_data_path():
    if is_windows():
        data_path = pathlib.Path(os.getenv("APPDATA")).joinpath("Serpent.AI")
    elif is_linux():
        data_path = pathlib.Path(os.getenv("HOME")).joinpath(".serpent")

    return data_path.absolute()


@click.group(invoke_without_command=True)
@click.option("--version", help="Shows Serpent.AI version", is_flag=True)
@click.option("--help", help="Shows Serpent.AI CLI commands", is_flag=True)
@click.pass_context
def cli(context, version, help):
    if version:
        print(VERSION)
        return

    if context.invoked_subcommand is None:
        print(context.get_help())
        return


# General
cli.add_command(setup)
cli.add_command(update)
cli.add_command(gui)
cli.add_command(download)
cli.add_command(show_plugins)
cli.add_command(plugins)
cli.add_command(games)
cli.add_command(game_agents)
cli.add_command(rl_agents)
cli.add_command(game_instructions)
cli.add_command(launch)
cli.add_command(train)
cli.add_command(play)
cli.add_command(record)

# SDK
cli.add_command(sdk_setup)
cli.add_command(sdk_window_name)
cli.add_command(sdk_test_cuda)
cli.add_command(sdk_test_input_capture)
cli.add_command(sdk_capture)
cli.add_command(sdk_generate_game_plugin)
cli.add_command(sdk_generate_game_agent_plugin)
cli.add_command(sdk_generate_rl_agent_plugin)
cli.add_command(sdk_package_game_plugin)
cli.add_command(sdk_package_game_agent_plugin)
cli.add_command(sdk_package_rl_agent_plugin)
cli.add_command(sdk_install_plugin)
cli.add_command(sdk_uninstall_plugin)


if __name__ == "__main__":
    cli()
