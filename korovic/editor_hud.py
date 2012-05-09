from collections import namedtuple

from pyglet.gl import gl

from .vector import v
from . import components
from .camera import Rect
from .primitives import Rectangle, Label
from .constants import SCREEN_SIZE

from .components import IncompatibleComponent


Item = namedtuple('Item', 'name price component')
Button = namedtuple('Button', 'rect callback')

SHOP = [
    Item('Jet Engine', 750, components.JetEngine),
    Item('Rocket', 350, components.Rocket),
    Item('Wing', 200, components.Wing),
    Item('Biplane', 150, components.BiplaneWing),
    Item('Propeller', 100, components.Propeller),
    Item('Small Fuel Tank', 60, components.SmallFuelTank),
    Item('Large Fuel Tank', 100, components.LargeFuelTank),
]

GREY = (90, 90, 90, 255)
WHITE = (255, 255, 255, 255)

class ListItem(object):
    def __init__(self, hud, item):
        self.rect = Rect(v(0, 0), hud.tile_size)
        self.r = Rectangle(self.rect, [(0, 0, 0, 0.33)])
        self.hud = hud
        self.item = item

        self.label = Label(
            text=item.name,
            pos=(85, 46),
            font_size=12,
        )
        self.pricelabel = Label(
            text='$%d' % item.price,
            pos=(85, 16),
            font_size=10
        )
        
        self.buy = Label(
            text='Buy',
            anchor_x='center',
            pos=(230, 19),
            font_size=12
        )

        self.sell = Label(
            text='Sell',
            anchor_x='center',
            pos=(300, 19),
            font_size=12
        )

    def draw(self):
        self.r.draw()
        self.label.draw()
        self.pricelabel.draw()
        if not self.can_buy():
            self.buy.color = GREY
        else:
            self.buy.color = WHITE
        self.buy.draw()

        if not self.can_sell():
            self.sell.color = GREY
        else:
            self.sell.color = WHITE
        self.sell.draw()

    def can_buy(self):
        if self.hud.money < self.item.price:
            return False
        try:
            self.hud.slots.find_slot(self.item.component)
        except IncompatibleComponent:
            return False
        return True

    def can_sell(self):
        return self.hud.slots.has(self.item.component)

    def on_buy(self):
        print "Buy", self.item.name
        self.hud.squid.attach(self.item.component)
        self.hud.money -= self.item.price

    def on_sell(self):
        print "Sell", self.item.name
        self.hud.slots.remove_any(self.item.component)
        self.hud.money += self.item.price

    def buttons(self):
        bs = []
        if self.can_buy():
            bs.append(Button(Rect(v(195, 0), v(195 + 65, 80)), self.on_buy))
        if self.can_sell():
            bs.append(Button(Rect(v(268, 0), v(268 + 65, 80)), self.on_sell))
        return bs


class EditorHud(object):
    @classmethod
    def load(cls):
        pass

    def __init__(self, squid, money):
        self.squid = squid
        self.slots = squid.slots
        self.money = money

        self.moneylabel = Label((20, 565))
        self.weightlabel = Label((20, 530))
        self.fuellabel = Label((20, 495))

        self.tile_size = v(340, 80)
        self.build()

    def build(self):
        items = []
        for item in SHOP:
            items.append(ListItem(self, item))
        self.items = items

    def buttons(self):
        tr = v(SCREEN_SIZE)
        pos = tr - self.tile_size - v(10, 10)
        buttons = []
        for item in self.items:
            for b in item.buttons():
                buttons.append(Button(
                    b.rect.translate(pos),
                    b.callback
                ))
            pos -= v(0, self.tile_size.y + 10)
        return buttons

    def draw(self):
        self.moneylabel.document.text = 'Money: $%d' % self.money
        self.weightlabel.document.text = 'Weight: %dkg' % self.squid.total_weight()
        cap = self.squid.fuel_capacity()

        if cap:
            self.fuellabel.document.text = 'Fuel Capacity: %dkg' % cap
        else:
            self.fuellabel.document.text = 'Fuel Capacity: -'
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
        self.fuellabel.draw()
