import pytest
import os
import sys

from serpent import utilities

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
		assert actual == name
		
def test_actual_os():
    yourOS = sys.platform


	
	
	
