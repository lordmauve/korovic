import pyglet
from pyglet import gl
from pyglet.window import key
from pyglet.event import EVENT_HANDLED
import pyglet.clock

from .world import World
from .scene import Scene, Editor, TitleScreen
from .cutscene import intro, level_start


from .constants import SCREEN_SIZE, TARGET_FPS, NAME


class Game(object):
    def start(self, level=1):
        w, h = SCREEN_SIZE
        self.window = pyglet.window.Window(width=w, height=h, caption=NAME)
        self.game = self.scene = Scene(self, level=level)
        self.squid = self.game.world.squid
        self.editor = Editor(self, self.game.world)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDepthFunc(gl.GL_ALWAYS)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glTranslatef(0, 0, -0.5)
        gl.glEnable(gl.GL_ALPHA_TEST)
        gl.glAlphaFunc(gl.GL_GREATER, 0)

        self.fps_display = pyglet.clock.ClockDisplay()

        pyglet.clock.schedule_interval(self.update, 1/TARGET_FPS)
        pyglet.clock.set_fps_limit(TARGET_FPS)
        self.window.push_handlers(
            on_key_press=self.on_key_press
        )
        self.window.push_handlers()
        if level == 1:
            self.title_screen()
        else:
            self.next_level()

        pyglet.app.run()

    def start_scene(self, scene):
        self.scene.stop()
        self.window.pop_handlers()
        self.scene = scene
        self.window.push_handlers(**scene.get_handlers())
        self.scene.start()

    def next_level(self):
        start = level_start(self.game.level, self.game.world.title, self, self.editor)
        self.start_scene(start)

    def title_screen(self):
        self.start_scene(TitleScreen(self))

    def start_intro(self):
        start = level_start(self.game.level, self.game.world.title, self, self.editor)
        introduction = intro(self, start)
        self.start_scene(introduction)

    def start_editor(self):
        self.start_scene(self.editor)

    def start_game(self):
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
        if symbol == key.ESCAPE and self.scene is self.game:
            self.toggle_editor()
            return EVENT_HANDLED
