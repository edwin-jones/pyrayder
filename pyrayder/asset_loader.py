"""This is a helper module to load assets such as tectures etc."""

import os
import pygame


def get_textures(texture_folder):
    """A simple way to load game textures from a folder"""

    textures = []

    for file in os.listdir(texture_folder):
        if file.endswith(".png"):
            path = os.path.join(texture_folder, file)
            texture = pygame.image.load(path)
            textures.append(texture)

    return textures
