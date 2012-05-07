"""Save a screenshot.

Taken from http://themonkeyproject.wordpress.com/2011/05/04/screenshot-code/
"""

import datetime
import pyglet.image
from pyglet import gl


def screenshot_path():
    return datetime.datetime.now().strftime('screenshot_%Y-%m-%d_%H:%M:%S.%f.png')


def take_screenshot(window):
    """This is your registered on_key_press handler.

    window is the pyglet.window.Window object to grab.
    """
    gl.glPixelTransferf(gl.GL_ALPHA_BIAS, 1.0)  # don't transfer alpha channel
    image = pyglet.image.ColorBufferImage(0, 0, window.width, window.height)
    image.save(screenshot_path())
    gl.glPixelTransferf(gl.GL_ALPHA_BIAS, 0.0)  # restore alpha channel transfer
