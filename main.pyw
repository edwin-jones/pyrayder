"""This is the main entry point for the program"""

from pyrayder.renderer import Renderer
from pyrayder.game import Game
from pyrayder.player import Player
from pyrayder.keyboard_input_handler import KeyboardInputHandler

import pyrayder.settings as settings


if __name__ == "__main__":

    renderer = Renderer()

    player = Player(settings.PLAYER_START_POSITION,
                    settings.PLAYER_START_DIRECTION, settings.PLAYER_START_CAMERA_PLANE)

    input_handler = KeyboardInputHandler()

    game = Game(renderer, player, input_handler)
    game.run()
