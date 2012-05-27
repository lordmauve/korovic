import math
import pyglet.sprite

from .base import Component
from .squid import Tether, Slot

from ..vector import v


class Balloon(Component):
    LIFT = v(0, 20000)
    MASS = 3
    ALT_ATTENUATION = 0.00001  # how fast lift drops off with altitude
    slot_mask = Slot.TOP

    def __init__(self, squid, attachment_point):
        super(Balloon, self).__init__(squid, attachment_point)
        self.reset()

    def reset(self):
        self.tether = None
        self.create_body()
        self.tether_to(self.squid.body) 

    def bodies_and_shapes(self):
        bs = super(Balloon, self).bodies_and_shapes()
        if self.tether:
            bs.extend(self.tether.bodies_and_shapes())
        return bs

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
