from pyglet.sprite import Sprite

from .background import GradientPainter, sky
from .background import HorizonPainter, ForegroundSeaPainter

from .camera import Camera
from . import loader
from .constants import SEA_LEVEL, HORIZON_LEVEL

from .hud import GameHud
from .components import Susie




class Scene(object):
    def __init__(self, world):
        self.camera = Camera()
        self.background = GradientPainter(sky)
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

        with self.camera.modelview():
            self.lair.draw()
            self.world.draw()

        self.fgsea.draw(vp)
        self.hud.draw()


class Editor(object):
    def __init__(self, squid):
        self.squid = squid
        self.background = Sprite(loader.image('data/sprites/editor-bg.png'))
    
    def update(self, dt):
        pass

    def draw(self):
        self.background.draw()
        self.squid.draw()
