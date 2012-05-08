import math

from ..vector import v
from ..editor import AngleEditor
from ..controllers import PressController

from .base import Component


class JetEngine(Component):
    def __init__(self, squid, attachment_point, angle=math.pi * 0.5):
        super(JetEngine, self).__init__(squid, attachment_point, angle)
        self.active = False

    def set_active(self, active):
        self.active = active

    def draw_component(self):
        self.sprite.set_position(*self.position)
        self.sprite.rotation = -180 / math.pi * (self.angle + self.squid.body.angle)
        self.sprite.draw()

    def update(self, dt):
        if self.active:
            force = v(60000, 0).rotated((self.angle + self.squid.body.angle) * 180 / math.pi)
            pos = self.squid.body.local_to_world(self.attachment_point) - self.squid.body.position
            self.squid.body.apply_force(f=force, r=pos)

    def controller(self):
        return PressController(self)

    def editor(self):
        return AngleEditor(self)



