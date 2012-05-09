import math

from ..vector import v
from ..editor import AngleEditor

from .base import Component
from .squid import Slot


class Wing(Component):
    MASS = 15
    slot_mask = Slot.SIDE

    MAX_LIFT = 150000
    LIFT_RATE = 5  # a number representing the relative wing area etc
    DRAG = 0.1

    def draw_component(self):
        self.sprite.set_position(*self.position)
        self.sprite.rotation = -180 / math.pi * (self.angle + self.squid.body.angle)
        self.sprite.draw()

    def update(self, dt):
        # Drag
        #self.apply_force_absolute(self.absolute_wind() * -self.DRAG)

        # Lift
        wind = self.relative_wind()
        aoa = -(-wind).angle
        if wind.length2 > 1 and -45 < aoa < 45:
            coeff = self.LIFT_RATE * math.sin(2 * math.radians(aoa + 5))
            lift = v(0, max(-self.MAX_LIFT, min(self.MAX_LIFT, coeff * wind.length2)))
            self.apply_force(lift)

    def controller(self):
        return None

    def editor(self):
        return AngleEditor(self, max_angle=20)


class BiplaneWing(Wing):
    MASS = 10

    #FIXME: give biplane wing different properties
    LIFT_RATE = 10
    DRAG = 0.2
