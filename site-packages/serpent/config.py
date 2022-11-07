import yaml
import yaml.scanner

import offshoot

config = dict()
plugin_config = dict()

try:
    with open("config/config.yml", "r") as f:
        try:
            config = yaml.safe_load(f) or {}
        except yaml.scanner.ScannerError as e:
            raise Exception("Configuration file at 'config/config.yml' contains invalid YAML...")
        except Exception as e:
            print(type(e))
except FileNotFoundError as e:
    raise Exception("Configuration file not found at: 'config/config.yml'...")

try:
    with open(offshoot.config["file_paths"]["config"], "r") as f:
        try:
            plugin_config = yaml.safe_load(f) or {}
        except yaml.scanner.ScannerError as e:
            raise Exception(f"Configuration file at '{offshoot.config['file_paths']['config']}' contains invalid YAML...")
        except Exception as e:
            print(type(e))
except FileNotFoundError as e:
    raise Exception(f"Configuration file not found at: '{offshoot.config['file_paths']['config']}'...")

config = {**plugin_config, **config}
