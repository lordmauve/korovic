import math
from pyglet import gl
import pyglet.sprite

from lepton import Particle, ParticleGroup
from lepton.emitter import StaticEmitter
from lepton import texturizer
from lepton import renderer
from lepton import controller
from lepton import domain

from ..vector import v
from ..editor import AngleEditor
from ..controllers import PressController, OneTimeController

from .base import Component, ActivateableComponent
from .squid import Slot

from .. import loader


class JetEngine(ActivateableComponent):
    slot_mask = Slot.SIDE
    FORCE = v(100000, 0)
    FUEL_CONSUMPTION = 6

    def update(self, dt):
        if self.active:
            if self.squid.draw_fuel(self.FUEL_CONSUMPTION * dt):
                force = self.FORCE.rotated((self.angle + self.squid.body.angle) * 180 / math.pi)
                pos = self.squid.body.local_to_world(self.attachment_point) - self.squid.body.position
                self.squid.body.apply_force(f=force, r=pos)

    def is_enabled(self):
        return self.squid.has_fuel()

    def controller(self):
        return PressController(self)

    def editor(self):
        return AngleEditor(self)


class Rocket(JetEngine):
    @classmethod
    def load(cls):
        super(Rocket, cls).load()
        cls.particle_texture = loader.texture('data/sprites/rocket-spark.png')
        cls.particle_controllers = [
            controller.Lifetime(max_age=3),
            controller.Growth(300, 0.8),
            controller.ColorBlender([
                (1, (1.0, 0.9, 0.0, 0.0)),
                (3, (0.0, 0.0, 0.0, 0)),
            ])
        ]
        cls.particle_renderer = renderer.PointRenderer(20,
            texturizer=texturizer.SpriteTexturizer(cls.particle_texture.id)
        )
        cls.particle_renderer = renderer.BillboardRenderer(
            texturizer=texturizer.SpriteTexturizer(cls.particle_texture.id)
        )

    MASS = 10
    BURN_TIME = 3
    FORCE = v(100000, 0)
    FUEL_CONSUMPTION = 0

    def __init__(self, *args):
        super(Rocket, self).__init__(*args)
        self.particlegroup = ParticleGroup(
            renderer=self.particle_renderer,
            controllers=[
                controller.Lifetime(max_age=3),
                controller.Growth(100, 0.8),
#                controller.ColorBlender([
#                    (1, (1.0, 0.9, 0.0, 0.0)),
#                    (3, (0.0, 0.0, 0.0, 0)),
#                ])
            ]
        )

        self.emitter = None

    def controller(self):
        return OneTimeController(self)

    def is_enabled(self):
        return not self.active

    def set_active(self, _):
        if not self.active:
            self.time_left = self.BURN_TIME
            self.active = True
            vel = v(-200, 0).rotated(math.degrees(self.rotation))
            
            self.vel_domain = domain.Disc(
                (vel.x, vel.y, 0),
                (0, 0, 1),
                100
            )
            self.pos_domain = domain.Disc(
                (self.position.x, self.position.y, 0),
                (0, 0, 1),
                30
            )
            self.template = Particle(
                size=(30, 30, 0),
                rotation=(0, 0, 1.5),
                color=(1, 1, 1),
            )
            self.emitter = StaticEmitter(
                position=self.pos_domain,
                velocity=self.vel_domain,
                template=self.template,
                rate=30,
                time_to_live=self.BURN_TIME,
            )
            self.particlegroup.bind_controller(self.emitter)

    def update(self, dt):
        if self.active:
            self.time_left -= dt
            if self.time_left > 0:
                p = (self.position.x, self.position.y, 0)
                self.pos_domain.center = p
                super(Rocket, self).update(dt)
        self.particlegroup.update(dt)

    def draw_particles(self):
        self.particlegroup.draw()

    def draw(self):
        self.draw_particles()
        super(Rocket, self).draw()


class Propeller(JetEngine):
    MASS = 3
    slot_mask = Slot.TOP | Slot.BOTTOM | Slot.NOSE
    FORCE = v(40000, 0)
    angles = {
        Slot.TOP: math.pi * 0.5,
        Slot.BOTTOM: math.pi * 1.5,
        Slot.NOSE: 0
    }
    FUEL_CONSUMPTION = 2

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
    FORCE = v(60000, 0)
    FUEL_CONSUMPTION = 1

    def editor(self):
        return AngleEditor(self, min_angle=-5, max_angle=30)
