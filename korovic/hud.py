from pyglet import gl

from .constants import SEA_LEVEL, SCREEN_SIZE
from .primitives import Label, Rectangle
from .camera import Rect
from .vector import v


class GameHud(object):
    def __init__(self, world):
        self.world = world

        w, h = SCREEN_SIZE
        r = Rect(v(0, 0), v(250, 113))
        r = r.translate(v(8, h - r.height - 8))
        self.infobox = Rectangle(r, [(0, 0, 0, 0.33)])

        self.altlabel = Label(
            text='Altitude:',
            x=20,
            y=h - 35
        )
        self.distlabel = Label(
            text='Distance:',
            x=20,
            y=h - 70
        )
        self.fuellabel = Label(
            text='',
            x=20,
            y=h - 105
        )

        self.controllers = []

    def set_controllers(self, controllers):
        self.controllers = controllers

    def draw(self):
        alt = (self.world.squid.position.y - SEA_LEVEL - 15) * 0.1
        dist = (self.world.squid.position.x - 150) * 0.1

        if alt < 0:
            self.altlabel.document.text = 'Depth: %dm' % (-alt)
        else:
            self.altlabel.document.text = 'Altitude: %dm' % alt
        self.distlabel.document.text = 'Distance: %dm' % dist
        self.fuellabel.document.text = 'Fuel: %0.1fkg' % self.world.squid.fuel
        self.infobox.draw()
        self.altlabel.draw()
        self.distlabel.draw()
        self.fuellabel.draw()

        if self.controllers:
            gl.glPushMatrix(gl.GL_MODELVIEW)
            gl.glTranslatef(SCREEN_SIZE[0] - 74, 10, 0)
            for controller in reversed(self.controllers):
                controller.draw()
                gl.glTranslatef(-74, 0, 0)
            gl.glPopMatrix(gl.GL_MODELVIEW)
