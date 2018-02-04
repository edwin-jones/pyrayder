# inspiration lovingly taken from here http://lodev.org/cgtutor/raycasting.html
# and here https://www.essentialmath.com/GDC2012/GDC2012_JMV_Rotations.pdf (see 2D vec rotations)
# and here https://github.com/Mekire/pygame-raycasting-experiment

import math
import pygame
import settings

from pygame.math import Vector2
from side import Side

class Game:
    """primary game engine"""

    """To rotate a vector, multiply it with the rotation matrix
    [ cos(a) -sin(a) ]
    [ sin(a)  cos(a) ]"""

    def __init__(self, renderer, player):
        self.renderer = renderer
        self.player = player


    def handle_input(self, player):
        """This function handles control input for this program"""

        for event in pygame.event.get():
            # quit if user presses exit
            if event.type == pygame.QUIT:
                self.running = False
                return

        pressed = pygame.key.get_pressed()

        if pressed[pygame.K_ESCAPE]:
            self.running = False
            return

        # handle movement

            #forward and backward
        if pressed[pygame.K_UP]:

            # very basic collision checking by figuring out where will be IF we move forward
            # and checking to see if that position is inside a map square with something in it we don't want to walk through.
            # We have to cut out the decimal part of the result with math.floor because the 2D map array is accessed by integer/whole number index.
            new_position = player.position + player.direction
            x = math.floor(new_position.x)
            y = math.floor(new_position.y)

            if settings.MAP[x][y] < 1:
                player.position += player.direction * settings.MOVE_SPEED

        if pressed[pygame.K_DOWN]:

            # same basic collision check as above, just in reverse because we are trying to move backwards.
            new_position = player.position - player.direction
            x = math.floor(new_position.x)
            y = math.floor(new_position.y)

            if settings.MAP[x][y] < 1:
                player.position -= player.direction * settings.MOVE_SPEED

        # strafe left and right
        if pressed[pygame.K_a]:
            player.position -= player.camera_plane * settings.MOVE_SPEED

        if pressed[pygame.K_d]:
            player.position += player.camera_plane * settings.MOVE_SPEED

            # rotate left and right
        # note, to rotate a vector a by an angle to become vector r(a):
        # j+k = a so r(j) + r(k) = r(a)
        # The vectors (a.x, 0) and (0, a.y) meet the criteria so if we rotate then sum them, we get r(a).
        # It is easy to rotate a vector with one zero axis around the origin (0,0) with SOHCAH(toa) as the sine/cosine are the new elements in a unit circle.
        # See http://mathworld.wolfram.com/images/eps-gif/RotationMatrixAxes_1000.gif for more a better explanation for the rotating the vector (1,1)

        if pressed[pygame.K_LEFT]:
            # both camera direction and camera plane must be rotated
            player.direction = player.direction.rotate(settings.ROTATION_SPEED)
            player.camera_plane = player.camera_plane.rotate(
                settings.ROTATION_SPEED)

        if pressed[pygame.K_RIGHT]:
            # both camera direction and camera plane must be rotated
            player.direction = player.direction.rotate(
                -settings.ROTATION_SPEED)

            player.camera_plane = player.camera_plane.rotate(
                -settings.ROTATION_SPEED)

    def simulate(self, player):
        """This method runs all simulation for the program"""
        self.handle_input(player)

    running = True

    def run(self):
        """Run the game with this method"""
        pygame.init()

        clock = pygame.time.Clock()

        fps = 0

        while self.running:

            self.simulate(self.player)
            self.renderer.render(self.player, fps)

            # delay until next frame.
            clock.tick(settings.TARGET_FPS)
            fps = math.floor(clock.get_fps())

        pygame.quit()
