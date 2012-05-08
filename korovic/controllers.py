"""Classes for mapping input to control of components.
"""

class PressController(object):
    """Activate a component for as long as the key is held.

    """
    def __init__(self, component):
        self.component = component

    def on_press(self):
        self.component.set_active(True)

    def on_release(self):
        self.component.set_active(False)


class ToggleController(object):
    """Toggle a component on/off.

    """
    def __init__(self, component):
        self.component = component

    def on_press(self):
        active = self.component.is_active()
        self.component.set_active(not active)

    def on_release(self):
        pass


class OneTimeController(object):
    """Start a component, never stop it.

    """
    def __init__(self, component):
        self.component = component

    def on_press(self):
        active = self.component.is_active()
        if not active:
            self.component.set_active(True)

    def on_release(self):
        pass


class NullController(object):
    """Doesn't do anything.

    This is used for keys that aren't bound to components.

    """
    def on_press(self):
        """Don't do anything."""

    def on_release(self):
        """Don't do anything."""

    def update(self, dt):
        """Don't do anything."""

