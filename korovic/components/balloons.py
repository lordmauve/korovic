import math
import pyglet.sprite

from .base import Component, ActivateableComponent
from .engines import OnAnimation, ActiveSound
from .squid import Tether, Slot

from ..controllers import PressController
from ..vector import v
from ..sound import load_sound


class Balloon(Component):
    LIFT = v(0, 20000)
    MASS = 3
    ALT_ATTENUATION = 0.00001  # how fast lift drops off with altitude
    slot_mask = Slot.TOP | Slot.NOSE | Slot.TAIL

    def __init__(self, squid, attachment_point):
        super(Balloon, self).__init__(squid, attachment_point)
        self.reset()

    def reset(self):
        self.tether = None
        self.create_body()
        self.tether_to(self.squid.body) 
        super(Balloon, self).reset()

    def bodies_and_shapes(self):
        bs = super(Balloon, self).bodies_and_shapes()
        if self.tether:
            bs.extend(self.tether.bodies_and_shapes())
        return bs

    def attach_at_slot(self, slot):
        super(Balloon, self).attach_at_slot(slot)
        self.reset()

    def home_position(self):
        return Component.get_position(self) + v(0, 100)

    def tether_to(self, body):
        self.body.position = self.home_position()
        self.tether = Tether(
            a=self.body.local_to_world(-self.insertion_point),
            b=v(body.position + self.attachment_point),
            c1=self.body,
            c2=body,
            density=0.1,
            segments=2
        )

    def update(self, dt):
        self.body.reset_forces()
        alt = self.body.position.y
        if alt < 0:
            frac = 1.0
        else:
            # lift drops off with altitude
            frac = 1.0 / (1 + alt * 0.0001)
        self.body.apply_force(frac * self.LIFT)

    def get_position(self):
        return v(self.body.position)

    def set_position(self, pos):
        self.body.position = v(pos)
        a = self.body.local_to_world(-self.insertion_point)
        b = Component.get_position(self)
        self.tether.reorient(a, b)
        self.body.angle = 0

    position = property(get_position, set_position)

    @property
    def rotation(self):
        return self.body.angle

    def draw_component(self):
        if self.tether:
            self.tether.draw()
        super(Balloon, self).draw_component()


class HotAirBalloon(ActiveSound, Balloon, OnAnimation, ActivateableComponent):
    slot_mask = Slot.TOP
    FUEL_CONSUMPTION = 0.1
    MASS = 7
    
    temp = 0
    MIN_LIFT = v(0, 10000)
    MAX_LIFT = v(0, 80000)
    started = False

    sound = load_sound('data/sounds/hotairballoon.wav')

    def update(self, dt):
        ran = False
        if self.active:
            if self.squid.draw_fuel(self.FUEL_CONSUMPTION * dt):
                if not self.started:
                    self.on_start()
                    self.started = True
                ran = True
                self.temp = min(1, self.temp + dt * 0.05)
        else:
            self.temp = self.temp * 0.9 ** dt 
        if not ran and self.started:
            self.on_stop()
            self.started = False

        # Not actually apply the lift
        self.LIFT = (
            self.temp * self.MAX_LIFT +
            (1 - self.temp) * self.MIN_LIFT
        )
        super(HotAirBalloon, self).update(dt)

    def is_enabled(self):
        return self.squid.has_fuel()

    def controller(self):
        return PressController(self)
