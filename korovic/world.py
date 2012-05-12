import pymunk
from pyglet.event import EventDispatcher

from . import components
from .constants import TARGET_FPS, SEA_LEVEL

from lepton import ParticleSystem
from lepton.emitter import StaticEmitter


class World(EventDispatcher):
    def __init__(self):
        super(World, self).__init__()
        self.space = pymunk.Space()
        self.space.gravity = (0.0, -900.0)
        self.space.damping = 0.9
        self.create_floor(self.space, 20)

        components.load_all()

        self.particles = ParticleSystem()
        self.squid = components.Susie(self)
        self.crashed = False

    def clear_particles(self):
        for group in self.particles:
            for c in list(group.controllers):
                if isinstance(c, StaticEmitter):
                    group.unbind_controller(c)
            group.update(10)  # force any particles to expire

    def remove_squid(self):
        try:
            self.space.remove(self.squid.body, *self.squid.shapes)
        except KeyError:
            pass

    def reset(self):
        self.remove_squid()
        self.squid.reset()
        self.crashed = False
        self.clear_particles()
        self.space.add(self.squid.body, *self.squid.shapes)

    def create_floor(self, space, y=0):
        body = pymunk.Body()
        space.add_static(pymunk.Segment(body, (0, y), (676, y), SEA_LEVEL))
        space.add_static(pymunk.Segment(body, (676, y), (876, y - 100), SEA_LEVEL))
        space.add_static(pymunk.Segment(body, (-50, 0), (-50, 100000), 50))

    def update(self, dt):
        self.particles.update(dt)
        if not self.crashed:
            self.check_crash()
            self.squid.update(dt)
        self.space.step(1.0 / TARGET_FPS)

    def check_crash(self):
        p = self.squid.position
        if p.y < 0:
            self.distance = p.x * 0.1
            self.crashed = True
            self.remove_squid()
            self.dispatch_event('on_crash', self.distance)

    def draw(self):
        if self.crashed:
            # Keep particles going
            self.particles.draw()
        else:
            self.squid.draw()

    def controllers(self):
        return list(self.squid.controllers())


World.register_event_type('on_crash')
