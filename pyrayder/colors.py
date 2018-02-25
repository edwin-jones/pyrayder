"""This module defines color constants."""

from collections import namedtuple

Color = namedtuple('Color', 'r g b')

#bespoke colors
SKY_BLUE = Color(100, 149, 237)
CEILING_GRAY = Color(51, 51, 51)
FLOOR_GRAY = Color(102, 102, 102)

#standard colors
WHITE = Color(255, 255, 255)
BLACK = Color(0, 0, 0)
YELLOW = Color(255, 255, 0)
RED = Color(255, 0, 0)
GREEN = Color(0, 255, 0)
BLUE = Color(0, 0, 255)
PURPLE = Color(255, 0, 255)
ORANGE = Color(255, 128, 0)


def halve_color(color):
    """This method returns a color that is exactly half of what is passed in.
    
    For example white(255,255,255) would become grey(127,127,127)
    Use this function to lower the brightness of an existing color.
    """

    return  Color(int(color.r/2), int(color.g/2), int(color.b/2))
