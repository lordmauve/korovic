import pyglet
from pyglet.gl import gl

from .vector import v


# This was extracted from source/sky.svg using tools/svg_to_gradient.py
SKY = [
    (0.0, (0.686, 0.914, 0.898)),
    (0.6, (0.0, 0.533, 0.667)),
    (1.0, (0.0, 0.0, 0.0)),
]

SKY_TOP = 50000


def lerp(frac, a, b):
    """Linear interpolation"""
    ifrac = (1 - frac)
    return tuple(ifrac * ca + frac * cb for ca, cb in zip(a, b))
    


class Gradient(object):
    def __init__(self, gradient, scale):
        self.gradient = [
            (float(alt * scale), colour) for (alt, colour) in gradient
        ]

    def colour(self, pos):
        """Get the colour at position `pos` in the gradient."""
        lastv, lastc = None, None
        for v, c in self.gradient:
            if v >= pos:
                if lastc is None:
                    return c
                else:
                    frac = (pos - lastv) / (v - lastv)
                    return lerp(frac, lastc, c)
            else:
                lastv = v
                lastc = c
        else:
            return lastc


sky = Gradient(SKY, SKY_TOP)

def walk(list):
    for i in list:
        for j in i:
            yield j


class GradientPainter(object):
    def __init__(self, gradient):
        self.gradient = gradient

    def draw(self, viewport):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        alt = viewport.bl.y
        h = viewport.height 
        w = viewport.width
        c1 = self.gradient.colour(alt)
        c2 = self.gradient.colour(alt + h)

        o = v(0, 0)
        x = v(w, 0)
        y = v(0, h)

        vs = [o, x, x + y, y]
        cs = [c1, c1, c2, c2]
        
        pyglet.graphics.draw(4, gl.GL_QUADS,
            ('v2f', list(walk(vs))),
            ('c3f', list(walk(cs)))
        )


class HorizonPainter(object):
    def __init__(self, height, colour):
        self.height = height
        self.colour = colour

    def draw(self, viewport):
        alt = viewport.bl.y

        if alt > self.height:
            return
        h = max(0, min(self.height - alt, viewport.height))
        w = viewport.width
        
        o = v(0, 0)
        x = v(w, 0)
        y = v(0, h)

        return self.draw_quad([o, x, x + y, y])

    def draw_quad(self, vs):
        """Draw a quad defined by vs"""
        gl.glColor3f(*self.colour)
        pyglet.graphics.draw(4, gl.GL_QUADS,
            ('v2f', list(walk(vs))),
        )


class ForegroundSeaPainter(HorizonPainter):
    def __init__(self, height, colour, x):
        super(ForegroundSeaPainter, self).__init__(height, colour)
        self.x = x

    def draw(self, viewport):
        alt = viewport.bl.y

        if alt > self.height:
            return
        h = max(0, min(self.height - alt, viewport.height))
        w = viewport.width
        x = viewport.bl.x
        startx = max(0, self.x - x)

        o = v(startx, 0)
        x = v(w, 0)
        y = v(startx, h)

        return self.draw_quad([o, x, x + y, y])
