from serpent.window_controller import WindowController
from multiprocessing import Process, Queue
from subprocess import check_output, call, CalledProcessError
import multiprocessing
import re


class CmdRunner:
    def __init__(self):
        multiprocessing.set_start_method('spawn')
        self.inQueue = Queue()
        self.outQueue = Queue()
        self.cmdHostProcess = multiprocessing.Process(target=self.cmdloop, args=(self.inQueue, self.outQueue))
        self.cmdHostProcess.daemon = True
        self.cmdHostProcess.start()

    def callCommand(self, command):
        self.inQueue.put(command)
        return self.outQueue.get()

    @staticmethod
    def cmdloop(inQueue, outQueue):
        while True:
            result = None
            cmd = inQueue.get()
            command = cmd[0]
            opt = cmd[1]
            try:
                if opt == "check":
                    result = check_output(command, shell=True)
                elif opt == "call":
                    call(command, shell=True)
            except CalledProcessError as e:
                result = e

            outQueue.put(result)


class LinuxWindowController(WindowController):
    def __init__(self):
        self.cmdRunner = CmdRunner()

    def locate_window(self, name):
        return self.cmdRunner.callCommand([f"xdotool search --onlyvisible --name \"^{name}$\"", "check"]).decode(
            "utf-8").strip()

    def move_window(self, window_id, x, y):
        self.cmdRunner.callCommand([f"xdotool windowmove {window_id} {x} {y}", "call"])

    def resize_window(self, window_id, width, height):
        self.cmdRunner.callCommand([f"xdotool windowsize {window_id} {width} {height}", "call"])

    def focus_window(self, window_id):
        self.cmdRunner.callCommand([f"xdotool windowactivate {window_id}", "call"])

    def bring_window_to_top(self, window_id):
        self.cmdRunner.callCommand([f"xdotool windowactivate {window_id}", "call"])

    def is_window_focused(self, window_id):
        focused_window_id = self.cmdRunner.callCommand(["xdotool getwindowfocus", "check"]).decode("utf-8").strip()
        return focused_window_id == window_id

    def get_focused_window_name(self):
        focused_window_id = self.cmdRunner.callCommand(["xdotool getwindowfocus", "check"]).decode("utf-8").strip()
        return self.cmdRunner.callCommand([f"xdotool getwindowname {focused_window_id}", "check"]).decode(
            "utf-8").strip()

    def get_window_geometry(self, window_id):
        geometry = dict()

        window_geometry = self.cmdRunner.callCommand([f"xdotool getwindowgeometry {window_id}", "check"]).decode(
            "utf-8").strip()
        size = re.match(r"\s+Geometry: ([0-9]+x[0-9]+)", window_geometry.split("\n")[2]).group(1).split("x")

        geometry["width"] = int(size[0])
        geometry["height"] = int(size[1])

        window_information = self.cmdRunner.callCommand([f"xwininfo -id {window_id}", "check"]).decode("utf-8").strip()
        geometry["x_offset"] = int(
            re.match(r"\s+Absolute upper-left X:\s+([0-9]+)", window_information.split("\n")[2]).group(1))
        geometry["y_offset"] = int(
            re.match(r"\s+Absolute upper-left Y:\s+([0-9]+)", window_information.split("\n")[3]).group(1))

        return geometry
