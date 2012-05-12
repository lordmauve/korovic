import math
from pyglet import gl
from pyglet.event import EVENT_HANDLED

from .vector import v

from .constants import SELECTED_COLOUR, WHITE
from .primitives import Protractor


class SlotEditor(object):
    def __init__(self, component):
        self.component = component
        self.display_offset = v(0, 0)
        self.dragging = False

    def draw(self):
        self.component.sprite.color = SELECTED_COLOUR
        if self.dragging:
            gl.glPushMatrix(gl.GL_MODELVIEW)
            gl.glTranslatef(self.display_offset.x, self.display_offset.y, 0)
            self.component.sprite.opacity = 127
            self.component.draw()
            gl.glPopMatrix(gl.GL_MODELVIEW)
            self.component.sprite.opacity = 255
        else:
            self.component.draw()
        self.component.sprite.color = WHITE

    def get_handlers(self):
        return {
            'on_mouse_press': self.on_mouse_press,
            'on_mouse_release': self.on_mouse_release,
            'on_mouse_drag': self.on_mouse_drag,
        }

    def on_mouse_press(self, x, y, button, modifiers):
        p = v(x, y)
        self.dragging = (p - self.component.position).length <= self.component.radius()
        if self.dragging:
            return EVENT_HANDLED

    def on_mouse_release(self, x, y, button, modifiers):
        if self.dragging:
            self.display_offset = v(0, 0)
            self.dragging = False
            return EVENT_HANDLED

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.dragging:
            self.display_offset += v(dx, dy)
            return EVENT_HANDLED


class AngleEditor(SlotEditor):
    def __init__(self, component, min_angle=0, max_angle=135):
        super(AngleEditor, self).__init__(component)
        self.min_angle = min_angle
        self.max_angle = max_angle
        adeg = self.component.angle * (180 / math.pi)
        pos = self.component.attachment_position()
        self.protractor = Protractor(
            centre=pos,
            radius=120,
            angle=adeg,
            min_angle=self.min_angle,
            max_angle=self.max_angle
        )
        self.adjusting = False

    def draw(self):
        super(AngleEditor, self).draw()
        if not self.dragging:
            gl.glColor3f(*SELECTED_COLOUR)
            self.protractor.draw()
            gl.glColor3f(*WHITE)

    def on_mouse_press(self, x, y, button, modifiers):
        ret = super(AngleEditor, self).on_mouse_press(x, y, button, modifiers)
        if ret: return ret
        p = v(x, y)
        self.adjusting = 70 < (p - self.protractor.centre).length < 120
        if self.adjusting:
            return EVENT_HANDLED

    def on_mouse_release(self, x, y, button, modifiers):
        ret = super(AngleEditor, self).on_mouse_release(x, y, button, modifiers)
        if ret: return ret
        if self.adjusting:
            self.adjusting = False
            return EVENT_HANDLED

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        ret = super(AngleEditor, self).on_mouse_drag(x, y, dx, dy, buttons, modifiers)
        if ret: return ret
        if self.adjusting:
            p = v(x, y)
            angle = (p - self.protractor.centre).angle
            angle = min(self.max_angle, max(self.min_angle, angle))
            self.component.angle = math.radians(angle)
            self.protractor.set_angle(angle)
            return EVENT_HANDLED
