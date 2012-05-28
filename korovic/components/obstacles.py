import math
import pyglet.sprite

from .base import Component
from .squid import Tether

from ..vector import v


class BarrageBalloon(Component):
    """Only a subclass of component to allow loading."""
    LIFT = v(0, 100000)
    MASS = 50
    collision_group = 2

    def __init__(self):
        self.sprite = pyglet.sprite.Sprite(self.image, 0, 0)
        self.create_body()
        self.tether = None

    def bodies_and_shapes(self):
        bs = super(BarrageBalloon, self).bodies_and_shapes()
        if self.tether:
            bs.extend(self.tether.bodies_and_shapes())
        return bs

    def tether_to(self, body, alt):
        self.body.position = body.position + v(0, alt)
        self.tether = Tether(
            a=self.body.local_to_world(-self.insertion_point),
            b=v(body.position),
            c1=self.body,
            c2=body,
            density=5,
            segments=int(alt * 0.01)
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

    def draw(self):
        self.tether.draw()
        self.draw_component()
