import pytest
import os
import sys 

import serpent.utilities

def test_notlinux():
    nameNotLinux = ["win32", "darwin"]
    
    actual = sys.platform

    for name in nameNotLinux:
        assert actual != name

def test_notWindows():
    nameNotWindows = ["linux", "darwin", "linux2"]
    
    actual = sys.platform

    for name in nameNotWindows:
        assert actual != name

def test_notMacOS():
    nameNotLinux = ["win32", "linux", "linux2"]
    
    actual = sys.platform

    for name in nameNotMacOS:
        assert actual != name

def test_linux():
	name = "linux"
	
	actual = sys.platform
	
	assert actual == name
	
def test_windows():
	name = "win32"
	
	actual = sys.platform
	
	assert actual == name
	
def test_macos():
	name = "darwin"
	
	actual = sys.platform
	
	assert actual == name
	
def test_unix():

	nameUnix = ["linux", "linux2", "darwin"]
	
	actual = sys.platform
	
	for name in nameUnix:
		assert actual != name