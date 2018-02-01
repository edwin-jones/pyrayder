"""This module contains settings and config for the main game"""

import math
import colors

from pygame.math import Vector2


TARGET_FPS = 60

# flip grid 90 left for 'real' map. +y is up, +x is right.
MAP = (
    (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    (1, 2, 0, 0, 0, 0, 0, 0, 0, 1),
    (1, 0, 0, 0, 0, 3, 0, 0, 0, 1),
    (1, 0, 0, 0, 0, 0, 0, 0, 0, 1),
    (1, 0, 0, 0, 2, 3, 0, 0, 0, 1),
    (1, 0, 0, 0, 5, 6, 0, 0, 0, 1),
    (1, 0, 0, 0, 0, 0, 0, 0, 0, 1),
    (1, 0, 0, 0, 0, 0, 0, 0, 4, 1),
    (1, 3, 3, 0, 0, 0, 0, 0, 4, 1),
    (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
)

# rotate the grid 90 degrees right to fix the issue.
# You can find out how this works here: https://stackoverflow.com/questions/8421337
MAP = tuple(zip(*MAP[::-1]))

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
HALF_SCREEN_HEIGHT = SCREEN_HEIGHT / 2

ROTATION_SPEED = 2.5  # rotation speed is defined degrees per frame
MOVE_SPEED = 0.05  # move speed is defined as squares per frame.

SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

PLAYER_START_POSITION = Vector2(3, 3)
PLAYER_START_DIRECTION = Vector2(1, 0)

# 66 degree fov. Length 1 would be a 90 degree fov, 0.5 would be 45. Camera plane must be perpendicular to player direction!
PLAYER_START_CAMERA_PLANE = Vector2(0, -0.66)

WALL_PALETTE = [colors.BLACK, colors.WHITE, colors.RED, colors.GREEN,
                colors.BLUE, colors.YELLOW, colors.PURPLE, colors.ORANGE]
