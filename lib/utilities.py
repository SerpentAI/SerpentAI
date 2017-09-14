import sys
import subprocess


def clear_terminal():
    if sys.platform in ["linux", "linux2"]:
        print("\033c")
    elif sys.platform == "darwin":
        print("\033c")
    elif sys.platform == "win32":
        subprocess.call(["cls"], shell=True)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
