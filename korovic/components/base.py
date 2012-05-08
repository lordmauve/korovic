import json
import pyglet
from pyglet import gl
import pymunk
import math

from ..vector import v
from .. import loader


class Component(object):
    MASS = 50.0
    selected = False

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
        cls.moi = moi  # moment of intertia

    def __init__(self, squid, attachment_point, angle=0):
        self.squid = squid
        self.attachment_point = attachment_point
        self.angle = angle
        self.sprite = pyglet.sprite.Sprite(self.image, 0, 0)

    @property
    def position(self):
        return v(self.squid.body.local_to_world(self.attachment_point))

    def create_body(self):
        self.body = pymunk.Body(self.MASS, self.moi)
        self.shapes = []
        for centre, radius in self.circles:
            c = pymunk.Circle(self.body, radius, centre)
            c.friction = 50000.0
            c.elasticity = 0.01
            self.shapes.append(c)

    def set_rotation(self, angle):
        self.body.angle = angle
        self.sprite.rotation = -180 / math.pi * self.body.angle

    def get_rotation(self):
        return self.body.angle

    rotation = property(get_rotation, set_rotation)

    def draw(self):
        if self.selected:
            self.draw_selected()
        else:
            self.draw_component()

    def draw_selected(self):
        gl.glColor3f(0, 1, 0)
        self.draw_component()
        gl.glColor3f(1, 1, 1)

    def velocity(self):
        """The velocity of the component through space."""
        # FIXME: take into account angular momentum
        return v(self.squid.body.velocity)

    def wind(self):
        """The wind velocity over the component."""
        vel = -self.velocity()
        a = self.squid.body.angle + self.angle
        return vel.rotated(math.degrees(-a))

    def apply_force(self, f):
        """Apply force f (relative to the component) at the attachment point"""
        f = f.rotated(math.degrees(self.squid.body.angle + self.angle))
        pos = self.squid.body.local_to_world(self.attachment_point) - self.squid.body.position
        self.squid.body.apply_force(f=f, r=pos)


class ActivateableComponent(Component):
    def __init__(self, squid, attachment_point, angle=0):
        super(ActivateableComponent, self).__init__(squid, attachment_point, angle)
        self.active = False

    def set_active(self, active):
        self.active = active

    def is_active(self):
        return self.active
