import pytest
import pygame
import time
from serpent.window_controller import WindowController

#mockWindow allows for the creation of a game window through the pygame library
def mockWindow(name, width, height):
    pygame.init()
    mock = pygame.display.set_mode((width,height),pygame.RESIZABLE)
    pygame.display.set_caption(name)
    return mock

#Create a game window named 'blorp' and check that we can get the expected
#   focused window name is 'blorp'. 
def test_get_focused_window_name_1():
    name = 'blorp'

    window_controller = WindowController()

    mockWindow(name, 100, 100)

    time.sleep(1)

    focused_name = window_controller.get_focused_window_name()

    assert focused_name == name

#Create a game window with an empty string for the name. Assert that the expected
#   focused window name is the blank string. 
def test_get_focused_window_name_2():
    name = ''

    window_controller = WindowController()

    mockWindow(name, 100, 100)

    time.sleep(1)

    focused_name = window_controller.get_focused_window_name()

    assert focused_name == name

#Create a game window with special characters in the name. Assert that the expected
#   focused window name is the same string. 
def test_get_focused_window_name_3():
    name = 'Special:Characters/in+me'

    window_controller = WindowController()

    mockWindow(name, 100, 100)

    time.sleep(1)

    focused_name = window_controller.get_focused_window_name()

    assert focused_name == name    

#Create a game window with escaped characters in the name. Assert that the expected
#   focused window name is the same string.
def test_get_focused_window_name_4():
    name = 'escape\"\n\\'

    window_controller = WindowController()

    mockWindow(name, 100, 100)

    time.sleep(1)

    focused_name = window_controller.get_focused_window_name()

    assert focused_name == name


#Create a game window with an incredibly long name. Assert that the expected
#   focused window name is the same string.
def test_get_focused_window_name_5():
    name = 'Lorem ipsum.'

    name = name*1000000

    window_controller = WindowController()

    mockWindow(name, 100, 100)

    time.sleep(1)

    focused_name = window_controller.get_focused_window_name()

    assert focused_name == name

#Create a game window 100 x 100 pixels. Resize the window to 500 x 500 pixels.
#   Assert that the window is now 500 x 500. 
def test_resize_window_1():
    name = 'Resize_1'

    window_controller = WindowController()

    mockWindow(name, 100, 100)

    mock_id = window_controller.locate_window(name)

    window_controller.resize_window(mock_id,500,500)

    geometry = window_controller.get_window_geometry(mock_id)

    assert geometry['width'] == 500 and geometry['height'] == 500

#Create a game window 100 x 100 pixels. Attempt to resize the window to 0 x 0 pixels.
#   Assert that the window will not resize to 0 x 0 pixels. 
def test_resize_window_2():
    name = 'Resize_2'

    window_controller = WindowController()

    mockWindow(name, 100, 100)

    mock_id = window_controller.locate_window(name)

    window_controller.resize_window(mock_id,0,0)

    geometry = window_controller.get_window_geometry(mock_id)

    assert not geometry['width'] == 0 and not geometry['height'] == 0    

#Create a game window 100 x 100 pixels. Attempt to resize the window to -500 x 500 pixels.
#   Assert that the window width will not resize to negative pixals. 
def test_resize_window_3():
    name = 'Resize_3'

    window_controller = WindowController()

    mockWindow(name, 100, 100)

    mock_id = window_controller.locate_window(name)

    window_controller.resize_window(mock_id,-500,500)

    geometry = window_controller.get_window_geometry(mock_id)

    assert not geometry['width'] == -500 and geometry['height'] == 500

#Create a game window 100 x 100 pixels. Attempt to resize the window to 500 x -500 pixels.
#   Assert that the window height will not resize to negative pixals.
def test_resize_window_4():
    name = 'Resize_4'

    window_controller = WindowController()

    mockWindow(name, 100, 100)

    mock_id = window_controller.locate_window(name)

    window_controller.resize_window(mock_id,500,-500)

    geometry = window_controller.get_window_geometry(mock_id)

    assert geometry['width'] == 500 and not geometry['height'] == -500

#Create a game window 100 x 100 pixels. Attempt to resize the window to 1600 x 500 pixels.
#   Assert that the window is resized to 1600 x 500. 
def test_resize_window_5():
    name = 'Resize_5'

    window_controller = WindowController()

    mockWindow(name, 100, 100)

    mock_id = window_controller.locate_window(name)

    window_controller.resize_window(mock_id,1600,500)

    geometry = window_controller.get_window_geometry(mock_id)

    assert geometry['width'] == 1600 and geometry['height'] == 500

#Create a game window 100 x 100 pixels. Attempt to resize the window to 2000 x 500 pixels.
#   Assert that the window will not resize past the resolution width. 
def test_resize_window_6():
    name = 'Resize_5'

    window_controller = WindowController()

    mockWindow(name, 100, 100)

    mock_id = window_controller.locate_window(name)

    window_controller.resize_window(mock_id,2000,500)

    geometry = window_controller.get_window_geometry(mock_id)

    assert not geometry['width'] == 2000 and geometry['height'] == 500
