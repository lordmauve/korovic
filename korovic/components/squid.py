import math
import pyglet.sprite
from .base import Component


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

    def next_attachment_point(self):
        # FIXME: maintain a list of free/occupied slots
        return 0

    def set_position(self, pos):
        self.body.position = pos
        self.sprite.position = pos

    def get_position(self):
        return self.body.position

    position = property(get_position, set_position)

    def total_weight(self):
        return sum([c.MASS for c in self.attachments], self.MASS)

    def attach(self, component_class, pos=None):
        if pos is None:
            pos = self.next_attachment_point()
        inst = component_class(self, self.attachment_points[pos])
        self.attachments.append(
           inst 
        )
        return inst

    def has(self, class_):
        """Determine if this squid has an instance of a component class attached.
        """
        for a in self.attachments:
            if a.__class__ is class_:
                return True
        return False

    def remove(self, class_):
        """Remove an instance of class_ from the attached components.
        """
        for a in self.attachments[:]:
            if a.__class__ is class_:
                self.attachments.remove(a)
                return a
        raise ValueError("%s is not attached" % class_)

    def controllers(self):
        for a in self.attachments:
            c = a.controller()
            if c:
                yield c

    def update(self, dt):
        self.body.reset_forces()
        for a in self.attachments:
            a.update(dt)
        self.body.angular_velocity *= self.ANGULAR_VELOCITY_DAMPING

    def draw_component(self, selected=None):
        self.sprite.set_position(*self.body.position)
        self.sprite.rotation = -180 / math.pi * self.body.angle
        self.sprite.draw()

    def draw(self):
        self.draw_component()
        for a in self.attachments:
            a.draw()

    def draw_selected(self, editor=None):
        self.draw_component()
        if editor is not None:
            for a in self.attachments:
                if a is not editor.component:
                    a.draw()
                editor.draw()
        else:
            for a in self.attachments:
                a.draw()
