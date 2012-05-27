import math

from ..vector import v
from ..editor import AngleEditor
from ..controllers import PressController
from ..constants import SEA_LEVEL

from .base import Component, ActivateableComponent
from .squid import Slot


class Wing(Component):
    MASS = 15
    slot_mask = Slot.SIDE

    MAX_LIFT = 100000
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
    MAX_LIFT = 120000

    #FIXME: give biplane wing different properties
    LIFT_RATE = 10
    DRAG = 0.2


class HangGlider(Wing):
    MASS = 4
    MAX_LIFT = 60000
    slot_mask = Slot.TOP

    LIFT_RATE = 7
    DRAG = 0.3


class Aerolon(Wing, ActivateableComponent):
    MASS = 2
    LIFT_RATE = 1
    DRAG = 0.05
    
    MAX_LIFT = 20000

    def update(self, dt):
        super(Aerolon, self).update(dt)
        if self.active:
            wind = self.relative_wind()
            x2 = wind.x * wind.x
            force = math.sin(-0.5 * math.radians(self.rotation % 180))
            lift = max(self.MAX_LIFT, force * self.LIFT_RATE * x2)
            self.apply_force_relative(v(0, lift)) 

    def controller(self):
        return PressController(self)


class Ekranoplan(Component):
    MASS = 15
    MAX_LIFT = 200000
    LIFT_RATE = 7
    DRAG = 0.1
    TORQUE_SCALE = 8

    slot_mask = Slot.BOTTOM

    def update(self, dt):
        # Drag
        self.apply_force_absolute(self.absolute_wind() * -self.DRAG)

        # Lift
        wind = self.relative_wind()
        aoa = -(-wind).angle
        if wind.length2 > 1 and -45 < aoa < 45:
            coeff = self.LIFT_RATE * math.sin(2 * math.radians(aoa + 5))
            lift = v(0, max(-self.MAX_LIFT, min(self.MAX_LIFT, coeff * wind.length2)))
            alt = self.position.y - SEA_LEVEL
            scale = max(0, 1 - (alt / 100.0) ** 2)
            if alt > 0:
                self.apply_force(lift * scale)
                self.apply_torque(-self.rotation * scale * self.TORQUE_SCALE)
