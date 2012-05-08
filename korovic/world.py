import pymunk

from .components import Susie, JetEngine, Wing, Rocket
from .controllers import NullController
from .constants import TARGET_FPS, SEA_LEVEL


class World(object):
    def __init__(self):
        self.space = pymunk.Space()
        self.space.gravity = (0.0, -900.0)
        self.space.damping = 0.9
        self.create_floor(self.space, 20)

        # FIXME: do loading somewhere sensible
        Susie.load()
        JetEngine.load()
        Wing.load()
        Rocket.load()

        self.squid = Susie((150, 56))
        self.squid.attach(Wing)
        self.squid.attach(JetEngine, 1)
        self.space.add(self.squid.body, *self.squid.shapes)

    def create_floor(self, space, y=0):
        body = pymunk.Body()
        space.add_static(pymunk.Segment(body, (0, y), (676, y), SEA_LEVEL))
        space.add_static(pymunk.Segment(body, (676, y), (876, y - 100), SEA_LEVEL))
        space.add_static(pymunk.Segment(body, (-50, 0), (-50, 100000), 50))

    def update(self, dt):
        self.squid.update(dt)
        self.space.step(1.0/TARGET_FPS)

    def draw(self):
        self.squid.draw()

    def controllers(self):
        return list(self.squid.controllers())

    def get_controller(self, num):
        cs = self.controllers()
        try:
            return cs[(num - 1) % 10]
        except IndexError:
            return NullController()

