from pkg_resources import resource_stream
import pygame.mixer

pygame.mixer.init()


def load_sound(name):
    f = resource_stream(__name__, name)
    return pygame.mixer.Sound(f)
