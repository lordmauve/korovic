from collections import namedtuple

from pyglet.gl import gl

from .vector import v
from . import components
from .camera import Rect
from .primitives import Rectangle, Label
from .constants import SCREEN_SIZE


Item = namedtuple('Item', 'name price component')

SHOP = [
    Item('Jet Engine', 750, components.JetEngine),
]


class ListItem(object):
    def __init__(self, hud, item):
        self.r = Rectangle(Rect(v(0, 0), hud.tile_size), [(0, 0, 0, 0.33)])

        self.label = Label(
            text=item.name,
            pos=(85, 46),
            font_size=14,
        )
        self.pricelabel = Label(
            text='$%d' % item.price,
            pos=(85, 16),
            font_size=12
        )

    def draw(self):
        self.r.draw()
        self.label.draw()
        self.pricelabel.draw()


class EditorHud(object):
    @classmethod
    def load(cls):
        pass

    def __init__(self, squid, money):
        self.squid = squid
        self.money = money

        self.moneylabel = Label((20, 565))
        self.weightlabel = Label((20, 530))

        self.tile_size = v(340, 80)
        self.build()

    def build(self):
        items = []
        for item in SHOP:
            items.append(ListItem(self, item))
        self.items = items

    def draw(self):
        self.moneylabel.document.text = 'Money: $%d' % self.money
        self.weightlabel.document.text = 'Weight: %dkg' % self.squid.total_weight()
        tr = v(SCREEN_SIZE)
        pos = tr - self.tile_size - v(10, 10)
        gl.glPushMatrix(gl.GL_MODELVIEW)
        gl.glTranslatef(pos.x, pos.y, 0)
        for item in self.items:
            item.draw()
            gl.glTranslatef(0, -self.tile_size.y - 10, 0)
        gl.glPopMatrix(gl.GL_MODELVIEW)
        self.moneylabel.draw()
        self.weightlabel.draw()
