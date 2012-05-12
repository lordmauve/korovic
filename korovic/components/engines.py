import math
from pyglet import gl
from pyglet.graphics import Batch
from pyglet.sprite import Sprite

from lepton import Particle, ParticleGroup
from lepton.emitter import StaticEmitter
from lepton import controller
from lepton import domain

from ..constants import SEA_LEVEL
from ..vector import v
from ..editor import AngleEditor
from ..controllers import PressController, OneTimeController

from .base import Component, ActivateableComponent
from .squid import Slot

from .. import loader


class OnAnimation(Component):
    abstract = True
    @classmethod
    def load(cls):
        super(OnAnimation, cls).load()
        cls.image_on = loader.image('data/sprites/%s-on.png' % cls.__name__.lower())
        cls.image_on.anchor_x = cls.image.anchor_x
        cls.image_on.anchor_y = cls.image.anchor_y

    def draw(self):
        if self.active and self.is_enabled():
            self.sprite.image = self.image_on
        else:
            self.sprite.image = self.image
        super(OnAnimation, self).draw()


class Engine(ActivateableComponent):
    abstract = True
    slot_mask = Slot.SIDE
    FORCE = v(100000, 0)
    FUEL_CONSUMPTION = 6
    OFFSET = v(0, 0)

    def update(self, dt):
        if self.active:
            if self.squid.draw_fuel(self.FUEL_CONSUMPTION * dt):
                self.apply_force_relative(self.FORCE, self.OFFSET)

    def is_enabled(self):
        return self.squid.has_fuel()

    def controller(self):
        return PressController(self)

    def editor(self):
        return AngleEditor(self)


class JetEngine(OnAnimation, Engine):
    """A jet engine."""


class Renderer(object):
    """A replacement for lepton's billboard renderer."""
    def __init__(self, image):
        self.image = image

    def draw(self, group):
        batch = Batch()
        ss = []
        for particle in group:
            s = Sprite(self.image, batch=batch)
            s.position = list(particle.position)[:2]
            s.color = [c * 255 for c in list(particle.color)[:3]]
            s.scale = particle.size[0] / 64.0
            s.rotation = particle.age * 720
            s.opacity = particle.color[3] * 255
            ss.append(s)
        batch.draw()
            

class Rocket(Engine):
    @classmethod
    def load(cls):
        super(Rocket, cls).load()
        img = loader.image('data/sprites/rocket-spark.png')
        cls.particle_texture = img 
        w = img.width
        h = img.height
        img.anchor_x = w * 0.5
        img.anchor_y = h * 0.5
        cls.particle_controllers = [
            controller.Movement(),
            controller.Lifetime(max_age=2),
            controller.Growth(30.0),
            controller.ColorBlender([
                (0, (1.0, 0.9, 0.0, 1.0)),
                (1, (0.0, 0.0, 0.0, 0.2)),
                (3, (0.0, 0.0, 0.0, 0.0)),
            ]),
            controller.Bounce(
                domain=domain.Plane(
                    (0, SEA_LEVEL, 0),
                    (0, 1, 0)
                ),
                bounce=0.02
            )
        ]
        cls.particle_renderer = Renderer(cls.particle_texture)

    MASS = 10
    BURN_TIME = 3
    FORCE = v(100000, 0)
    FUEL_CONSUMPTION = 0

    def __init__(self, *args):
        super(Rocket, self).__init__(*args)
        psystem = self.squid.world.particles
        self.particlegroup = ParticleGroup(
            renderer=self.particle_renderer,
            controllers=self.particle_controllers,
            system=psystem
        )

        self.emitter = None

    def __del__(self):
        self.particlegroup.system.remove_group(self.particlegroup)

    def controller(self):
        return OneTimeController(self)

    def is_enabled(self):
        return not self.active

    def set_active(self, _):
        if not self.active:
            self.time_left = self.BURN_TIME
            self.active = True
            
            # Stuff in any numbers for now, update later
            self.vel_domain = domain.Disc(
                (0, 0, 0),
                (0, 0, 1),
                100
            )
            self.pos_domain = domain.Cone(
                (0, 0, 0),
                (-1, 0, 0),
                1
            )
            self.template = Particle(
                size=(20.0, 20.0, 0),
                color=(1.0, 0.5, 0.0, 1.0),
            )
            self.emitter = StaticEmitter(
                position=self.pos_domain,
                velocity=self.vel_domain,
                template=self.template,
                rate=30,
                time_to_live=self.BURN_TIME,
            )
            self.particlegroup.bind_controller(self.emitter)

    def update_emitter(self, dt):
        tv = v(-100, 0).rotated(math.degrees(self.rotation))  # thrust vel
        bv = v(self.squid.body.velocity)  # body vel

        ve = (tv + bv) * 0.5  # velocity of emitted particles
        self.vel_domain.center = (ve.x, ve.y, 0)

        pos = self.position
        cone = ve * dt
        if cone.length2 < 0.001:
            cone = tv * 0.1
        base = pos + cone
        self.pos_domain.apex = (pos.x, pos.y, 0)
        self.pos_domain.base = (base.x, base.y, 0)
        self.pos_domain.outer_radius = cone.length * 0.2
    
    def update(self, dt):
        if self.active:
            self.time_left -= dt
            if self.time_left > 0:
                self.update_emitter(dt)
                super(Rocket, self).update(dt)

    def draw_particles(self):
        self.particlegroup.draw()

    def draw(self):
        self.draw_particles()
        super(Rocket, self).draw()


class Propeller(OnAnimation, Engine):
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


class PulseJet(Engine):
    MASS = 20
    slot_mask = Slot.TOP
    FORCE = v(40000, 0)
    FUEL_CONSUMPTION = 1
    OFFSET = v(0, 22)  # Offset of force from attachment point

    def editor(self):
        return AngleEditor(self, min_angle=-5, max_angle=30)


class Rotor(OnAnimation, Engine):
    MASS = 30
    FORCE = v(0, 140000)
    OFFSET = v(0, 100)
    slot_mask = Slot.TOP

    FUEL_CONSUMPTION = 5

    def editor(self):
        return AngleEditor(self, min_angle=-10, max_angle=10)
