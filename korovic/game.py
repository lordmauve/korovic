import pyglet
from pyglet import gl
from pyglet.window import key

from .world import World
from .scene import Scene


from .constants import SCREEN_SIZE, TARGET_FPS, NAME


class Game(object):
    def start(self):
        w, h = SCREEN_SIZE
        self.window = pyglet.window.Window(width=w, height=h, caption=NAME)
        self.world = World()
        self.scene = Scene(self.world)

        self.fps_display = pyglet.clock.ClockDisplay()

        pyglet.clock.schedule_interval(self.update, 1/TARGET_FPS)
        self.window.set_handlers(
            on_draw=self.draw,
            on_key_press=self.on_key_press,
            on_key_release=self.on_key_release
        )

        pyglet.app.run()

    def draw(self):
        self.scene.draw()

    def update(self, dt):
        self.world.update(dt)

    def on_key_press(self, symbol, modifiers):
        """Handle key press:

        - handle global keys
        - pass the key event to the appropriate controller.

        """
        if symbol == key.F12:
            from .screenshot import take_screenshot
            take_screenshot(self.window)
            return
        if key._0 <= symbol <= key._9:
            controller = symbol - key._0
            self.world.get_controller(controller).on_press()

    def on_key_release(self, symbol, modifiers):
        """Pass the key release event to the appropriate controller.
        
        """
        if key._0 <= symbol <= key._9:
            controller = symbol - key._0
            self.world.get_controller(controller).on_release()

