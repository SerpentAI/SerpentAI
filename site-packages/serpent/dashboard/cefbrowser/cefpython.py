#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
This library provides functions to import and initialize cefpython found in
PYTHONPATH.
"""

import atexit
import os
import signal
import sys
import tempfile

import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
kivy.require("1.8.0")


# Try import from package (PYTHONPATH)
try:
    from cefpython3 import cefpython
    Logger.info("CEFLoader: cefpython3 imported from package")
except ImportError:
    Logger.critical("CEFLoader: Failed to import cefpython")
    raise Exception("Failed to import cefpython")

cefpython_loop_event = None


def cefpython_initialize(cef_browser_cls):
    global cefpython_loop_event
    if cefpython_loop_event:
        Logger.warning(
            "CEFLoader: Attempt to initialize CEFPython another time")
        return
    try:
        md = cefpython.GetModuleDirectory()
    except Exception as e:
        raise Exception("CEFLoader: Could not define module-directory: %s" % e)
    Logger.debug("CEFLoader: Module Directory: %s", md)

    sd = tempfile.gettempdir()
    Logger.debug("CEFLoader: Storage Directory: %s", sd)

    def cef_loop(*largs):
        try:
            cefpython.MessageLoopWork()
        except Exception as e:
            print("EXCEPTION IN CEF LOOP", e)
    cefpython_loop_event = Clock.schedule_interval(cef_loop, 0.01)

    default_settings = {
        # "debug": True,
        # "log_severity": cefpython.LOGSEVERITY_INFO,
        # "release_dcheck_enabled": True,  # Enable only when debugging.
        "locales_dir_path": os.path.join(md, "locales"),
        "resources_dir_path": md,
        "browser_subprocess_path": os.path.join(md, "subprocess"),
        "unique_request_context_per_browser": True,
        "context_menu": {"enabled": False, },
        "downloads_enabled": False,
    }
    default_settings.update(cef_browser_cls._settings)
    caches_path = os.path.join(sd, "caches")
    cookies_path = os.path.join(sd, "cookies")
    logs_path = os.path.join(sd, "logs")
    if (
        cef_browser_cls._caches_path and
        os.path.isdir(os.path.dirname(cef_browser_cls._caches_path))
    ):
        caches_path = cef_browser_cls._caches_path
    if (
        cef_browser_cls._cookies_path and
        os.path.isdir(os.path.dirname(cef_browser_cls._cookies_path))
    ):
        cookies_path = cef_browser_cls._cookies_path
    if (
        cef_browser_cls._logs_path and
        os.path.isdir(os.path.dirname(cef_browser_cls._logs_path))
    ):
        logs_path = cef_browser_cls._logs_path
    Logger.debug("CEFLoader: Caches path: %s", caches_path)
    Logger.debug("CEFLoader: Cookies path: %s", cookies_path)
    Logger.debug("CEFLoader: Logs path: %s", logs_path)
    if not os.path.isdir(caches_path):
        os.makedirs(caches_path, 0o0700)
    default_settings["cache_path"] = caches_path
    if not os.path.isdir(cookies_path):
        os.makedirs(cookies_path, 0o0700)
    if not os.path.isdir(logs_path):
        os.makedirs(logs_path, 0o0700)
    default_settings["log_file"] = os.path.join(logs_path, "cefpython.log")

    try:
        cefpython.Initialize(
            default_settings, cef_browser_cls._command_line_switches)
    except Exception as err:
        del default_settings["debug"]
        cefpython.g_debug = True
        cefpython.g_debugFile = "debug.log"
        try:
            cefpython.Initialize(
                default_settings, cef_browser_cls._command_line_switches)
        except Exception as err:
            raise Exception(
                "CEFLoader: Failed to initialize cefpython %s" % (err, ))

    try:
        cookie_manager = cefpython.CookieManager.GetGlobalManager()
        cookie_manager.SetStoragePath(cookies_path, True)
        cef_browser_cls._cookie_manager = cookie_manager
    except Exception as e:
        Logger.warning("CEFLoader: Failed to set up cookie manager: %s" % e)

    def cefpython_shutdown(*largs):
        print("CEFPYTHON SHUTDOWN", largs, App.get_running_app())
        cefpython.Shutdown()
        App.get_running_app().stop()

    def cefpython_exit(*largs):
        cefpython_shutdown()
        sys.exit()

    atexit.register(cefpython_shutdown)
    signal.signal(signal.SIGINT, cefpython_exit)
