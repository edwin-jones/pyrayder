"""This module contains the keyboard input handler type"""

import pygame
import math
import pyrayder.settings as settings


class KeyboardInputHandler:
    """A basic keyboard input handler class"""

    def handle_input(self, player):
        """This function handles control input for this program. Returns false if exit button pressed"""

        for event in pygame.event.get():
            # quit if user presses exit
            if event.type == pygame.QUIT:
                return False

        pressed = pygame.key.get_pressed()

        if pressed[pygame.K_ESCAPE]:
            return False

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

        return True
