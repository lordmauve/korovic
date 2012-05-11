import pyglet.graphics
from pyglet import gl
import pyglet.text


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
