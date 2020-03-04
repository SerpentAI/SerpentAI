import pytest
import os
import sys

from serpent.utilities import clear_terminal, display_serpent_logo, is_linux, is_macos, is_windows, is_unix
from serpent.serpent import setup_gui, setup_ml

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
		

	
	
	
