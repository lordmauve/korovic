import pymunk

from .components import Susie, JetEngine
from .controllers import NullController


class World(object):
    def __init__(self):
        self.space = pymunk.Space()
        self.space.gravity = (0.0, -900.0)
        self.space.damping = 0.9
        self.create_floor(self.space, 20)

        Susie.load()
        JetEngine.load()
        self.squid = Susie((150, 200))
        self.squid.attach(JetEngine)
        self.squid.attach(JetEngine, 1)
        self.space.add(self.squid.body, *self.squid.shapes)

    def create_floor(self, space, y=0):
        body = pymunk.Body()
        floor = pymunk.Segment(body, (0, y), (200, y), 50)
        wall = pymunk.Segment(body, (-50, 0), (-50, 10000), 50)
        space.add_static(floor)
        space.add_static(wall)

    def update(self, dt):
        from .game import TARGET_FPS
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

