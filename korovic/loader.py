import pyglet.resource
from pkg_resources import resource_stream


class Loader(pyglet.resource.Loader):
    def file(self, name, mode='rb'):
        assert mode == 'rb', "Resource files are read-only."
        return resource_stream(__name__, name)


loader = Loader()
image = loader.image
texture = loader.texture
file = loader.file
add_font = loader.add_font
