import math

from .base import Component
from .squid import Slot

from ..editor import AngleEditor


class FuelTank(Component):
    abstract = True
    slot_mask = Slot.TOP | Slot.BOTTOM
    
    angles = {
        Slot.TOP: math.pi,
        Slot.BOTTOM: 0
    }

    @property
    def angle(self):
        return self.angles[self.slot.flags]


class LargeFuelTank(FuelTank):
    MASS = 80
    CAPACITY = 75


class SmallFuelTank(FuelTank):
    MASS = 30
    CAPACITY = 25
