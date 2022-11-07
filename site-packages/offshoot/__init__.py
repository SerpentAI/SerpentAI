from offshoot.base import *

from offshoot.plugin import Plugin, PluginError
from offshoot.pluggable import Pluggable
from offshoot.manifest import Manifest


config = load_configuration("offshoot.yml")
pluggable_classes = lambda: map_pluggable_classes(config)
