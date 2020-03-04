import pytest
import time
import tkinter as tk
from serpent.window_controller import WindowController


# Test locate_window on regular title
def test_locate_window_1():
    name = 'Locate One'
    window = tk.Tk()
    window.title(name)
    window.configure(width=100, height=100)
    window.update()
    
    window_controller = WindowController()

    window_id = window_controller.locate_window(name)

    window_controller.focus_window(window_id)

    window_name = window_controller.get_focused_window_name()

    time.sleep(1)

    window.destroy()

    assert window_name == name

# Test locate_window on title that is an empty string
def test_locate_window_2():
    name = ''
    window = tk.Tk()
    window.title(name)
    window.configure(width=100, height=100)
    window.update()

    window_controller = WindowController()

    window_id = window_controller.locate_window(name)

    window_controller.focus_window(window_id)

    window_name = window_controller.get_focused_window_name()

    time.sleep(1)

    window.destroy()

    assert window_name == name

# Test locate_window on title with special characters
def test_locate_window_3():
    name = '.hack//+&_!@#%^&*()'
    window = tk.Tk()
    window.title(name)
    window.configure(width=100, height=100)
    window.update()

    window_controller = WindowController()

    window_id = window_controller.locate_window(name)

    window_controller.focus_window(window_id)

    window_name = window_controller.get_focused_window_name()

    time.sleep(1)

    window.destroy()

    assert window_name == name

# Test locate_window on title with escaped characters
def test_locate_window_4():
    name = 'a \newli\ne ma\nia'
    window = tk.Tk()
    window.title(name)
    window.configure(width=100, height=100)
    window.update()

    window_controller = WindowController()

    window_id = window_controller.locate_window(name)

    window_controller.focus_window(window_id)

    window_name = window_controller.get_focused_window_name()

    time.sleep(1)

    window.destroy()

    assert window_name == name

# Test locate_window on title with an escaped character at the beginning
def test_locate_window_5():
    name = '\newline first'
    window = tk.Tk()
    window.title(name)
    window.configure(width=100, height=100)
    window.update()

    window_controller = WindowController()

    window_id = window_controller.locate_window(name)

    window_controller.focus_window(window_id)

    window_name = window_controller.get_focused_window_name()

    time.sleep(1)

    window.destroy()

    assert window_name == name

# Test move_window x_offset
def test_move_window_1():
    name = 'Move One'
    window = tk.Tk()
    window.title(name)
    window.configure(width=100, height=100)
    window.update()

    window_controller = WindowController()

    window_id = window_controller.locate_window(name)

    geometry_before = window_controller.get_window_geometry(window_id)
    
    time.sleep(1)

    window_controller.move_window(window_id,200,200)

    time.sleep(1)

    geometry_after = window_controller.get_window_geometry(window_id)

    window.destroy()

    assert geometry_after['x_offset'] == 200

# Test move_window y_offset
def test_move_window_2():
    name = 'Move Two'
    window = tk.Tk()
    window.title(name)
    window.configure(width=100, height=100)
    window.update()

    window_controller = WindowController()

    window_id = window_controller.locate_window(name)

    geometry_before = window_controller.get_window_geometry(window_id)
    
    time.sleep(1)

    window_controller.move_window(window_id,200,200)

    time.sleep(1)

    geometry_after = window_controller.get_window_geometry(window_id)

    window.destroy()

    assert geometry_after['y_offset'] == 200

# Test move_window moving to current location
def test_move_window_3():
    name = 'Move Three'
    window = tk.Tk()
    window.title(name)
    window.configure(width=100, height=100)
    window.update()

    window_controller = WindowController()

    window_id = window_controller.locate_window(name)

    geometry_before = window_controller.get_window_geometry(window_id)
    
    time.sleep(1)

    window_controller.move_window(window_id,geometry_before['x_offset'], geometry_before['y_offset'])

    time.sleep(1)

    geometry_after = window_controller.get_window_geometry(window_id)

    window.destroy()

    assert geometry_after['x_offset'] == geometry_before['x_offset'] and geometry_after['y_offset'] == geometry_before['y_offset']


# Test move_window moving to negative coordinate
def test_move_window_4():
    name = 'Move Four'

    window_controller = WindowController()

    window = tk.Tk()
    window.title(name)
    window.configure(width=100, height=100)
    window.update()

    window_id = window_controller.locate_window(name)

    window_controller.get_window_geometry(window_id)
    
    time.sleep(1)

    window_controller.move_window(window_id,-100, 200)

    time.sleep(1)

    geometry_after = window_controller.get_window_geometry(window_id)

    window.destroy()

    assert not geometry_after['x_offset'] == -100

# Test move_window moving to out-of-bounds coordinate
def test_move_window_5():
    name = 'Move Five'
    window = tk.Tk()
    window.title(name)
    window.configure(width=100, height=100)
    window.update()

    window_controller = WindowController()

    window_id = window_controller.locate_window(name)

    window_controller.get_window_geometry(window_id)
    
    time.sleep(1)

    window_controller.move_window(window_id,2000, 200)

    time.sleep(1)

    geometry_after = window_controller.get_window_geometry(window_id)

    window.destroy()

    assert not geometry_after['x_offset'] == 2000
