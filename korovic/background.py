import pyglet
from pyglet.gl import gl
from vector import v


# This was extracted from source/sky.svg using tools/svg_to_gradient.py
SKY = [
    (0.0, (0.0, 0.0, 0.0)),
    (0.40000001, (0.0, 0.5333333333333333, 0.6666666666666666)),
    (1.0, (0.6862745098039216, 0.9137254901960784, 0.8980392156862745))
]

SKY_TOP = 10000

class Gradient(object):
    def __init__(self, gradient, scale):
        self.gradient = [(alt * scale, colour) for (alt, colour) in gradient]

    def colour(self, frac):
        col = self.gradient[0][0]
        # TODO
        return col


class GradientPainter(object):
    def draw(self, alt, viewport):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        #TODO - call gradient to implement this

