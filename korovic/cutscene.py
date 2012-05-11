import pyglet.sprite
from .primitives import SpeechBubble

from .vector import v
from . import loader


class Cutscene(object):
    def __init__(self, path):
        self.t = 0
        self.steps = []
        self.path = path
        self.images = {}
        self.sprites = {}
        self.bubbles = []
        self.interpolators = []
        self.delay = 0
        self.current = 0
    
    def load_image(self, img):
        try:
            return self.images[img]
        except KeyError:
            i = loader.image(self.path + img + '.png')
            self.images[img] = i
            return i

    def step(self, func):
        self.steps.append(func)

    def background(self, img):
        """Set the background."""
        self.sprite('background', (0, 0), img, -1e9)

    def pause(self, t):
        """Pause for a given amount of time."""
        @self.step
        def _pause():
            self.delay += t

    def sprite(self, name, pos, img, z=0):
        """Show a sprite at pos"""
        i = self.load_image(img)
        x, y = pos
        @self.step
        def _sprite():
            s = pyglet.sprite.Sprite(i, x=x, y=y)
            s.z = z
            self.sprites['name'] = s

    def say(self, name, text, duration=5, delay=True):
        """Create a speech bubble above a sprite"""
        @self.step
        def _say():
            s = self.sprites[name]
            x = s.pos + s.width * 0.5
            y = s.pos + s.height + 25
            b = SpeechBubble(v(x, y), text)
            b.expire = self.t + duration
            self.bubbles.append(b)
            if delay:
                self.delay += duration


    def remove_sprite(self, name):
        """Hide the sprite `name`"""
        @self.step
        def _remove_sprite():
            self.sprites.pop(name.delete())

    def replace_sprite(self, name, img):
        """Replace the image of sprite name"""
        i = self.load_image(img)
        @self.step
        def _replace_sprite():
            self.sprites[name].img = i

    def animate_sprite(self, name, imgs, framerate=2):
        """Replace a sprite with animated frames."""
        #TODO

    def move_sprite(self, name, pos, duration=1):
        """Move name to pos"""
        def interpolator():
            s = self.sprites[name]
            t = 0
            start = v(s.position)
            end = v(pos)
            while t < duration:
                t += yield
                frac = min(1.0, float(t) / duration)
                s.position = (1 - frac) * start + frac * end
            s.position = pos

        @self.step
        def _move_sprite():
            self.interpolators.append(interpolator())

    def do_delay(self, dt):
        if self.delay:
            self.delay -= dt
            if self.delay > 0:
                return True
            else:
                self.delay = 0
        return False

    def do_interpolators(self, dt):
        interpolators = []
        for s in self.interpolators:
            try:
                s.next(dt)
            except StopIteration:
                pass
            else:
                interpolators.append(s)
        self.interpolators = []

    def do_bubbles(self):
        self.bubbles = [b for b in self.bubbles if b.expiry < self.t]

    def update(self, dt):
        self.t += dt
        self.do_interpolators(dt)
        if self.do_delay(dt):
            return
        self.run_steps()

    def run_steps(self):
        while self.delay == 0 and not self.is_finished():
            step = self.steps[self.current]
            self.current += 1
            step()

    def draw(self):
        sprites = self.sprites.values()
        sprites.sort(key=lambda s: s.z)
        for s in sprites:
            s.draw()
        for s in self.bubbles:
            s.draw()

    def is_finished(self):
        return self.current < len(self.steps)

    def rewind(self):
        self.current = 0

    def __del__(self):
        for s in self.sprites.values():
            s.delete()
        del(self.sprites)


def intro():
    c = Cutscene('data/')
    c.set_background('cutscene/aerial')
    c.pause(3)
    c.set_background('cutscene/beach')
    c.sprite('korovic', (52, 35), 'cutscene/korovic-elated')
    c.sprite('susie', (55, 10), 'cutscene/susie-standing')
    c.pause(2)
    c.say('korovic', 'At last!', duration=2)
    c.say('korovic', 'My atomic super squid is complete!', duration=2)
