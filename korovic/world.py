import re
from xml.etree.ElementTree import parse
from pkg_resources import resource_stream

import pymunk
from pyglet import gl
from pyglet.event import EventDispatcher
from pyglet.graphics import Batch
from pyglet.sprite import Sprite
from lepton import ParticleSystem, ParticleGroup, Particle
from lepton import domain
from lepton.emitter import StaticEmitter
from lepton import controller

from .components.engines import Renderer

from .vector import v
from .camera import Rect
from . import components
from . import loader
from .constants import TARGET_FPS, SEA_LEVEL
from .sound import load_sound


class World(EventDispatcher):
    def __init__(self, initial_level):
        super(World, self).__init__()
        self.space = pymunk.Space()
        self.space.gravity = (0.0, -900.0)
        self.space.damping = 0.9
        self.space.iterations = 20

        self.splash = load_sound('data/sounds/splash.wav')

        self.images = {}
        self.sprites = []
        self.actors = []
        self.batch = Batch()

        self.load_sprite('sprites/susie-destroy')
        components.load_all()
        self.squid = components.Susie(self)

        self.width = None
        self.goal = None

        self.load(initial_level)
        self.particles = ParticleSystem()
        self.crashed = False
        self.won = False
        self.splash_group = None

    def particle_splash(self, pos, vel):
        img = self.load_sprite('sprites/drip')
        img.anchor_x = img.width / 2
        img.anchor_y = img.height / 2
        e = StaticEmitter(
            position=domain.Disc(
                (pos.x, SEA_LEVEL, 0),
                (0, 0, 1),
                50
            ),
            velocity=domain.Disc(
                (vel.x, vel.y, 0),
                (0, 0, 1),
                200
            ),
            size=[(64.0, 64.0, 0), (80.0, 80.0, 0), (100.0, 100.0, 0)],
            template=Particle(
                color=(1.0, 1.0, 1.0, 1.0),
            ),
            rate=100,
            time_to_live=0.3
        )
        self.splash_group = ParticleGroup(
            controllers=[
                controller.Movement(),
                controller.Gravity((0, -900, 0)),
                controller.Lifetime(max_age=2),
                e
            ],
            renderer=Renderer(img),
            system=self.particles
        )

    def load_sprite(self, img):
        if img not in self.images:
            self.images[img] = loader.image('data/%s.png' % img)
        return self.images[img]

    def create_sprite(self, img, x, y):
        s = self.load_sprite(img)
        self.sprites.append(
            Sprite(s, x=x, y=y)
        )

    def destroy_actors(self):
        for a in self.actors:
            self.space.remove(*a.bodies_and_shapes())
        self.actors = []
    
    def load(self, level):
        self.space.remove_static(*self.space.static_shapes)
        self.squid.slots.detach_all()
        self.create_wall()
        self.sprites = []
        self.goal = None
        self.width = None
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

            if type == 'island-lair':
                self.create_island(x, x + iw)
                self.create_sprite(path, x, y)
            elif type == 'city':
                self.create_island(x, x + iw)
                self.create_sprite(path, x, y)
                self.create_goal(x, x + iw)
                # Only if the city straddles the edge of the page
                # Do we create a wall there
                if x + iw < w:
                    self.width = None
            elif type == 'barrageballoon':
                balloon = components.BarrageBalloon()
                self.actors.append(balloon)
                b = pymunk.Body()
                b.position = v(x, 0)
                balloon.tether_to(b, y)
                self.space.add(*balloon.bodies_and_shapes())
            else:
                print "Unknown object", path

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
            self.space.remove(*self.squid.bodies_and_shapes())
        except KeyError:
            pass

    def reset(self):
        self.remove_squid()
        self.squid.reset()
        self.crashed = False
        self.won = False
        self.clear_particles()
        self.space.add(self.squid.bodies_and_shapes())

    def create_wall(self, x=-500, width=500):
        body = self.space.static_body
        seg = pymunk.Segment(body, (x, 0), (x, 100000), width)
        seg.friction = 0
        self.space.add_static(seg)

    def create_island(self, x1, x2, y=20):
        body = self.space.static_body
        margin = 50  #  A little leeway to stop susie clipping badly into the sea
        p1 = (x1 - 200 - margin, y - 100)
        p2 = (x1 - margin, y)
        p3 = (x2 + margin, y)
        p4 = (x2 + 200 + margin, y - 100)
        self.space.add_static(pymunk.Segment(body, p1, p2, SEA_LEVEL))
        self.space.add_static(pymunk.Segment(body, p2, p3, SEA_LEVEL))
        self.space.add_static(pymunk.Segment(body, p3, p4, SEA_LEVEL))

    def create_goal(self, x1, x2, y=20):
        self.goal = Rect(v(x1 + 200, y), v(x2 - 200, y + 100))

    def create_floor(self):
        self.create_island(0, 676)

    def update(self, dt):
        self.particles.update(dt)
        for a in self.actors:
            a.update(dt)
        if not self.crashed and not self.won:
            self.check_crash()
            self.squid.update(dt)

            g = self.goal
            if g and self.squid.position in g:
                self.won = True
                self.create_sprite('sprites/susie-destroy', g.left + 200, g.bottom + 22)
                self.dispatch_event('on_goal')

            # We run the physics with very small time steps
            # in order to give more sensitive collisions at speed
            for i in xrange(5):
                self.space.step(0.2 / TARGET_FPS)

    def check_crash(self):
        p = self.squid.position
        if p.y < 0:
            if self.crashed:
                return
            self.distance = p.x * 0.1
            self.crashed = True
            self.remove_squid()
            self.splash.play()
            vx, vy = self.squid.body.velocity * 0.7
            vy = max(20, vy * -1)
            self.particle_splash(p, v(vx, vy))
            self.dispatch_event('on_crash', self.distance)

    def draw(self, viewport):
        for s in self.sprites:
            s.draw()
        # Draw with depth testing
        gl.glDepthFunc(gl.GL_LEQUAL)
        if self.splash_group:
            self.splash_group.draw()
        for a in self.actors:
            a.draw()
        if self.crashed:
            # Keep particles going
            self.particles.draw()
        elif not self.won:
            self.squid.draw()
        gl.glDepthFunc(gl.GL_ALWAYS)

    def controllers(self):
        return list(self.squid.controllers())


World.register_event_type('on_crash')
World.register_event_type('on_goal')
