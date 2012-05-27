import math
import pymunk
import pyglet.sprite
import pyglet.graphics
from pyglet import gl
from .base import Component

from ..constants import SEA_LEVEL, TARGET_FPS

from .. import loader
from ..vector import v


class Slot(object):
    # Bit flags to determine what can be attached where
    SIDE = 1
    BOTTOM = 2
    TOP = 4
    NOSE = 8
    TAIL = 16

    def __init__(self, pos, flags):
        self.pos = pos
        self.flags = flags
        self.component = None


class IncompatibleComponent(Exception):
    """A component was incompatible with the slot or the slot was full."""


class Slots(object):
    """Manage a list of slots"""
    def __init__(self, squid):
        self.squid = squid
        self.slots = []
        self.components = []

    def add_slot(self, pos, flags):
        s = Slot(pos, flags)
        s.id = len(self.slots)
        self.slots.append(s)

    def detach_all(self):
        self.components = []
        for s in self.slots:
            s.component = None

    def slot_position(self, id):
        s = self.slots[id]
        return self.squid.body.local_to_world(s.pos)

    def slot_positions(self):
        for i, s in enumerate(self.slots):
            yield i, self.slot_position(i)

    def can_attach(self, id, component):
        s = self.slots[id]
        if s.component and s.component is not component:
            return False
        return bool(s.flags & component.slot_mask)

    def find_slot(self, component):
        for i, s in enumerate(self.slots):
            if self.can_attach(i, component):
                return i
        raise IncompatibleComponent("No slot available for %s" % component)

    def attach(self, id, component):
        if not self.can_attach(id, component):
            raise IncompatibleComponent('%s not compatible with slot %d' % component, id)
        self.slots[id].component = component
        self.components.append(component)
        self.components.sort(key=lambda c: bool(c.slot_mask & Slot.SIDE))
        component.attach_at_slot(self.slots[id])

    def attach_new(self, id, component_class):
        """Attach a new instance of component_class at id"""
        if not self.can_attach(id, component_class):
            raise IncompatibleComponent('%s not compatible with slot %d' % (component_class, id))
        inst = component_class(self.squid, self.slots[id].pos)
        self.attach(id, inst)

    def remove(self, component):
        for s in self.slots:
            if s.component is component:
                s.component = None
        self.components.remove(component)
        component.slot = None

    def has(self, class_):
        """Determine if this squid has an instance of a component class attached.
        """
        for a in self.components:
            if a.__class__ is class_:
                return True
        return False

    def remove_any(self, class_):
        """Remove an instance of class_ from the attached components.
        """
        for a in self.components[:]:
            if a.__class__ is class_:
                self.remove(a)
                return a
        raise ValueError("%s is not attached" % class_)


class Susie(Component):
    MASS = 25
    ANGULAR_VELOCITY_DAMPING = 0.8
    money = 0

    @classmethod
    def load(cls):
        super(Susie, cls).load()
        img = loader.image('data/sprites/squid-shadow.png') 
        w = img.width
        img.anchor_x = w * 0.5
        cls.shadow_image = img

    def __init__(self, world):
        self.world = world
        self.sprite = pyglet.sprite.Sprite(self.image, 0, 0)
        self.shadow = pyglet.sprite.Sprite(self.shadow_image, 0, 0)
        
        self.slots = Slots(self)
        self.slots.add_slot(self.circles[2][0], Slot.SIDE)
        self.slots.add_slot(self.circles[3][0], Slot.SIDE)
        self.slots.add_slot(self.circles[2][0] + v(0, 22), Slot.TOP)
        self.slots.add_slot(self.circles[2][0] - v(0, 20), Slot.BOTTOM)
        self.slots.add_slot(self.circles[2][0] + v(82, 3), Slot.NOSE)
        self.slots.add_slot(self.circles[3][0] + v(0, 15), Slot.TOP)
        self.slots.add_slot(self.circles[3][0] - v(0, 16), Slot.BOTTOM)
        self.slots.add_slot(self.circles[3][0] - v(34, 1), Slot.TAIL)

        self.spikes = []
        self.reset()

    def bodies_and_shapes(self):
        bs = [self.body] + self.shapes
        for s in self.spikes:
            bs.extend(s.bodies_and_shapes())
        for c in self.slots.components:
            bs.extend(c.bodies_and_shapes())
        return bs
    
    def create_body(self):
        super(Susie, self).create_body()
        self.spikes = [ 
#            TentacleSpike(self, v(-90, 0)),
        ]

    def reset(self, position=(250, 80)):
        self.create_body()
        self.body.angular_velocity_limit = 1.5  # Ensure Susie can't spin too fast
        self.body.mass = self.total_weight()
        self.fuel = self.fuel_capacity()
        self.position = position
        for a in self.slots.components:
            a.reset()

    def draw_fuel(self, amount):
        if amount == 0:
            return True
        if self.has_fuel():
            drawn = min(self.fuel, amount)
            self.body.mass -= drawn
            self.fuel -= drawn
            return True
        else:
            return False

    def stop_all(self):
        for c in self.slots.components:
            try:
                c.on_stop()
            except AttributeError:
                pass

    def has_fuel(self):
        return self.fuel > 0

    def set_position(self, pos):
        self.body.position = pos
        self.sprite.position = pos
        for c in self.slots.components:
            try:
                c.position = Component.get_position(c)
            except AttributeError:
                # position isn't settable, probably because it's derived
                pass
