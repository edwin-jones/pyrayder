"""This type handles sprite information and logic"""


class Sprite:
    def __init__(self, sprite_index, map_position, distance_from_player):
        self.sprite_index = sprite_index
        self.map_position = map_position
        self.distance_from_player = distance_from_player
