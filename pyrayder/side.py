"""This module defines an enum for marking which side of a wall has been hit"""

from enum import Enum


class Side(Enum):
    """This enum is for marking which side of a wall has been hit"""
    LeftOrRight = 0
    TopOrBottom = 1
