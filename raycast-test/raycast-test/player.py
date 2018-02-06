"""This module contains definitions of vector objects"""

import math

class Player:
    """A basic player class"""

    def __init__(self, position, direction, camera_plane):
        self.position = position
        self.direction = direction
        self.camera_plane = camera_plane

    def get_rotation(self):
        return math.atan2(self.direction.y, self.direction.x)

    def __repr__(self):
        return 'Player with position x:{} y:{}'.format(self.position.x, self.position.y)
