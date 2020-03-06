import pytest
import os
import sys 

import serpent.utilities

def fakeOS():
    name = "faux OS"

    actual = sys.platform

    assert actual != name

def test_unix():
    names = ["darwin", "linux", "linux2"]

    actual = sys.platform

    if actual in names: 
        for name in names:
            if name == actual:
                assert name == actual
    else
        for name in names:
            if name != actual:
                assert name != actual

            
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
