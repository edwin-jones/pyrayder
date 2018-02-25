"""This module contains definitions of vector objects"""

import math


class Player:
    """A basic player class"""

    def __init__(self, position, direction, camera_plane):
        self.position = position
        self.direction = direction
        self.camera_plane = camera_plane

    def rotate(self, angle):
         """Rotate the player by n radians"""
         # both camera direction and camera plane must be rotated together
         self.direction = self.direction.rotate(angle)
         self.camera_plane = self.camera_plane.rotate(angle)

    def get_rotation(self):
        """Get the current rotation of the player in radians"""
        return math.atan2(self.direction.y, self.direction.x)

    def get_rotation_degrees(self):
        """Get the current rotation of the player in degrees, between 0 and 360"""
        temp = self.get_rotation()
        temp = temp * 57.2958  # Convert to degrees
        if (temp < 0):
            temp += 360  # Make sure it's in the expected range

        return temp
