import math

from ..vector import v
from ..editor import AngleEditor

from .base import Component


class Wing(Component):
    def draw_component(self):
        self.sprite.set_position(*self.position)
        self.sprite.rotation = -180 / math.pi * (self.angle + self.squid.body.angle)
        self.sprite.draw()

    def update(self, dt):
        wind = self.wind()
        drag = v(wind.x * -0.1, wind.y * -0.5)
        lift = v(0, min(50000, abs(wind.x) * 100))
        # FIXME: make lift vary with angle of attack
        self.apply_force(lift + drag)

    def controller(self):
        return None

    def editor(self):
        return AngleEditor(self, max_angle=20)
