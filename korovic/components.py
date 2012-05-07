import json
import pyglet
import pymunk
import math

from .vector import v
from .controllers import PressController
from . import loader


class Component(object):
    MASS = 50.0

    @classmethod
    def load(cls):
        cls.data = json.load(loader.file('data/components/%s.json' % cls.__name__.lower()))
        cls.image = loader.image('data/' + cls.data['name'])
        ax, ay = cls.data['offset']
        # FIXME: this loading is really cludgey
        offset = v(ax, ay)
        circles = []
        circles.append((v(0, 0), cls.data['radius']))
        for point in cls.data.get('points', []):
            centre = v(point['offset']) + offset
            circles.append((v(centre.x, -centre.y), point['radius']))
        total_area = 0
        cs2 = []
        for c, r in circles:
            area = math.pi * r * r
            total_area += area
            cs2.append((c, r, area))

        density = cls.MASS / total_area

        cog = v(0, 0)
        moi = 0
        for c, r, area in cs2:
            cog += c * (area / total_area) 
            moi += pymunk.moment_for_circle(density * area, 0, r, c - cog)

        offset -= cog
        cls.circles = [(c - cog, r) for c, r in circles]

        cls.image.anchor_x = -int(offset.x + 0.5)
        cls.image.anchor_y = int(cls.image.height + offset.y + 0.5)
        cls.moi = moi
        print moi

    def create_body(self):
        self.body = pymunk.Body(self.MASS, self.moi)
        self.shapes = []
        for centre, radius in self.circles:
            c = pymunk.Circle(self.body, radius, centre)
            c.friction = 1.0
            c.elasticity = 0.01
            self.shapes.append(c)


class Susie(Component):
    ANGULAR_VELOCITY_DAMPING = 0.8
    def __init__(self, pos=(0, 0)):
        self.create_body()
        self.sprite = pyglet.sprite.Sprite(self.image, 0, 0)
        self.body.position = pos
        self.body.angular_velocity_limit = 1.5  # Ensure Susie can't spin too fast
        self.attachment_points = [
            self.circles[2][0],
            self.circles[3][0],
        ]
        self.attachments = []

    def attach(self, component_class, pos=0):
        inst = component_class(self, self.attachment_points[pos])
        self.attachments.append(
           inst 
        )
        return inst

    def controllers(self):
        for a in self.attachments:
            yield a.controller()

    def update(self, dt):
        self.body.reset_forces()
        for a in self.attachments:
            a.update(dt)
        self.body.angular_velocity *= self.ANGULAR_VELOCITY_DAMPING

    def draw(self):
        self.sprite.set_position(*self.body.position)
        self.sprite.rotation = -180 / math.pi * self.body.angle
        self.sprite.draw()
        for a in self.attachments:
            a.draw()


class JetEngine(Component):
    def __init__(self, squid, attachment_point, angle=math.pi * 0.5):
        self.squid = squid
        self.attachment_point = attachment_point
        self.angle = angle
        self.sprite = pyglet.sprite.Sprite(self.image, 0, 0)
        self.active = False

    def set_active(self, active):
        self.active = active
    
    def draw(self):
        self.sprite.set_position(*self.squid.body.local_to_world(self.attachment_point))
        self.sprite.rotation = -180 / math.pi * (self.angle + self.squid.body.angle)
        self.sprite.draw()

    def update(self, dt):
        if self.active:
            force = v(60000, 0).rotated((self.angle + self.squid.body.angle) * 180 / math.pi)
            pos = self.squid.body.local_to_world(self.attachment_point) - self.squid.body.position
            self.squid.body.apply_force(f=force, r=pos)

    def controller(self):
        return PressController(self)

