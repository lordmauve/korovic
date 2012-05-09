import math
import pyglet.sprite
from .base import Component

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

    def can_attach(self, id, component):
        s = self.slots[id]
        if s.component:
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
        component.slot = self.slots[id]

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
    ANGULAR_VELOCITY_DAMPING = 0.8
    def __init__(self, pos=(0, 0)):
        self.create_body()
        self.sprite = pyglet.sprite.Sprite(self.image, 0, 0)
        self.body.position = pos
        self.body.angular_velocity_limit = 1.5  # Ensure Susie can't spin too fast
        self.slots = Slots(self)

        self.slots.add_slot(self.circles[2][0], Slot.SIDE)
        self.slots.add_slot(self.circles[3][0], Slot.SIDE)
        self.slots.add_slot(self.circles[2][0] + v(0, 20), Slot.TOP)
        self.slots.add_slot(self.circles[2][0] - v(0, 20), Slot.BOTTOM)
        self.slots.add_slot(self.circles[2][0] + v(85, 0), Slot.NOSE)
        self.slots.add_slot(self.circles[3][0] + v(0, 15), Slot.TOP)
        self.slots.add_slot(self.circles[3][0] - v(0, 15), Slot.BOTTOM)
        self.slots.add_slot(self.circles[3][0] - v(38, 4), Slot.NOSE)

    def set_position(self, pos):
        self.body.position = pos
        self.sprite.position = pos

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
        for a in self.slots.components:
            a.update(dt)
        self.body.angular_velocity *= self.ANGULAR_VELOCITY_DAMPING

    def draw_component(self, selected=None):
        self.sprite.set_position(*self.body.position)
        self.sprite.rotation = -180 / math.pi * self.body.angle
        self.sprite.draw()

    def draw(self):
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
