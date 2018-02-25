"""This module contains a type to store sprite information"""


class Sprite:
    """This class stores sprite information"""
    
    def __init__(self, sprite_index, map_position, distance_from_player):
        self.sprite_index = sprite_index
        self.map_position = map_position
        self.distance_from_player = distance_from_player
