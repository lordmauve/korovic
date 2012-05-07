from pyglet.gl import gl


# This was extracted from source/sky.svg using tools/svg_to_gradient.py
SKY = [
    (0.0, (0.0, 0.0, 0.0)),
    (0.40000001, (0.0, 0.5333333333333333, 0.6666666666666666)),
    (1.0, (0.6862745098039216, 0.9137254901960784, 0.8980392156862745))
]

SKY_TOP = 10000


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



class GradientPainter(object):
    def draw(self, alt, viewport):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        #TODO - call gradient to implement this

