import json

import os
import os.path

import offshoot


class Manifest:

    def __init__(self, **kwargs):
        self.file_path = kwargs.get("file_path", "offshoot.manifest.json")

        if not os.path.isfile(self.file_path):
            with open(self.file_path, "w") as f:
                f.write(json.dumps({"plugins": {}}))

    def list_plugins(self):
        with open(self.file_path, "r") as f:
            manifest = json.loads(f.read())

        return manifest["plugins"]

    def contains_plugin(self, plugin_name):
        with open(self.file_path, "r") as f:
            manifest = json.loads(f.read())

        return plugin_name in manifest["plugins"]

    def add_plugin(self, plugin_name):
        with open(self.file_path, "a+") as f:
            f.seek(0)
            manifest = json.loads(f.read())

            exec("from %s.%s.plugin import %s" % (
                offshoot.config["file_paths"]["plugins"],
                plugin_name,
                plugin_name
            ))

            plugin_class = eval(plugin_name)

            manifest["plugins"][plugin_name] = {
                "name": plugin_name,
                "version": plugin_class.version,
                "files": plugin_class.files,
                "plugins": plugin_class.plugins,
                "libraries": plugin_class.libraries,
                "config": plugin_class.config
            }

            f.truncate(0)
            f.write(json.dumps(manifest, indent=4))

    def remove_plugin(self, plugin_name):
        with open(self.file_path, "a+") as f:
            f.seek(0)
            manifest = json.loads(f.read())

            if plugin_name in manifest["plugins"]:
                del manifest["plugins"][plugin_name]

                f.truncate(0)
                f.write(json.dumps(manifest, indent=4))

    def plugin_files_for_pluggable(self, pluggable):
        files = list()

        with open(self.file_path, "r") as f:
            manifest = json.loads(f.read())

        for name, metadata in manifest["plugins"].items():
            for file in metadata["files"]:
                if file.get("pluggable") == pluggable:
                    files.append(("plugins/%s/files/%s".replace("/", os.sep) % (name, file.get("path")), file.get("pluggable")))

        return files
