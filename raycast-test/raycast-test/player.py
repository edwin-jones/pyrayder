"""This module contains definitions of vector objects"""

class Player(object):
    """A basic player class"""
    def __init__(self, position, direction, camera_plane):
        self.position = position
        self.direction = direction
        self.camera_plane = camera_plane
        self.rotation = 0
        self.camera_rotation = 90

    def __repr__(self):
        return 'Player with position x:{} y:{}'.format(self.position.x, self.position.y)
