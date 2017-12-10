import pygame
import os

class TextureLoader(object):
    """A simple way to load game textures"""
    def __init__(self, texture_folder):
        self.textures = []

        for file in os.listdir(texture_folder):
            if file.endswith(".png"):
                path = os.path.join(texture_folder, file)
                print(path)
                texture = pygame.image.load(path)
                self.textures.append(texture)

    def get_textures(self):
        return self.textures