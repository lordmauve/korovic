import math
import random
import pyglet
import pyglet.graphics
import pyglet.sprite
from pyglet.gl import gl


from . import loader
from .camera import Rect
from .vector import v
from .primitives import walk


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
        c2 = self.gradient.colour(alt + 10000)

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


class SpatialSparseHash(object):
    """A spatial hash in which the contents of the cells is computed procedurally."""
    def __init__(self, cell_size=100):
        self.cell_size = cell_size
        self._cs = v(self.cell_size, self.cell_size)

    def _cells(self, viewport):
        def mod(x, y):
            r = math.fmod(x, y)
            if r < 0:
                return r + y
            return r

        cs = self.cell_size
        l = viewport.left - mod(viewport.left, cs)
        r = viewport.right

        b = viewport.bottom - mod(viewport.bottom, cs)
        t = viewport.top

        cx = l
        while cx < r:
            cy = b
            while cy < t:
                yield v(cx, cy)
                cy += cs
            cx += cs

    def _cell_rects(self, viewport):
        for bl in self._cells(viewport):
            yield Rect(bl, bl + self._cs)

    def _get(self, rect, random):
        """Subclasses should implement this method."""
        return []

    def get(self, coord):
        """Get the contents of the cell given by coord.

        NB. this is not the CELL *at* coord, coord must correspond to an extant
        cell!

        """
        return self._get(*self._params_for_coord(coord))

    def _params_for_coord(self, c):
        rand = random.Random()
        rand.seed(hash(c))
        return (Rect(c, c + self._cs), rand) 

    def for_viewport(self, viewport):
        res = []
        for c in self._cells(viewport):
            res.extend(self.get(c))
        return res


class Clouds(SpatialSparseHash):
    """Generate random clouds in a sparse but persistent way."""
    @classmethod
    def load(cls):
        cls.images = [
            loader.image('data/sprites/cloud1.png'),
            loader.image('data/sprites/cloud2.png'),
            loader.image('data/sprites/cloud3.png'),
        ]

    def __init__(self, cell_size=500):
        super(Clouds, self).__init__(cell_size)
        self.batch = pyglet.graphics.Batch()
        self.current = {}  # current cells

    def _get(self, rect, random):
        if rect.bottom < 400 or rect.top > 50000:
            return []
        if random.uniform(0, rect.bottom * 0.0001) < 0.5:
            img = random.choice(self.images)
            x = random.uniform(rect.left, rect.right)
            y = random.uniform(rect.bottom, rect.top)
            c = pyglet.sprite.Sprite(img, x=x, y=y, batch=self.batch)
            return [c]
        return []

    def set_viewport(self, vp):
        vp = vp.extend(256)
        cs = set(self._cells(vp))
        keys = set(self.current.keys())

        # Compute new
        for coord in (cs - keys):
            self.current[coord] = self.get(coord)

        # Delete existing
        for coord in (keys - cs):
            del(self.current[coord])

    def draw(self):
        self.batch.draw()


class Stars(Clouds):
    """Generate random clouds in a sparse but persistent way."""
    @classmethod
    def load(cls):
        cls.image = loader.image('data/sprites/star.png')

    def _get(self, rect, random):
        cs = []
        if rect.bottom > 20000:
            for i in range(int(random.uniform(0, (rect.bottom - 20000) * 0.0001))):
                x = random.uniform(rect.left, rect.right)
                y = random.uniform(rect.bottom, rect.top)
                c = pyglet.sprite.Sprite(self.image, x=x, y=y, batch=self.batch)
                c.rotation = random.randint(0, 60)
                cs.append(c)
        return cs
