#!/usr/bin/env python
import sys
import os

import subprocess

import offshoot

valid_commands = ["init", "install", "uninstall"]


def execute():
    if len(sys.argv) == 2:
        command = sys.argv[1]

        if command not in valid_commands:
            raise Exception("'%s' is not a valid Offshoot command." % command)

        if command == "init":
            init()
    elif len(sys.argv) > 2:
        command, args = sys.argv[1], sys.argv[2:]

        if command not in valid_commands:
            raise Exception("'%s' is not a valid Offshoot command." % command)

        if command == "install":
            install(args[0])
        elif command == "uninstall":
            uninstall(args[0])


def install(plugin):
    print("OFFSHOOT: Attempting to install %s..." % plugin)

    plugin_directory = offshoot.config.get("file_paths").get("plugins")
    plugin_path = "%s/%s/plugin.py".replace("/", os.sep) % (plugin_directory, plugin)

    plugin_module_string = plugin_path.replace(os.sep, ".").replace(".py", "")

    subprocess.call([sys.executable.split(os.sep)[-1], "-m", "%s" % plugin_module_string, "install"])


def uninstall(plugin):
    print("OFFSHOOT: Attempting to uninstall %s..." % plugin)

    plugin_directory = offshoot.config.get("file_paths").get("plugins")
    plugin_path = "%s/%s/plugin.py".replace("/", os.sep) % (plugin_directory, plugin)

    plugin_module_string = plugin_path.replace(os.sep, ".").replace(".py", "")

    subprocess.call([sys.executable.split(os.sep)[-1], "-m", "%s" % plugin_module_string, "uninstall"])


def init():
    import warnings
    warnings.filterwarnings("ignore")

    print("OFFSHOOT: Generating configuration file...")
    offshoot.generate_configuration_file()
    print("OFFSHOOT: Initialized successfully!")


if __name__ == "__main__":
    execute()
