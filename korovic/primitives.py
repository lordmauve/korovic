import pyglet.graphics
from pyglet import gl
import pyglet.text


from .constants import SELECTED_COLOUR
from .camera import Rect
from . import loader
from .vector import v


def walk(list):
    """Flatten a list of vertices into a vertex list."""
    for i in list:
        for j in i:
            yield j


class Circle(object):
    def __init__(self, radius, centre=(0, 0)):
        self.radius = radius
        self.centre = v(centre)
        self._build()

    def _build(self):
        vs = []
        for deg in xrange(181):
            vs.append(self.centre + v(self.radius, 0).rotated(deg * 2))
        self.vs = list(walk(vs))
    
    def draw(self):
        pyglet.graphics.draw(len(self.vs) // 2, gl.GL_LINE_STRIP,
            ('v2f', self.vs),
        )


class Rectangle(object):
    def __init__(self, rect, colours):
        self.vertices = list(walk([rect.bl, rect.br, rect.tr, rect.tl]))
        if len(colours) == 1:
            colours = colours * 4
        elif len(colours) == 2:
            a, b = colours
            colours = [a, a, b, b]
        cl = len(colours[0])
        self.colours = list(walk(colours))
        self.vertex_list = pyglet.graphics.vertex_list(4,
            ('v2f', self.vertices),
            ('c%df' % cl, self.colours)
        )
        
    def draw(self):
        self.vertex_list.draw(gl.GL_QUADS)


class Protractor(object):
    """A circular display an angle.

    Users should be able to drag on the protractor to adjust the angle of the
    component.

    """
    def __init__(self, radius, centre=(0, 0), min_angle=0, max_angle=90, angle=None):
        self.circle = Circle(radius, centre)
        self.inner_circle = Circle(radius - 30, centre)
        self.min_angle = min_angle
        self.max_angle = max_angle
        self._build()
        self.label = Label(
            text='0deg',
            font_name='Atomic Clock Radio',
            font_size=12,
            color=(0, 255, 0, 255)
        )
        self.set_angle(angle)

    @property
    def centre(self):
        return self.circle.centre

    def set_angle(self, angle):
        self.angle = angle
        if self.angle is not None:
            self.label.document.text = '%ddeg' % self.angle

    def _build(self):
        vs = []
        def tick(angle, length):
            centre = self.circle.centre
            radius = self.circle.radius
            l2 = length // 2
            vs.extend([
                centre + v(radius - l2, 0).rotated(angle),
                centre + v(radius, 0).rotated(angle)
            ])

        tick(self.min_angle, 20)
        tick(self.max_angle, 20)

        next = self.min_angle - self.min_angle % 5 + 5
        for deg in xrange(next, self.max_angle, 5):
            if deg % 45 == 0:
                tick(deg, 14)
            else:
                tick(deg, 8)
        self.vs = list(walk(vs))
    
    def draw(self):
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glColor4f(*(list(SELECTED_COLOUR) + [0.5]))
        self.inner_circle.draw()
        gl.glColor3f(*SELECTED_COLOUR)
        self.circle.draw()
        pyglet.graphics.draw(len(self.vs) // 2, gl.GL_LINES,
            ('v2f', self.vs),
        )

        if self.angle is not None:
            centre = self.circle.centre
            radius = self.circle.radius
            l = 10
            avs = list(walk([
                centre + v(radius + 4, 0).rotated(self.angle),
                centre + v(radius + 4 + l , 0).rotated(self.angle)
            ]))
            pyglet.graphics.draw(2, gl.GL_LINES,
                ('v2f', avs),
            )
            pos = centre + v(radius + 6 + l , 0).rotated(self.angle)
            self.label.x, self.label.y = pos
            self.label.anchor_x = 'right' if self.label.x < centre.x else 'left'
            self.label.draw()
            self.label.draw()  # Draw twice because it doesn't come out well


class Label(pyglet.text.Label):
    DEFAULTS = dict(
        text='Label',
        font_name='Atomic Clock Radio',
        font_size=16,
        x=0,
        y=0
    )
    def __init__(self, pos=None, **kwargs):
        params = self.DEFAULTS.copy()
        params.update(kwargs)
        if pos:
            x, y = pos
            params.update({
                'x': x,
                'y': y
            })
        super(Label, self).__init__(**params)


class SpeechBubble(object):
    tail = None

    PADDING = 30, 15

    @classmethod
    def load(cls):
        cls.tail = loader.image('data/cutscene/bubble-tail.png')

    def __init__(self, pos, text, width=None):
        if self.tail is None:
            self.load()
        self.pos = v(pos)
        self.text = text
        self.width = width
        self.build()

    def build(self):
        off = v(-29, 73)
        pad_x, pad_y = self.PADDING
        self.label = Label(
            pos=self.pos + off + v(self.PADDING),
            color=(0, 0, 0, 255),
            text=self.text,
            font_name="Comic Sans MS",
            multiline=bool(self.width),
            anchor_y='bottom',
            width=self.width
        )
        self.label.content_valign = 'bottom'
        w = self.label.content_width
        h = self.label.content_height
        bl = self.pos + off 
        tr = bl + v(w + pad_x * 2, h + pad_y * 2)
        self.rect = Rect(bl, tr)

        self.rectangle = Rectangle(self.rect, [(1.0, 1.0, 1.0, 1.0)])

        self.vertices = list(walk([self.rect.bl, self.rect.br, self.rect.tr, self.rect.tl, self.rect.bl]))
        self.vertex_list = pyglet.graphics.vertex_list(5,
            ('v2f', self.vertices),
        )
        self.tail = pyglet.sprite.Sprite(self.tail, x=self.pos.x, y=self.pos.y)
        
    def draw(self):
        self.rectangle.draw()
        gl.glColor4f(0.5, 0.5, 0.5, 1)
        gl.glLineWidth(2)
        self.vertex_list.draw(gl.GL_LINE_STRIP) 
        gl.glLineWidth(1)
        gl.glColor4f(1, 1, 1, 1)
        self.tail.draw()
        self.label.draw()
