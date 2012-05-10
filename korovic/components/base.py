import json
import pyglet
from pyglet import gl
import pymunk
import math

from ..vector import v
from .. import loader


class Component(object):
    MASS = 50.0
    CAPACITY = 0
    slot_mask = 1

    selected = False
    angle = 0
    abstract = True

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
        cls.insertion_point = -cog
        cls.moi = moi  # moment of inertia

    def __init__(self, squid, attachment_point):
        self.squid = squid
        self.attachment_point = attachment_point
        self.sprite = pyglet.sprite.Sprite(self.image, 0, 0)

    @classmethod
    def get_icon(cls, size=48):
        w, h = cls.image.width, cls.image.height
        s = max(w, h)
        img = cls.image.get_texture()
        img.anchor_x = w * 0.5
        img.anchor_y = h * 0.5
        icon = pyglet.sprite.Sprite(img)
        if s > size:
            icon.scale = float(size) / s
        return icon

    @property
    def position(self):
        """World position of the component."""
        p = self.attachment_point + self.insertion_point.rotated(math.degrees(self.angle))  # position of the insertion point in body space
        return v(self.squid.body.local_to_world(p))
    
    @property
    def rotation(self):
        """World rotation of the component."""
        return self.angle + self.squid.body.angle

    def radius(self):
        return (self.sprite.width + self.sprite.height) * 0.5

    def create_body(self):
        self.body = pymunk.Body(self.MASS, self.moi)
        self.shapes = []
        for centre, radius in self.circles:
            c = pymunk.Circle(self.body, radius, centre)
            c.friction = 50000.0
            c.elasticity = 0.01
            self.shapes.append(c)

    def draw_component(self):
        self.sprite.set_position(*self.position)
        self.sprite.rotation = -math.degrees(self.rotation)
        self.sprite.draw()

    def draw(self):
        if self.selected:
            self.draw_selected()
        else:
            self.draw_component()

    def update(self, dt):
        """Components can override this to add behaviour."""

    def controller(self):
        """Components can return a controller here that can respond to input events."""

    def draw_selected(self):
        gl.glColor3f(0, 1, 0)
        self.draw_component()
        gl.glColor3f(1, 1, 1)

    def velocity(self):
        """The velocity of the component through space."""
        # FIXME: take into account angular momentum
        return v(self.squid.body.velocity)

    def relative_wind(self):
        """The wind velocity over the component in component space."""
        vel = -self.velocity()
        a = self.squid.body.angle + self.angle
        return vel.rotated(math.degrees(-a))

    wind = relative_wind

    def absolute_wind(self):
        """The wind velocity over the component in world space"""
        return self.velocity()

    def apply_force_absolute(self, f):
        """Apply force f (in world space) at the attachment point"""
        pos = self.squid.body.local_to_world(self.attachment_point) - self.squid.body.position
        self.squid.body.apply_force(f=f, r=pos)

    def apply_force_relative(self, f):
        """Apply force f (in component space) at the attachment point"""
        f = f.rotated(math.degrees(self.squid.body.angle + self.angle))
        pos = self.squid.body.local_to_world(self.attachment_point) - self.squid.body.position
        self.squid.body.apply_force(f=f, r=pos)

    apply_force = apply_force_relative

    def reset(self):
        """Reset the state of the component."""


class ActivateableComponent(Component):
    abstract = True
    initial = False

    def __init__(self, squid, attachment_point):
        super(ActivateableComponent, self).__init__(squid, attachment_point)
        self.reset()

    def set_active(self, active):
        self.active = active

    def is_active(self):
        return self.active

    def reset(self):
        """Reset the state of the component."""
        self.active = self.initial
