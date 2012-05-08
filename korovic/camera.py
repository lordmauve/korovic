from contextlib import contextmanager
from pyglet.gl import gl

from .constants import SCREEN_SIZE
from .vector import v


class Rect(object):
    __slots__ = 'bl', 'tr'

    def __init__(self, bl, tr):
        self.bl = v(bl)
        self.tr = v(tr)

    def __repr__(self):
        return 'Rect(%r, %r)' % (tuple(self.bl), tuple(self.tr))

    @property
    def height(self):
        return (self.tr - self.bl).y

    @property
    def left(self):
        return self.bl.x

    @property
    def right(self):
        return self.tr.x

    @property
    def bottom(self):
        return self.bl.y

    @property
    def top(self):
        return self.tr.y

    @property
    def width(self):
        return (self.tr - self.bl).x

    def __hash__(self):
        return hash((self.tr, self.bl))

    def __eq__(self, ano):
        return (
            self.bl == ano.bl and 
            self.tr == ano.tr
        )

    def extend(self, dist):
        """Compute a new rect bigger than this by dist in each direction."""
        o = v(dist, dist)
        return Rect(self.bl - o, self.tr + o)
        

class Camera(object):
    def __init__(self):
        self.ss = v(*SCREEN_SIZE) * 0.5
        self.pos = self.ss
    
    def pan_to(self, point):
        x, y = self.pos + (point - self.pos) * 0.1
        x = max(self.ss.x, x)
        y = max(self.ss.y, y)
        self.pos = v(x, y)

    def set_pos(self, pos):
        x, y = pos
        x = max(self.ss.x, x)
        y = max(self.ss.y, y)
        self.pos = v(x, y)

    def track(self, actor):
        self.set_pos(actor.body.position)

    def viewport(self):
        ss = v(*SCREEN_SIZE) * 0.5
        return Rect(self.pos - ss, self.pos + ss)

    @contextmanager
    def modelview(self):
        gl.glPushMatrix(gl.GL_MODELVIEW)
        try:
            gl.glMatrixMode(gl.GL_MODELVIEW)
            x, y = self.pos - self.ss
            gl.glTranslatef(-x, -y, 0)
            yield
        finally:
            gl.glPopMatrix(gl.GL_MODELVIEW)
