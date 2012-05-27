
import pyglet.clock
from pyglet.sprite import Sprite
from pyglet.window import key
from pyglet.event import EVENT_HANDLED

from .vector import v

from .background import GradientPainter, sky
from .background import Clouds, Stars
from .background import HorizonPainter, ForegroundSeaPainter

from .camera import Camera
from . import loader
from .constants import SEA_LEVEL, HORIZON_LEVEL, SCREEN_SIZE

from .editor_hud import EditorHud
from .hud import GameHud
from .world import World
from .controllers import NullController
from .primitives import SpeechBubble, Button, Label


class Scene(object):
    def __init__(self, game, level=1):
        self.game = game
        Clouds.load()
        Stars.load()
        self.level = level
        self.world = World('level%d' % self.level)
        self.camera = Camera()
        self.background = GradientPainter(sky)
        self.clouds = Clouds()
        self.stars = Stars()
        self.horizon = HorizonPainter(HORIZON_LEVEL, (0.5, 0.8, 1))
        self.fgsea = ForegroundSeaPainter(SEA_LEVEL, (0.5, 0.8, 1))
        self.hud = GameHud(self.world)

        self.world.set_handler('on_crash', self.on_crash)
        self.world.set_handler('on_goal', self.on_goal)

    def on_goal(self):
        pyglet.clock.schedule_once(self.on_next_level, 3)

    def on_crash(self, distance):
        pyglet.clock.schedule_once(self.on_death, 3)

    def on_next_level(self, dt):
        self.level += 1
        try:
            self.world.load('level%d' % self.level)
        except IOError:
            self.world.load('freeflight')
        self.game.next_level()

    def on_death(self, dt):
        self.game.start_editor()

    def update_controllers(self):
        cs = self.world.controllers()
        for i, c in enumerate(cs):
            c.set_key(key._0 + (i + 1) % 10)
        self.controllers = cs
        self.hud.set_controllers(cs)

    def get_controller(self, num):
        cs = self.controllers
        try:
            return cs[(num - 1) % 10]
        except IndexError:
            return NullController()
    
    def update(self, dt):
        self.world.update(dt)

    def draw(self):
        self.camera.track(self.world.squid, max_x=self.world.width)
        vp = self.camera.viewport()
        self.background.draw(vp)
        self.horizon.draw(vp)
        self.clouds.set_viewport(vp)
        self.stars.set_viewport(vp)
        self.fgsea.draw(vp)

        with self.camera.modelview():
            self.stars.draw()
            self.clouds.draw()
            self.world.draw(vp)
        self.hud.draw()

    def get_handlers(self):
        return {
            'on_key_press': self.on_key_press,
            'on_key_release': self.on_key_release,
            'on_draw': self.draw
        }

    def on_key_press(self, symbol, modifiers):
        if key._0 <= symbol <= key._9:
            controller = symbol - key._0
            self.get_controller(controller).on_press()
            return EVENT_HANDLED


    def on_key_release(self, symbol, modifiers):
        """Pass the key release event to the appropriate controller.
        
        """
        if key._0 <= symbol <= key._9:
            controller = symbol - key._0
            self.get_controller(controller).on_release()
            return EVENT_HANDLED

    def start(self):
        self.world.reset()
        self.world.squid.stop_all()
        self.update_controllers()

    def stop(self):
        self.world.clear_particles()


