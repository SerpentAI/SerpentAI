import sys
import subprocess


def clear_terminal():
    if sys.platform in ["linux", "linux2"]:
        print("\033c")
    elif sys.platform == "darwin":
        print("\033c")
    elif sys.platform == "win32":
        subprocess.call(["cls"], shell=True)
