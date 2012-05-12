import pyglet.sprite
from pyglet.event import EVENT_HANDLED
from pyglet.window import key
from .primitives import SpeechBubble

from .vector import v
from . import loader

PATH = 'data/'


class Cutscene(object):
    def __init__(self, game, next):
        self.game = game
        self.next = next
        self.t = 0
        self.steps = []
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
            i = loader.image(PATH + img + '.png')
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
            if name in self.sprites:
                self.sprites[name].delete()
            s = pyglet.sprite.Sprite(i, x=x, y=y)
            s.z = z
            self.sprites[name] = s

    def bubble(self, pos, text, duration=3.5, delay=False):
        """Create a speech bubble above a sprite"""
        @self.step
        def _bubble():
            p = v(pos)
            b = SpeechBubble(p, text, tail=False)
            b.expiry = self.t + duration
            self.bubbles.append(b)
            if delay:
                self.delay += duration

    def say(self, name, text, duration=3.5, delay=True):
        """Create a speech bubble above a sprite"""
        @self.step
        def _say():
            s = self.sprites[name]
            pos = v(s.position) + v(int(s.width * 0.5), int(s.height + 25))
            b = SpeechBubble(pos, text)
            b.expiry = self.t + duration
            self.bubbles.append(b)
            if delay:
                self.delay += duration

    def remove_sprite(self, name):
        """Hide the sprite `name`"""
        @self.step
        def _remove_sprite():
            self.sprites.pop(name).delete()

    def replace_sprite(self, name, img):
        """Replace the image of sprite name"""
        i = self.load_image(img)
        @self.step
        def _replace_sprite():
            self.sprites[name].image = i

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
                t += (yield)
                frac = min(1.0, float(t) / duration)
                s.position = (1 - frac) * start + frac * end
            s.position = pos

        @self.step
        def _move_sprite():
            i = iter(interpolator())
            i.next()
            self.interpolators.append(i)

    def zoom_sprite(self, name, scale, duration=1):
        """Move name to pos"""
        def interpolator():
            s = self.sprites[name]
            t = 0
            start = s.scale
            end = scale
            while t < duration:
                t += (yield)
                frac = min(1.0, float(t) / duration)
                s.scale = (1 - frac) * start + frac * end
            s.scale = end

        @self.step
        def _zoom_sprite():
            i = iter(interpolator())
            i.next()
            self.interpolators.append(i)

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
                s.send(dt)
            except StopIteration:
                pass
            else:
                interpolators.append(s)
        self.interpolators = interpolators

    def expire_bubbles(self):
        self.bubbles = [b for b in self.bubbles if b.expiry > self.t]

    def update(self, dt):
        self.t += dt
        self.do_interpolators(dt)
        self.expire_bubbles()
        if self.do_delay(dt):
            return
        self.run_steps()

    def run_steps(self):
        while self.delay == 0 and not self.is_finished():
            step = self.steps[self.current]
            self.current += 1
            step()
        if self.is_finished():
            self.game.start_scene(self.next)

    def draw(self):
        sprites = self.sprites.values()
        sprites.sort(key=lambda s: s.z)
        for s in sprites:
            s.draw()
        for s in self.bubbles:
            s.draw()

    def is_finished(self):
        return (
            self.current >= len(self.steps) and
            self.delay == 0 and
            not self.interpolators
        )

    def start(self):
        self.current = 0

    def stop(self):
        """Don't need to to anything."""

    def __del__(self):
        for s in self.sprites.values():
            s.delete()
        del(self.sprites)

    def get_handlers(self):
        return {
            'on_draw': self.draw,
            'on_key_press': self.on_key_press,
        }

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.game.start_scene(self.next)
            return EVENT_HANDLED
        elif symbol == key.SPACE:
            self.t += self.delay
            self.delay = 0


def intro(game, next):
    c = Cutscene(game, next)
    c.background('cutscene/aerial')
    c.pause(1)
    c.bubble((62, 471), 'On a remote island...', duration=8)
    c.pause(3)
    c.bubble((420, 62), '...somewhere in the Pacific...', duration=5)
    c.pause(5)
    c.background('cutscene/beach')
    c.sprite('korovic', (52, 35), 'cutscene/korovic-standing')
    c.sprite('susie', (55, 6), 'cutscene/susie-standing')
    c.pause(2)
    c.replace_sprite('korovic', 'cutscene/korovic-elated')
    c.say('korovic', 'At last!')
    c.say('korovic', 'You are komplete, mein atomic super squid!')
    c.replace_sprite('korovic', 'cutscene/korovic-standing')
    c.say('korovic', 'I vill call you Susie.')
    c.pause(1.5)
    c.say('korovic', 'Who\'s a cute little atomic squid?')
    c.sprite('susie-speak', (233, 95), 'cutscene/blup')
    c.pause(2)
    c.remove_sprite('susie-speak')
    c.replace_sprite('korovic', 'cutscene/korovic-elated')
    c.say('korovic', 'Yes, you are!')
    c.say('korovic', 'You are my greatest achievement.')
    c.say('korovic', 'Now we vill be able to take over ze world!', delay=False)
    c.pause(0.5)
    c.sprite('susie-speak', (233, 95), 'cutscene/squee')
    c.pause(2)
    c.remove_sprite('susie-speak')
    c.pause(2)
    c.replace_sprite('korovic', 'cutscene/korovic-pointing')
    c.say('korovic', 'Now svim, my fantastisch cephalapod!', delay=False)
    c.pause(1)
    c.move_sprite('susie', (331, 6), duration=5)
    c.pause(2.5)
    c.replace_sprite('korovic', 'cutscene/korovic-elated')
    c.say('korovic', 'Lay vaste to ze cities and level ze towns!')
    c.replace_sprite('korovic', 'cutscene/korovic-standing')
    c.pause(1)
    c.replace_sprite('susie', 'cutscene/susie-dipping')
    c.pause(1)
    c.sprite('susie-speak', (515, 95), 'cutscene/exclamation')
    c.pause(1)
    c.remove_sprite('susie-speak')
    c.replace_sprite('susie', 'cutscene/susie-puffing1')
    c.pause(0.5)
    c.replace_sprite('susie', 'cutscene/susie-puffing2')
    c.say('korovic', 'Ah...!')
    c.say('korovic', 'I vos afraid of zis.')
    c.say('korovic', 'It vos a danger of ze atomicisink process.')
    c.say('korovic', 'You may vell be allergic to SALT WATER.')
    c.pause(2)
    c.say('korovic', 'No matter. Ve vill find another vay!')
    return c
