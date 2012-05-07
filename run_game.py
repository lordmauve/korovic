import json
import math

import pyglet
from pyglet import gl
from pyglet.window import key
import pymunk

from vector import v

NAME = 'Susie'
TARGET_FPS = 30.0
SCREEN_SIZE = (800, 600)


class Component(object):
    MASS = 50.0

    @classmethod
    def load(cls):
        cls.data = json.load(open('data/components/%s.json' % cls.__name__.lower()))
        cls.image = pyglet.image.load('data/' + cls.data['name'])
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
            force = v(500, 0).rotated((self.angle + self.squid.body.angle) * 180 / math.pi)
            pos = self.squid.body.local_to_world(self.attachment_point) - self.squid.body.position
            self.squid.body.apply_force(f=force, r=pos)

    def controller(self):
        return PressController(self)


class PressController(object):
    def __init__(self, component):
        self.component = component

    def on_press(self):
        self.component.set_active(True)

    def on_release(self):
        self.component.set_active(False)


class NullController(object):
    def on_press(self):
        """Don't do anything."""

    def on_release(self):
        """Don't do anything."""

    def update(self, dt):
        """Don't do anything."""


class World(object):
    def __init__(self):
        self.space = pymunk.Space()
        self.space.gravity = (0.0, -900.0)
        self.create_floor(self.space, 20)

        Susie.load()
        JetEngine.load()
        self.squid = Susie((150, 200))
        self.squid.attach(JetEngine)
        self.squid.attach(JetEngine, 1)
        self.space.add(self.squid.body, *self.squid.shapes)

    def create_floor(self, space, y=0):
        body = pymunk.Body()
        self.floor = pymunk.Segment(body, (0, y), (200, y), 50)
        space.add_static(self.floor)

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


class Game(object):
    def start(self):
        w, h = SCREEN_SIZE
        self.window = pyglet.window.Window(width=w, height=h, caption=NAME)
        self.world = World()

        self.fps_display = pyglet.clock.ClockDisplay()

        pyglet.clock.schedule_interval(self.update, 1/TARGET_FPS)
        self.window.set_handlers(
            on_draw=self.draw,
            on_key_press=self.on_key_press,
            on_key_release=self.on_key_release
        )

        pyglet.app.run()

    def draw(self):
        gl.glClearColor(0.7, 0.7, 1, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        self.world.draw()

    def update(self, dt):
        self.world.update(dt)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.F12:
            from .screenshot import take_screenshot
            take_screenshot(self.window)
            return
        if key._0 <= symbol <= key._9:
            controller = symbol - key._0
            self.world.get_controller(controller).on_press()

    def on_key_release(self, symbol, modifiers):
        """Key has been released."""
        if key._0 <= symbol <= key._9:
            controller = symbol - key._0
            self.world.get_controller(controller).on_release()


if __name__ == '__main__':
    g = Game()
    g.start()
