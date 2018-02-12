"""This is the main entry point for the program"""

from renderer import Renderer
from game import Game
from player import Player
from keyboard_input_handler import KeyboardInputHandler

import settings as settings


if __name__ == "__main__":

    renderer = Renderer()

    player = Player(settings.PLAYER_START_POSITION,
                    settings.PLAYER_START_DIRECTION, settings.PLAYER_START_CAMERA_PLANE)

    input_handler = KeyboardInputHandler()

    game = Game(renderer, player, input_handler)
    game.run()
