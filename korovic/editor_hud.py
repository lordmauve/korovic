from collections import namedtuple

from pyglet.gl import gl

from .vector import v
from . import components
from .camera import Rect
from .primitives import Rectangle, Label
from .constants import SCREEN_SIZE
from .primitives import Button as ButtonWidget

from .components import IncompatibleComponent
from .sound import load_sound


Item = namedtuple('Item', 'name price component tooltip')
Button = namedtuple('Button', 'rect callback tooltip')

SHOP = [
    Item('Jet Engine', 750, components.JetEngine, 'Lots of thrust, but heavy!'),
    Item('Rocket', 350, components.Rocket, 'Once rockets are up, who cares vhere zey come down?'),
    Item('Wing', 200, components.Wing, 'An aerofoil gives lift as it moves through ze air!'),
    Item('Biplane', 150, components.BiplaneWing, 'Ah! Ze old days!'),
    Item('Aerolon', 150, components.Aerolon, 'Control and stability, Susie!'),
    Item('Propeller', 100, components.Propeller, 'Contact!'),
    Item('Small Fuel Tank', 40, components.SmallFuelTank, 'A little fuel goes a long way!'),
    Item('Large Fuel Tank', 75, components.LargeFuelTank, 'Is zis too much fuel for you?'),
    Item('Balloon', 35, components.Balloon, 'Ninety-nine Luftballoons...'),
    Item('Pulsejet', 150, components.PulseJet, 'Vould you like to cruise like a V-1, Susie?'),
    Item('Rotor', 500, components.Rotor, 'You are Susie, not Huey, yes?'),
    Item('Hang Glider', 100, components.HangGlider, 'And it vill keep ze sun off you!'),
    Item('Ekranoplan', 400, components.Ekranoplan, 'I stole zese from ze Russians.'),
    Item('Hot Air Balloon', 275, components.HotAirBalloon, 'Up, up and avay!'),
]

GREY = (90, 90, 90, 255)
WHITE = (255, 255, 255, 255)


buy_sound = load_sound('data/sounds/buy.wav')
sell_sound = load_sound('data/sounds/beep.wav')


class ListItem(object):
    def __init__(self, hud, item):
        self.rect = Rect(v(0, 0), hud.tile_size)
        self.r = Rectangle(self.rect, [(0, 0, 0, 0.33)])
        self.hud = hud
        self.item = item
        self.icon = item.component.get_icon()
        p = int(hud.tile_size.y * 0.5 + 0.5)
        self.icon.position = (p, p)

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
        self.icon.draw()

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
        buy_sound.play()
        self.hud.squid.attach(self.item.component)
        self.hud.money -= self.item.price

    def on_sell(self):
        sell_sound.play()
        self.hud.slots.remove_any(self.item.component)
        self.hud.money += self.item.price

    def buttons(self):
        bs = []
        if self.can_buy():
            bs.append(Button(Rect(v(195, 0), v(195 + 65, 80)), self.on_buy, self.item.tooltip))
        if self.can_sell():
            bs.append(Button(Rect(v(268, 0), v(268 + 65, 80)), self.on_sell, None))
        return bs


class EditorHud(object):
    @classmethod
    def load(cls):
        pass

    def __init__(self, squid, max_money):
        self.squid = squid
        self.slots = squid.slots

        self.moneylabel = Label((20, 565))
        self.weightlabel = Label((20, 530))
        self.fuellabel = Label((20, 495))
        self.startbutton = ButtonWidget((8, 8), 'Fly >>>')

        self.tile_size = v(340, 80)
        self.height = 0
        self.scroll = 0
        self.build(max_money)

    def money(self):
        return self.squid.money

    def set_money(self, m):
        self.squid.money = m

    money = property(money, set_money)

    def scroll_rows(self, dy):
        self.scroll_by(dy * 20)

    def scroll_by(self, dy):
        max_scroll = max(0, self.height - SCREEN_SIZE[1])
        self.scroll = max(0, min(self.scroll - dy, max_scroll))

    def build(self, max_money):
        items = []
        for item in SHOP:
            if item.price > max_money:
                continue
            items.append(ListItem(self, item))
        items.sort(key=lambda x: x.item.price)
        self.items = items
        self.height = (self.tile_size.y + 10) * len(self.items) + 10

    def buttons(self):
        tr = v(SCREEN_SIZE)
        pos = tr - self.tile_size - v(10, 10) + v(0, self.scroll)
        buttons = []
        for item in self.items:
            for b in item.buttons():
                buttons.append(Button(
                    b.rect.translate(pos),
                    b.callback,
                    b.tooltip
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
        gl.glPushMatrix()
        gl.glTranslatef(pos.x, pos.y + self.scroll, 0)
        for item in self.items:
            item.draw()
            gl.glTranslatef(0, -self.tile_size.y - 10, 0)
        gl.glPopMatrix()
        self.moneylabel.draw()
        self.weightlabel.draw()
        self.fuellabel.draw()
        self.startbutton.draw()