class Editor(object):
    def __init__(self, game, world):
        self.game = game
        self.window = game.window
        self.world = world
        self.squid = world.squid
        self.slots = self.squid.slots
        self.background = Sprite(loader.image('data/sprites/editor-bg.png'))
        #self.squid.attachments[0].selected = True
        self.editor = None
        self.scroll_state = 0
        self.bubble = None
        self.hud = EditorHud(self.squid, max_money=world.money)
    
    def update(self, dt):
        if self.editor:
            if self.editor.component not in self.slots.components:
                self.editor = None

    def draw(self):
        self.background.draw()
        if self.editor:
            self.squid.draw_selected(editor=self.editor)
        else:
            self.squid.draw()
        self.hud.draw()
        if self.bubble:
            self.bubble.draw()

    def get_handlers(self):
        return {
            'on_draw': self.draw,
            'on_mouse_press': self.on_mouse_press,
            'on_mouse_scroll': self.on_mouse_scroll,
            'on_mouse_release': self.on_mouse_release,
            'on_mouse_drag': self.on_mouse_drag,
            'on_mouse_motion': self.on_mouse_motion
        }

    def set_editor(self, editor):
        if self.editor:
            self.window.pop_handlers()
        self.editor = editor
        if editor:
            self.window.push_handlers(**editor.get_handlers())

    def clear_editor(self):
        if self.editor:
            self.window.pop_handlers()
            self.editor = None

    def start(self):
        self.squid.reset(position=(255, 145))
        self.hud = EditorHud(self.squid, max_money=self.world.money)

    def stop(self):
        self.clear_editor()

    def on_mouse_press(self, x, y, button, modifiers):
        if x > SCREEN_SIZE[0] - self.hud.tile_size.x - 10:
            self.clear_editor()
            self.scroll_state = 1
            self.scroll_start = v(x, y)
        else:
            self.scroll_state = 0
            if not self.editor:
                self.find_editor(x, y)
                if self.editor:
                    return self.editor.on_mouse_press(x, y, button, modifiers)
                return EVENT_HANDLED

    def on_mouse_motion(self, x, y, dx, dy):
        mpos = v(x, y)
        for b in self.buttons():
            if b.tooltip and mpos in b.rect:
                self.bubble = SpeechBubble((90, 223), text=b.tooltip, width=300)
                break
        else:
            self.bubble = None

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if x > SCREEN_SIZE[0] - self.hud.tile_size.x - 10:
            self.hud.scroll_rows(scroll_y)
            return EVENT_HANDLED

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if not self.scroll_state:
            return

        if self.scroll_state == 2:
            self.hud.scroll_by(-dy)
            return EVENT_HANDLED

        p = v(x, y) - self.scroll_start
        if p.length2 > 64:
            self.scroll_state = 2
            self.hud.scroll_by(-p.y)
            return EVENT_HANDLED
    
    def on_mouse_release(self, x, y, button, modifiers):
        if self.scroll_state == 2:
            self.scroll_state = 0
            return EVENT_HANDLED
        mpos = v(x, y)

        if not self.editor:
            for b in self.buttons():
                if mpos in b.rect:
                    b.callback()
                    return
        else:
            self.find_editor(x, y)

    def buttons(self):
        from .editor_hud import Button
        return list(self.hud.buttons()) + [
            Button(self.hud.startbutton.rect, self.game.start_game, 'You are ready to fly already?')
        ]

    def find_editor(self, x, y):
        mpos = v(x, y)
        closest_dist = 1000
        closest = None

        for a in self.slots.components:
            r = min(a.radius(), 70)
            dist = (a.position - mpos).length
            if dist < r and dist < closest_dist:
                closest = a
                closest_dist = dist

        if closest:
            self.set_editor(closest.editor())
        else:
            self.clear_editor()


class TitleScreen(object):
    def __init__(self, game):
        self.game = game
        Clouds.load()
        self.camera = Camera()
        self.background = GradientPainter(sky)
        self.clouds = Clouds()
        self.logo = loader.image('data/sprites/logo.png')
        self.logo.anchor_x = int(self.logo.width * 0.5)

        center = int(SCREEN_SIZE[0] * 0.5)
        self.logo_sprite = pyglet.sprite.Sprite(self.logo, x=center, y=200)
        self.startbutton = Button((center, 100), 'Start', align='center')
        self.attribution = Label((center, 20), text='A Pyweek 14 game by Daniel Pope', font_name='MS Comic Sans', anchor_x='center', color=(0, 0, 0, 200), font_size=10)
        self.t = 0

    def start(self):
        pass

    def stop(self):
        pass

    def get_handlers(self):
        return {
            'on_draw': self.draw,
            'on_mouse_press': self.on_mouse_press,
        }

    def on_mouse_press(self, x, y, button, modifiers):
        p = v(x, y)
        if p in self.startbutton.rect:
            self.game.start_intro()

    def update(self, dt):
        self.t += dt
        self.camera.set_pos(v(self.t * 200, 800))

    def draw(self):
        w, h = SCREEN_SIZE
        vp = self.camera.viewport()
        self.background.draw(vp)
        self.clouds.set_viewport(vp)

        with self.camera.modelview():
            self.clouds.draw()

        self.attribution.draw()
        self.startbutton.draw()
        self.logo_sprite.draw()
