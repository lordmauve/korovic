import re
from xml.etree.ElementTree import parse
from pkg_resources import resource_stream

import pymunk
from pyglet import gl
from pyglet.event import EventDispatcher
from pyglet.graphics import Batch
from pyglet.sprite import Sprite
from lepton import ParticleSystem
from lepton.emitter import StaticEmitter

from .vector import v
from .camera import Rect
from . import components
from . import loader
from .constants import TARGET_FPS, SEA_LEVEL


class World(EventDispatcher):
    def __init__(self, initial_level):
        super(World, self).__init__()
        self.space = pymunk.Space()
        self.space.gravity = (0.0, -900.0)
        self.space.damping = 0.9

        self.images = {}
        self.sprites = []
        self.batch = Batch()

        components.load_all()
        self.squid = components.Susie(self)

        self.width = None
        self.goal = None

        self.load(initial_level)
        self.create_wall()
        self.particles = ParticleSystem()
        self.crashed = False
        self.won = False

    def create_sprite(self, img, x, y):
        if img not in self.images:
            self.images[img] = loader.image('data/%s.png' % img)
        self.sprites.append(
            Sprite(self.images[img], x=x, y=y, batch=self.batch)
        )

    def load(self, level):
        self.goal = None
        self.width = None
        self.batch = Batch()
        doc = parse(resource_stream(__name__, 'data/levels/%s.svg' % level))

        self.width = w = int(doc.getroot().get('width'))
        h = int(doc.getroot().get('height'))
        self.title = doc.find('.//{http://www.w3.org/2000/svg}title').text
        try:
            self.money = int(doc.find('.//{http://purl.org/dc/elements/1.1/}identifier').text)
        except AttributeError:
            self.money = 3000

        self.squid.money = self.money
        for im in doc.findall('.//{http://www.w3.org/2000/svg}image'):
            mo = re.search(r'(?P<path>\w+/(?P<type>[\w-]+))\.png$', im.get('{http://www.w3.org/1999/xlink}href'))
            if not mo:
                print "Unknown object", im
                continue
            type = mo.group('type')
            path = mo.group('path')
            x = int(float(im.get('x')))
            ih = float(im.get('height'))
            iw = int(float(im.get('width')))
            y = h - int(float(im.get('y')) + ih)

            if type in ['island-lair', 'city']:
                self.create_island(x, x + iw)
                self.create_sprite(path, x, y)
            if type == 'city':
                self.create_goal(x, x + iw)
                # Only if the city straddles the edge of the page
                # Do we create a wall there
                if w - x < iw:
                    self.width = None

        if self.goal:
            if self.width:
                self.create_wall(self.width + 500)
        else:
            self.width = None

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
        self.won = False
        self.clear_particles()
        self.space.add(self.squid.body, *self.squid.shapes)

    def create_wall(self, x=-500, width=500):
        body = pymunk.Body()
        seg = pymunk.Segment(body, (x, 0), (x, 100000), width)
        seg.friction = 0
        self.space.add_static(seg)

    def create_island(self, x1, x2, y=20):
        body = pymunk.Body()
        margin = 50  #  A little leeway to stop susie clipping badly into the sea
        p1 = (x1 - 200 - margin, y - 100)
        p2 = (x1 - margin, y)
        p3 = (x2 + margin, y)
        p4 = (x2 + 200 + margin, y - 100)
        self.space.add_static(pymunk.Segment(body, p1, p2, SEA_LEVEL))
        self.space.add_static(pymunk.Segment(body, p2, p3, SEA_LEVEL))
        self.space.add_static(pymunk.Segment(body, p3, p4, SEA_LEVEL))

    def create_goal(self, x1, x2, y=20):
        self.goal = Rect(v(x1, y), v(x2, y + 100))

    def create_floor(self):
        self.create_island(0, 676)

    def update(self, dt):
        self.particles.update(dt)
        if not self.crashed and not self.won:
            self.check_crash()
            self.squid.update(dt)

            g = self.goal
            if g and self.squid.position in g:
                self.won = True
                self.dispatch_event('on_goal')

        # We run the physics with very small time steps
        # in order to give more sensitive collisions at speed
        for i in xrange(5):
            self.space.step(0.2 / TARGET_FPS)

    def check_crash(self):
        p = self.squid.position
        if p.y < 0:
            self.distance = p.x * 0.1
            self.crashed = True
            self.remove_squid()
            self.dispatch_event('on_crash', self.distance)

    def draw(self, viewport):
        self.batch.draw()
        # Draw with depth testing
        gl.glDepthFunc(gl.GL_LEQUAL)
        if self.crashed:
            # Keep particles going
            self.particles.draw()
        else:
            self.squid.draw()
        gl.glDepthFunc(gl.GL_ALWAYS)

    def controllers(self):
        return list(self.squid.controllers())


World.register_event_type('on_crash')
World.register_event_type('on_goal')
