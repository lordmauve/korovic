import pyglet
from pyglet.window import key
from pyglet.event import EVENT_HANDLED

from .world import World
from .scene import Scene, Editor


from .constants import SCREEN_SIZE, TARGET_FPS, NAME


class Game(object):
    def start(self):
        w, h = SCREEN_SIZE
        self.window = pyglet.window.Window(width=w, height=h, caption=NAME)
        self.world = World()
        self.squid = self.world.squid
        self.game = self.scene = Scene(self.world)
        self.editor = Editor(self.window, self.squid)

        self.fps_display = pyglet.clock.ClockDisplay()

        pyglet.clock.schedule_interval(self.update, 1/TARGET_FPS)
        self.window.push_handlers(
            on_key_press=self.on_key_press
        )
        self.window.push_handlers()
        self.start_game()

        pyglet.app.run()

    def start_scene(self, scene):
        self.scene.stop()
        self.window.pop_handlers()
        self.scene = scene
        self.window.push_handlers(**scene.get_handlers())

    def start_editor(self):
        self.squid.position = (285, 150)
        self.squid.rotation = 0
        self.squid.body.velocity = (0, 0)
        self.start_scene(self.editor)

    def start_game(self):
        self.squid.position = (150, 200)
        self.start_scene(self.game)

    def toggle_editor(self):
        if isinstance(self.scene, Editor):
            self.start_game()
        else:
            self.start_editor()

    def update(self, dt):
        self.scene.update(dt)

    def on_key_press(self, symbol, modifiers):
        """Handle key press:

        - handle global keys
        - pass the key event to the appropriate controller.

        """
        if symbol == key.F12:
            from .screenshot import take_screenshot
            take_screenshot(self.window)
            return EVENT_HANDLED
        if symbol == key.F2:
            self.toggle_editor()
            return EVENT_HANDLED
