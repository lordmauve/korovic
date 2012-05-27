"""Monkey patch pyglet to pad the texture atlas to remove adjacency artifacts.

Taken from http://markmail.org/message/qn65kjlieq6n333k
"""
import pyglet.image.atlas


def _texture_atlas_add(self, img):
    pad = 1
    x, y = self.allocator.alloc(img.width + pad * 2, img.height + pad * 2)
    self.texture.blit_into(img, x + pad, y + pad, 0)
    region = self.texture.get_region(x + pad, y + pad, img.width, img.height)
    return region

pyglet.image.atlas.TextureAtlas.add = _texture_atlas_add
