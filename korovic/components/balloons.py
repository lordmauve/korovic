import math
import pyglet.sprite

from .base import Component
from .squid import Tether, Slot

from ..vector import v


class Balloon(Component):
    LIFT = v(0, 20000)
    MASS = 5
    slot_mask = Slot.TOP
    yfix = -1    # This is a bodge to fix insertion points - see base class

    def __init__(self, squid, attachment_point):
        super(Balloon, self).__init__(squid, attachment_point)
        self.tether = None
        self.create_body()
        self.tether_to(squid.body) 

    def bodies_and_shapes(self):
        bs = super(Balloon, self).bodies_and_shapes()
        if self.tether:
            bs.extend(self.tether.bodies_and_shapes())
        return bs

    def tether_to(self, body):
        self.body.position = body.position - self.insertion_point
        self.tether = Tether(
            a=self.body.local_to_world(self.insertion_point),
            b=v(body.position + self.attachment_point),
            c1=self.body,
            c2=body,
            density=5,
            segments=10
        )

    def update(self, dt):
        self.body.reset_forces()
        self.body.apply_force(self.LIFT)

    @property
    def position(self):
        return v(self.body.position)

    @property
    def rotation(self):
        return self.body.angle

    def draw_component(self):
        if self.tether:
            self.tether.draw()
        super(Balloon, self).draw_component()
