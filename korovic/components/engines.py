import math

from ..vector import v
from ..editor import AngleEditor
from ..controllers import PressController, OneTimeController

from .base import ActivateableComponent
from .squid import Slot


class JetEngine(ActivateableComponent):
    slot_mask = Slot.SIDE
    FORCE = v(100000, 0)

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
    MASS = 10
    BURN_TIME = 3
    FORCE = v(100000, 0)

    def controller(self):
        return OneTimeController(self)

    def set_active(self, _):
        if not self.active:
            self.time_left = self.BURN_TIME
            self.active = True

    def update(self, dt):
        if self.active:
            self.time_left -= dt
            if self.time_left > 0:
                super(Rocket, self).update(dt)


class Propeller(JetEngine):
    MASS = 3
    slot_mask = Slot.TOP | Slot.BOTTOM | Slot.NOSE
    FORCE = v(60000, 0)
    angles = {
        Slot.TOP: math.pi * 0.5,
        Slot.BOTTOM: math.pi * 1.5,
        Slot.NOSE: 0
    }

    def set_angle(self):
        """Angle is not user modifiable"""

    @property
    def angle(self):
        return self.angles[self.slot.flags]

    def controller(self):
        return PressController(self)

    def editor(self):
        return None


class PulseJet(JetEngine):
    MASS = 20
    slot_mask = Slot.TOP
    FORCE = v(40000, 0)

    def editor(self):
        return AngleEditor(self, min_angle=-5, max_angle=30)
