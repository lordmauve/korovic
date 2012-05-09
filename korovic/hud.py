from pyglet.text import Label

from .constants import SEA_LEVEL


class GameHud(object):
    def __init__(self, world):
        self.world = world

        self.altlabel = Label(
            text='Altitude:',
            font_name='Atomic Clock Radio',
            font_size=16,
            x=10,
            y=565
        )
        self.distlabel = Label(
            text='Distance:',
            font_name='Atomic Clock Radio',
            font_size=16,
            x=10,
            y=530
        )
        self.fuellabel = Label(
            text='',
            font_name='Atomic Clock Radio',
            font_size=16,
            x=10,
            y=495
        )

    def draw(self):
        alt = (self.world.squid.position.y - SEA_LEVEL - 15) * 0.1
        dist = (self.world.squid.position.x - 150) * 0.1

        if alt < 0:
            self.altlabel.document.text = 'Depth: %dm' % (-alt)
        else:
            self.altlabel.document.text = 'Altitude: %dm' % alt
        self.distlabel.document.text = 'Distance: %dm' % dist
        self.fuellabel.document.text = 'Fuel: %dkg' % self.world.squid.fuel
        self.altlabel.draw()
        self.distlabel.draw()
        self.fuellabel.draw()
