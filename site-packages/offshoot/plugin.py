import os
import os.path

import yaml

import offshoot


class PluginError(Exception):
    pass


class Plugin:
    name = "Plugin"
    version = "0.0.0"

    libraries = list()
    plugins = list()
    files = list()
    config = dict()

    @classmethod
    def on_install(cls):
        print("\n\n%s was installed successfully!" % cls.__name__)

    @classmethod
    def on_uninstall(cls):
        print("\n\n%s was uninstalled successfully!" % cls.__name__)

    @classmethod
    def install(cls):
        if offshoot.config["allow"]["plugins"] is True:
            cls.verify_plugin_dependencies()
        if offshoot.config["allow"]["files"] is True:
            cls.install_files()
        if offshoot.config["allow"]["config"] is True:
            cls.install_configuration()
        if offshoot.config["allow"]["libraries"] is True:
            cls.install_libraries()
        if offshoot.config["allow"]["callbacks"] is True:
            cls.on_install()

        manifest = offshoot.Manifest()
        manifest.add_plugin(cls.name)

    @classmethod
    def uninstall(cls):
        if offshoot.config["allow"]["files"] is True:
            cls.uninstall_files()
        if offshoot.config["allow"]["config"] is True:
            cls.uninstall_configuration()
        if offshoot.config["allow"]["libraries"] is True:
            cls.uninstall_libraries()
        if offshoot.config["allow"]["callbacks"] is True:
            cls.on_uninstall()

        manifest = offshoot.Manifest()
        manifest.remove_plugin(cls.name)

    @classmethod
    def verify_plugin_dependencies(cls):
        print("\nOFFSHOOT PLUGIN INSTALL: Verifying that plugin dependencies are installed...\n")

        manifest = offshoot.Manifest()

        missing_plugin_names = list()

        for plugin_name in cls.plugins:
            if not manifest.contains_plugin(plugin_name):
                missing_plugin_names.append(plugin_name)

        if len(missing_plugin_names):
            raise PluginError("One or more plugin dependencies are not met: %s. Please install them before continuing..." % ", ".join(missing_plugin_names))

    @classmethod
    def install_files(cls):
        print("\nOFFSHOOT PLUGIN INSTALL: Installing files...\n")

        is_success = True
        install_messages = list()

        installed_files = list()
        pluggable_classes = offshoot.pluggable_classes()

        try:
            for file_dict in cls.files:
                plugin_file_path = "%s/%s/files/%s".replace("/", os.sep) % (offshoot.config["file_paths"]["plugins"], cls.name, file_dict["path"])

                # Pluggable Validation
                if "pluggable" in file_dict:
                    is_valid, messages = cls._validate_file_for_pluggable(plugin_file_path, file_dict["pluggable"])

                    if not is_valid:
                        is_success = False
                        list(map(lambda m: install_messages.append("\n%s: %s" % (file_dict["path"], m)), messages))

                        continue

                installed_files.append(file_dict)

                # File Callback
                if "pluggable" in file_dict:
                    pluggable_classes[file_dict["pluggable"]].on_file_install(**file_dict)

            if not is_success:
                raise PluginError("Offshoot Plugin File Install Errors: %s" % "".join(install_messages))
        except PluginError as e:
            print("\nThere was a problem during installation... Reverting!")

            # Trigger File Uninstall Callback
            for file_dict in installed_files:
                if "pluggable" in file_dict:
                    pluggable_classes[file_dict["pluggable"]].on_file_uninstall(**file_dict)

            manifest = offshoot.Manifest()
            manifest.remove_plugin(cls.name)

            raise e

    @classmethod
    def uninstall_files(cls):
        print("\nOFFSHOOT PLUGIN UNINSTALL: Uninstalling files...\n")

        for file_dict in cls.files:
            if "pluggable" in file_dict:
                offshoot.pluggable_classes()[file_dict["pluggable"]].on_file_uninstall(**file_dict)

    @classmethod
    def install_configuration(cls):
        print("\n\nOFFSHOOT PLUGIN INSTALL: Updating configuration file (%s)...\n" % offshoot.config["file_paths"]["config"])

        if len(offshoot.config["file_paths"]["config"].split(os.sep)) > 1:
            configuration_path = os.sep.join(offshoot.config["file_paths"]["config"].split(os.sep)[:-1])

            if not os.path.isdir(configuration_path):
                raise PluginError("The plugin configuration directory ('%s') doesn't exist! Either create it or modify the Offshoot configuration file to point to an existing directory and restart the installation." % configuration_path)

        if not len(cls.config or dict()):
            return None

        if offshoot.config["sandbox_configuration_keys"]:
            config = dict()
            config[cls.name] = cls.config
        else:
            config = cls.config

        if not os.path.isfile(offshoot.config["file_paths"]["config"]):
            with open(offshoot.config["file_paths"]["config"], "w") as f:
                f.write(yaml.dump(config))
        else:
            with open(offshoot.config["file_paths"]["config"], "r") as f:
                existing_config = yaml.safe_load(f.read()) or dict()
                config = {**config, **existing_config}

            with open(offshoot.config["file_paths"]["config"], "w") as f:
                f.write(yaml.dump(config, default_flow_style=False))

        print("Merging the following keys:")
        print(config)

    @classmethod
    def uninstall_configuration(cls):
        print("\n\nOFFSHOOT PLUGIN UNINSTALL: Updating configuration file (%s)...\n" % offshoot.config["file_paths"]["config"])

        if len(offshoot.config["file_paths"]["config"].split(os.sep)) > 1:
            configuration_path = os.sep.join(offshoot.config["file_paths"]["config"].split(os.sep)[:-1])

            if not os.path.isdir(configuration_path):
                raise PluginError("The plugin configuration directory ('%s') doesn't exist! Either create it or modify the Offshoot configuration file to point to an existing directory and restart the installation." % configuration_path)

        if not len(cls.config or dict()):
            return None

        if os.path.isfile(offshoot.config["file_paths"]["config"]):
            with open(offshoot.config["file_paths"]["config"], "r") as f:
                config = yaml.safe_load(f.read())

            if offshoot.config["sandbox_configuration_keys"]:
                config.pop(cls.name)
            else:
                for key in cls.config:
                    config.pop(key)

            with open(offshoot.config["file_paths"]["config"], "w") as f:
                f.write(yaml.dump(config))

            print("Removing the following keys:")
            print(config)

    @classmethod
    def install_libraries(cls):
        print("\n\nOFFSHOOT PLUGIN INSTALL: Updating libraries (%s)...\n" % offshoot.config["file_paths"]["libraries"])

        if len(offshoot.config["file_paths"]["libraries"].split(os.sep)) > 1:
            libraries_path = os.sep.join(offshoot.config["file_paths"]["libraries"].split(os.sep)[:-1])

            if not os.path.isdir(libraries_path):
                raise PluginError("The plugin libraries directory ('%s') doesn't exist! Either create it or modify the Offshoot configuration file to point to an existing directory and restart the installation." % libraries_path)

        if not len(cls.libraries or list()):
            return None

        cls._write_plugin_requirement_blocks_to(offshoot.config["file_paths"]["libraries"])

        print("Merging the following libraries:")
        print("\n".join(cls.libraries))

        print("\nLibraries updated successfully. Make sure to run 'pip install -r %s' to fulfill the plugin requirements" % offshoot.config["file_paths"]["libraries"])

    @classmethod
    def uninstall_libraries(cls):
        print("\n\nOFFSHOOT PLUGIN UNINSTALL: Updating libraries (%s)...\n" % offshoot.config["file_paths"]["libraries"])

        if len(offshoot.config["file_paths"]["libraries"].split(os.sep)) > 1:
            libraries_path = os.sep.join(offshoot.config["file_paths"]["libraries"].split(os.sep)[:-1])

            if not os.path.isdir(libraries_path):
                raise PluginError("The plugin libraries directory ('%s') doesn't exist! Either create it or modify the Offshoot configuration file to point to an existing directory and restart the installation." % libraries_path)

        if not len(cls.libraries or list()):
            return None

        cls._remove_plugin_requirement_block_from(offshoot.config["file_paths"]["libraries"])

        print("Removing the following libraries:")
        print("\n".join(cls.libraries))

        print("\nLibraries updated successfully. Make sure to run 'pip install -r %s' to fulfill the plugin requirements" % offshoot.config["file_paths"]["libraries"])

    @classmethod
    def _validate_file_for_pluggable(cls, file_path, pluggable):
        pluggable_classes = offshoot.pluggable_classes()

        if pluggable not in pluggable_classes:
            raise PluginError("The Plugin definition specifies an invalid pluggable: %s => %s" % (file_path, pluggable))

        pluggable_class = pluggable_classes[pluggable]

        return offshoot.validate_plugin_file(
            file_path,
            pluggable,
            pluggable_class.method_directives()
        )

    @classmethod
    def _generate_plugin_requirement_block(cls):
        requirement_lines = ["### %s Requirements ###" % cls.name]

        for library in sorted(cls.libraries):
            requirement_lines.append(library)

        requirement_lines.append("######")

        return requirement_lines

    @classmethod
    def _extract_plugin_requirement_blocks_from(cls, file_path):
        plugin_requirement_blocks = dict()
        current_plugin = None

        if not os.path.isfile(file_path):
            return dict()

        with open(file_path, "r") as f:
            for line in f:
                if line == "":
                    continue

                if line.startswith("### "):
                    current_plugin = line.split("### ")[1].split(" ###")[0].strip()
                    plugin_requirement_blocks[current_plugin] = [line.strip()]
                    continue

                if line.startswith("######"):
                    plugin_requirement_blocks[current_plugin].append(line.strip())
                    current_plugin = None
                    continue

                if current_plugin:
                    plugin_requirement_blocks[current_plugin].append(line.strip())

        return plugin_requirement_blocks

    @classmethod
    def _write_plugin_requirement_blocks_to(cls, file_path):
        plugin_requirement_blocks = cls._extract_plugin_requirement_blocks_from(file_path)
        plugin_requirement_blocks["%s Requirements" % cls.name] = cls._generate_plugin_requirement_block()

        with open(file_path, "w") as f:
            for name, requirements in plugin_requirement_blocks.items():
                f.write("\n".join(requirements))
                f.write("\n\n")

    @classmethod
    def _remove_plugin_requirement_block_from(cls, file_path):
        plugin_requirement_blocks = cls._extract_plugin_requirement_blocks_from(file_path)
        plugin_requirement_blocks.pop("%s Requirements" % cls.name)

        with open(file_path, "w") as f:
            for name, requirements in plugin_requirement_blocks.items():
                f.write("\n".join(requirements))
                f.write("\n\n")
