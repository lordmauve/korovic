import math

from ..vector import v
from ..editor import AngleEditor
from ..controllers import PressController, OneTimeController

from .base import ActivateableComponent
from .squid import Slot


class JetEngine(ActivateableComponent):
    slot_mask = Slot.SIDE
    FORCE = v(60000, 0)
    def draw_component(self):
        self.sprite.set_position(*self.position)
        self.sprite.rotation = -180 / math.pi * (self.angle + self.squid.body.angle)
        self.sprite.draw()

    def update(self, dt):
        if self.active:
            force = self.FORCE.rotated((self.angle + self.squid.body.angle) * 180 / math.pi)
            pos = self.squid.body.local_to_world(self.attachment_point) - self.squid.body.position
            self.squid.body.apply_force(f=force, r=pos)

    def controller(self):
        return PressController(self)

    def editor(self):
        return AngleEditor(self)


class Rocket(JetEngine):
    BURN_TIME = 3
    FORCE = v(100000, 0)

    def controller(self):
        return OneTimeController(self)

    def set_active(self, _):
        self.time_left = self.BURN_TIME
        self.active = True

    def update(self, dt):
        if self.active:
            self.time_left -= dt
            if self.time_left < 0:
                self.active = False
        super(Rocket, self).update(dt)

