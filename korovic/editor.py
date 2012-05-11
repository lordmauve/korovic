import math
from pyglet import gl
from pyglet.event import EVENT_HANDLED

from .vector import v

from .constants import SELECTED_COLOUR, WHITE
from .primitives import Protractor


class AngleEditor(object):
    def __init__(self, component, min_angle=0, max_angle=135):
        self.component = component
        self.min_angle = min_angle
        self.max_angle = max_angle
        adeg = self.component.angle * (180 / math.pi)
        pos = self.component.attachment_position()
        self.protractor = Protractor(
            centre=pos,
            radius=60,
            angle=adeg,
            min_angle=self.min_angle,
            max_angle=self.max_angle
        )
        self.dragging = False

    def draw(self):
        self.component.sprite.color = SELECTED_COLOUR
        self.component.draw()
        gl.glColor3f(*SELECTED_COLOUR)
        self.protractor.draw()
        gl.glColor3f(*WHITE)
        self.component.sprite.color = WHITE

    def get_handlers(self):
        return {
            'on_mouse_press': self.on_mouse_press,
            'on_mouse_release': self.on_mouse_release,
            'on_mouse_drag': self.on_mouse_drag,
        }

    def on_mouse_press(self, x, y, button, modifiers):
        p = v(x, y)
        self.dragging = (p - self.protractor.centre).length <= 80
        if self.dragging:
            return EVENT_HANDLED

    def on_mouse_release(self, x, y, button, modifiers):
        self.dragging = False

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.dragging:
            p = v(x, y)
            angle = (p - self.protractor.centre).angle
            angle = min(self.max_angle, max(self.min_angle, angle))
            self.component.angle = math.radians(angle)
            self.protractor.set_angle(angle)
            return EVENT_HANDLED
