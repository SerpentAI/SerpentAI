import pytest
import os
import sys 
import unittest 

import serpent.utilities

def fakeOS():
    name = "faux OS"

    actual = sys.platform

    assert actual != name

def test_unix():
    names = ["darwin", "linux", "linux2"]

    actual = sys.platform

    assertIn(actual, names)
            
def test_linux():
	name = "linux"
	
	actual = sys.platform
	
	assert actual != name #current OS is windows
 	
def test_windows():
	name = "win32"
	
	actual = sys.platform
	
	assert actual == name
	
def test_macos():
	name = "darwin"
	
	actual = sys.platform
	
	assert actual != name #current OS is windows
