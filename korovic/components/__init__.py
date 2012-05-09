from .base import Component
from .squid import *
from .engines import *
from .wings import *


def load_all():
    for obj in globals().values():
        if (type(obj) is type and
            issubclass(obj, Component) and
            not obj.__dict__.get('abstract')):
            obj.load()
