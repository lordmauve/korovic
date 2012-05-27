import math
from pyglet import gl
from pyglet.event import EVENT_HANDLED

from .vector import v

from .constants import SELECTED_COLOUR, WHITE
from .primitives import Protractor
from .sound import load_sound


class SlotEditor(object):
    def __init__(self, component):
        self.component = component
        self.display_offset = v(0, 0)
        self.dragging = False
        self.proposed_slot = None
        self.real_slot = component.slot

    def draw(self):
        self.component.sprite.color = SELECTED_COLOUR
        if self.dragging:
            opacity = 127 if not self.proposed_slot else 255
            position = self.display_offset if not self.proposed_slot else self.proposed_slot[1]
            sopacity = self.component.sprite.opacity
            gl.glPushMatrix()
            gl.glTranslatef(position.x, position.y, 0)
            self.component.sprite.opacity = opacity
            self.component.draw()
            self.component.sprite.opacity = sopacity
            gl.glPopMatrix()
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
        self.dragging = (p - self.component.position).length <= 70
        if self.dragging:
            self.start_pos = self.component.attachment_position()
            return EVENT_HANDLED

    def on_mouse_release(self, x, y, button, modifiers):
        if self.dragging:
            if self.proposed_slot:
                slots = self.component.squid.slots
                slots.remove(self.component)
                slots.attach(self.proposed_slot[0], self.component)
                self.real_slot = self.component.slot
            else:
                self.component.attach_at_slot(self.real_slot)
            self.proposed_slot = None
            self.display_offset = v(0, 0)
            self.dragging = False
            return EVENT_HANDLED

    def find_slot(self):
        """Find a suitable slot to re-attach the component"""
        dist = 6400
        slot = None
        slots = self.component.squid.slots
        ap = self.start_pos + self.display_offset
        for i, pos in slots.slot_positions():
            can_attach = slots.can_attach(i, self.component)
            if not can_attach:
                continue
            self.component.slot = slots.slots[i]
            self.component.attachment_point = slots.slots[i].pos
            d = (ap - pos).length2 
            if d < dist:
                slot = i
                dist = d

        if slot is not None:
            self.proposed_slot = (slot, v(0, 0))
            self.component.attach_at_slot(slots.slots[slot])
        else:
            self.proposed_slot = None

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.dragging:
            self.display_offset += v(dx, dy)
            self.find_slot()
            return EVENT_HANDLED


class AngleEditor(SlotEditor):
    @classmethod
    def load(cls):
        if not hasattr(cls, 'click'):
            cls.click = load_sound('data/sounds/click.wav')

    def __init__(self, component, min_angle=0, max_angle=135):
        super(AngleEditor, self).__init__(component)
        self.load()
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.adjusting = False
        self.build_protractor()

    def build_protractor(self):
        adeg = self.component.angle * (180 / math.pi)
        pos = self.component.attachment_position()
        self.protractor = Protractor(
            centre=pos,
            radius=120,
            angle=adeg,
            min_angle=self.min_angle,
            max_angle=self.max_angle
        )

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
        if ret:
            self.build_protractor()
            return ret
        if self.adjusting:
            self.adjusting = False
            return EVENT_HANDLED

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        ret = super(AngleEditor, self).on_mouse_drag(x, y, dx, dy, buttons, modifiers)
        if ret: return ret
        if self.adjusting:
            self.click.play()
            p = v(x, y)
            angle = (p - self.protractor.centre).angle
            angle = min(self.max_angle, max(self.min_angle, angle))
            self.component.angle = math.radians(angle)
            self.protractor.set_angle(angle)
            return EVENT_HANDLED
