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

    def get_rotation_degrees(self):
        temp = self.get_rotation()
        temp = temp * 57.2958  # Convert to degrees
        if (temp < 0):
            temp += 360  # Make sure its in proper range

        return temp

    def __repr__(self):
        return 'Player with position x:{} y:{}'.format(self.position.x, self.position.y)
