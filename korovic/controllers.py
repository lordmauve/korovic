"""Classes for mapping input to control of components.
"""

from pyglet.window import key

from .vector import v
from .camera import Rect
from .primitives import Rectangle, Label


class ControllerIcon(object):
    """Visual representation of a control binding."""
    def __init__(self, icon):
        self.rect = Rect(v(0, 0), v(64, 64))
        self.r_off = Rectangle(self.rect, [(0, 0, 0, 0.5)])
        self.r_on = Rectangle(self.rect, [(0.5, 0.5, 0.5, 0.5)])
        self.r_disabled = Rectangle(self.rect, [(0, 0, 0, 0.15)])
        self.r = self.r_off 
        self.icon = icon
        self.icon.position = (32, 32)
        self.icon_default_scale = self.icon.scale

        self.label = None
        self.active = False
        self.disabled = False

    def set_label(self, text):
        self.label = Label(
            text=text,
            pos=(4, 50),
            font_size=10,
        )

    def set_active(self, active):
        if self.disabled or active == self.active:
            return
        self.active = active
        self.icon.scale = (1.5 if active else 1.0) * self.icon_default_scale
        self.r = self.r_on if active else self.r_off

    def set_disabled(self, disabled):
        if disabled == self.disabled:
            return
        self.disabled = disabled
        self.icon.opacity = 100 if disabled else 255
        if disabled:
            self.r = self.r_disabled
        else:
            self.set_active(self.active)

    def draw(self):
        self.r.draw()
        self.icon.draw()
        if self.label and not self.disabled:
            self.label.draw()



class Controller(object):
    def __init__(self, component):
        self.component = component
        self.icon = ControllerIcon(self.component.get_icon())

    def set_key(self, key_symbol):
        t = key.symbol_string(key_symbol)
        t = t.replace('_', ' ').strip()
        self.icon.set_label(t)

    def draw(self):
        self.icon.set_active(self.component.active)
        self.icon.set_disabled(not self.component.is_enabled())
        self.icon.draw()


class PressController(Controller):
    """Activate a component for as long as the key is held.

    """
    def on_press(self):
        self.component.set_active(True)

    def on_release(self):
        self.component.set_active(False)


class ToggleController(Controller):
    """Toggle a component on/off.

    """
    def on_press(self):
        active = self.component.is_active()
        self.component.set_active(not active)

    def on_release(self):
        pass


class OneTimeController(Controller):
    """Start a component, never stop it.

    """
    def on_press(self):
        active = self.component.is_active()
        if not active:
            self.component.set_active(True)
        self.icon.set_disabled(True)

    def on_release(self):
        pass


class NullController(Controller):
    """Doesn't do anything.

    This is used for keys that aren't bound to components.

    """
    def __init__(self):
        pass

    def noop(self, *args, **kwargs):
        """Don't do anything."""

    on_press = noop
    set_key = noop
    on_release = noop
    update = noop
    draw = noop