#        self.spikes[0].position += trans

    def get_position(self):
        return self.body.position

    position = property(get_position, set_position)

    def get_rotation(self):
        return self.body.angle

    def set_rotation(self, a):
        self.body.angle = a

    rotation = property(get_rotation, set_rotation)

    def total_weight(self):
        return sum([c.MASS for c in self.slots.components], self.MASS)

    def fuel_capacity(self):
        return sum([c.CAPACITY for c in self.slots.components], self.CAPACITY)

    def need_fuel(self):
        return any([getattr(c, 'FUEL_CONSUMPTION', 0) for c in self.slots.components])

    def attach(self, component_class, pos=None):
        if pos is None:
            pos = self.slots.find_slot(component_class)
        self.slots.attach_new(pos, component_class)

    def controllers(self):
        for a in self.slots.components:
            c = a.controller()
            if c:
                yield c

    def update(self, dt):
        self.body.reset_forces()
        for s in self.spikes:
            s.update(dt)
        for a in self.slots.components:
            a.update(dt)
        self.body.angular_velocity *= self.ANGULAR_VELOCITY_DAMPING

    def draw_component(self, selected=None):
        for s in self.spikes:
            s.draw()
        self.sprite.set_position(*self.body.position)
        self.sprite.rotation = -180 / math.pi * self.body.angle
        self.sprite.draw()

    def draw_shadow(self):
        if self.body.position.y > SEA_LEVEL:
            self.shadow.set_position(self.body.position.x, SEA_LEVEL)
            self.shadow.opacity = max(255 - self.body.position.y, 0)
            self.shadow.draw()

    def draw(self):
        self.draw_shadow()
        self.draw_component()
        for a in self.slots.components:
            a.draw()

    def draw_selected(self, editor=None):
        self.draw_component()
        if editor is not None:
            for a in self.slots.components:
                if a is not editor.component:
                    a.draw()
            editor.draw()
        else:
            for a in self.slots.components:
                a.draw()


class TentacleSpike(Component):
    """For decoration only!"""
    MASS = 0.1
    DRAG = 0.02
    def __init__(self, squid, attachment_point):
        super(TentacleSpike, self).__init__(squid, attachment_point)
        self.create_body()
        self.body.position = squid.position + attachment_point - v(50, 0)
        self.tether = Tether(
            a=self.body.position + v(3, 0),
            b=squid.position + attachment_point,
            c1=self.body,
            c2=self.squid.body,
            segments=5
        )
            
    def update(self, dt):
        vel = v(self.body.velocity)
        speed = vel.length
        if abs(speed) > 1:
            drag = vel.safe_scaled_to(1) * min(speed, 100) * -self.DRAG
            self.body.apply_force(drag)

    def bodies_and_shapes(self):
        bs = [self.body] + self.shapes
        return bs + self.tether.bodies_and_shapes()

    def position(self):
        return self.body.position

    def set_position(self, pos):
        self.body.position = pos
        self.tether.reorient(pos, self.squid.position + self.attachment_point - v(50, 0))
        self.body.angle = 0

    position = property(position, set_position)
    
    @property
    def rotation(self):
        return self.body.angle

    def draw(self):
        self.tether.draw()
        super(TentacleSpike, self).draw()


class Tether(object):
    def __init__(self, a, b, c1=None, c2=None, segments=10, density=0.01, colour=(0, 0, 0, 1), thickness=4):
        """Tether between points a and b.

        if c1 and c2 are given, these are bodies that will be jointed to each end of the tether.
        """
        self.density = density
        self.colour = colour
        self.thickness = thickness
        self.shapes = []
        self.bodies = []
        self.joints = []
        a = v(a)
        b = v(b)
        segment_length = (b - a).length / segments
        for i in xrange(segments + 1):
            frac = float(i) / segments
            pos = frac * b + (1 - frac) * a
            body = self.create_node(pos)
            if self.bodies:
                last = self.bodies[-1]
                self.joints.append(pymunk.SlideJoint(last, body, (0, 0), (0, 0), 0, segment_length))
            self.bodies.append(body)
        if c1:
            self.joints.append(
                pymunk.PivotJoint(c1, self.bodies[0], self.bodies[0].position),
            )
        if c2:
            self.joints.append(
                pymunk.PivotJoint(c2, self.bodies[-1], self.bodies[-1].position),
            )

        for j in self.joints:
            j.error_bias = 0.9 ** 30.0

        self.vertices = pyglet.graphics.vertex_list(len(self.bodies), 'v2f')

    def reorient(self, a, b):
        """Move bodies into a line between a and b"""
        for i, body in enumerate(self.bodies):
            frac = float(i) / (len(self.bodies) - 1)
            pos = frac * b + (1 - frac) * a
            body.position = pos
            body.velocity = v(0, 0)
        self.set_vertex_list(a, b)

    def bodies_and_shapes(self):
        return self.bodies + self.shapes + self.joints

    def set_vertex_list(self, a, b):
        vs = []
        for i, body in enumerate(self.bodies):
            frac = float(i) / (len(self.bodies) - 1)
            pos = frac * b + (1 - frac) * a
            vs.extend(list(pos))
        self.vertices.vertices = vs

    def build_vertex_list(self):
        vs = []
        for b in self.bodies:
            vs.extend(list(b.position))
        self.vertices.vertices = vs

    def draw(self):
        self.build_vertex_list()
        gl.glColor4f(*self.colour)
        gl.glLineWidth(self.thickness)
        self.vertices.draw(gl.GL_LINE_STRIP) 
        gl.glLineWidth(1)

    def create_node(self, pos):
        body = pymunk.Body(self.density, self.density)
        s = pymunk.Circle(body, self.thickness * 0.5)
        s.group = 1
        self.shapes.append(s)
        body.position = pos
        return body
