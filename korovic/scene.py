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

from .components import Susie




class Scene(object):
    def __init__(self, world):
        Clouds.load()
        Stars.load()
        self.camera = Camera()
        self.background = GradientPainter(sky)
        self.clouds = Clouds()
        self.stars = Stars()
        self.horizon = HorizonPainter(HORIZON_LEVEL, (0.5, 0.8, 1))
        self.fgsea = ForegroundSeaPainter(SEA_LEVEL, (0.5, 0.8, 1), x=676)
        self.world = world
        self.lair = Sprite(loader.image('data/sprites/island-lair.png')) 
        self.hud = GameHud(world)
    
    def update(self, dt):
        self.world.update(dt)

    def draw(self):
        self.camera.track(self.world.squid)
        vp = self.camera.viewport()
        self.background.draw(vp)
        self.horizon.draw(vp)
        self.clouds.set_viewport(vp)
        self.stars.set_viewport(vp)

        with self.camera.modelview():
            self.stars.draw()
            self.clouds.draw()
            self.lair.draw()
            self.world.draw()

        self.fgsea.draw(vp)
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
            self.world.get_controller(controller).on_press()
            return EVENT_HANDLED


    def on_key_release(self, symbol, modifiers):
        """Pass the key release event to the appropriate controller.
        
        """
        if key._0 <= symbol <= key._9:
            controller = symbol - key._0
            self.world.get_controller(controller).on_release()
            return EVENT_HANDLED

    def stop(self):
        pass


class Editor(object):
    def __init__(self, window, squid):
        self.window = window
        self.squid = squid
        self.slots = squid.slots
        self.background = Sprite(loader.image('data/sprites/editor-bg.png'))
        #self.squid.attachments[0].selected = True
        self.editor = None
        self.scroll_state = 0
        self.hud = EditorHud(squid, 2000)
    
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

    def get_handlers(self):
        return {
            'on_draw': self.draw,
            'on_mouse_press': self.on_mouse_press,
            'on_mouse_scroll': self.on_mouse_scroll,
            'on_mouse_release': self.on_mouse_release,
            'on_mouse_drag': self.on_mouse_drag
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

    def stop(self):
        self.clear_editor()

    def on_mouse_press(self, x, y, button, modifiers):
        if x > SCREEN_SIZE[0] - self.hud.tile_size.x - 10:
            self.clear_editor()
            self.scroll_state = 1
            self.scroll_start = v(x, y)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if x > SCREEN_SIZE[0] - self.hud.tile_size.x - 10:
            self.hud.scroll_rows(scroll_y)
            return EVENT_HANDLED

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
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

        for b in self.hud.buttons():
            if mpos in b.rect:
                b.callback()
                return
            
        closest_dist = 1000
        closest = None

        for a in self.slots.components:
            dist = (a.position - mpos).length
            if dist < a.radius() and dist < closest_dist:
                closest = a
                closest_dist = dist

        if closest:
            self.set_editor(closest.editor())
        else:
            self.clear_editor()
