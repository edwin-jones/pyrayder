"""This module defines the renderer object and related methods"""

from side import Side

import side
import settings
import pygame
import colors
import os
import math

import asset_loader


class Renderer:

    def __init__(self):
        self.SCREEN = pygame.display.set_mode(settings.SCREEN_SIZE)

        current_directory = os.path.dirname(os.path.realpath(__file__))
        wall_texture_folder_path = os.path.join(
            current_directory, "assets/textures/surfaces")

        self.WALL_TEXTURES = asset_loader.get_textures(
            wall_texture_folder_path)


    def _avoid_zero(self, value):
        """use this function to avoid zero if we risk a divide by zero expression."""
        if value == 0:
            return 0.000001
        else:
            return value


    def _darken(self, surface):
        "This method takes in a surface and drops its brightness in half"

        # we create a new rectangle with the same dimensions as the texture
        dark = pygame.Surface(surface.get_size())

        # we set the brightness of this surface to 128/half (255 is max)
        dark.set_alpha(128)

        # Apply the darken mask to the original surface from its origin (x:0, y:0)
        surface.blit(dark, (0, 0))


    def _draw_ui(self, player, fps):
        if(__debug__):
            self._draw_debug(player, fps)


    def _draw_debug_text(self, font, text, x_pos, y_pos):

        text = font.render(text, True, colors.YELLOW)

        textrect = text.get_rect()
        textrect.centerx = x_pos
        textrect.centery = y_pos

        self.SCREEN.blit(text, textrect)


    def _draw_debug(self, player, fps):
        basicfont = pygame.font.SysFont(None, 48)

        fps_text = f'fps: {fps}'
        player_x_text = f'x: {player.position.x:.2f}'
        player_y_text = f'y: {player.position.y:.2f}'

        self._draw_debug_text(basicfont, fps_text, 150, 20)
        self._draw_debug_text(basicfont, player_x_text, 150, 60)
        self._draw_debug_text(basicfont, player_y_text, 150, 90)


    def _draw_ceiling_and_floor(self):
        # fill screen with back buffer color and then draw the ceiling/sky.
        self.SCREEN.fill(colors.FLOOR_GRAY)
        pygame.draw.rect(self.SCREEN, colors.CEILING_GRAY,
                         (0, 0, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT / 2))


    def _draw_wall_line(self, x, ray_direction, wall_x, texture, side, draw_start, height):
            # figure out how many pixels across the texture to be in x
            texture_x = int(wall_x * int(texture.get_width()))

            # this code makes sure the texture doesn't flip/invert TODO HOW DOES THIS WORK?
            if side == Side.LeftOrRight and ray_direction.x > 0:
                texture_x = texture.get_width() - texture_x - 1
            if side == Side.TopOrBottom and ray_direction.y < 0:
                texture_x = texture.get_width() - texture_x - 1

            # get the part of the image we want to draw from the texture
            image_location = pygame.Rect(texture_x, 0, 1, texture.get_height())
            image_slice = texture.subsurface(image_location)

            # figure out the position and size of the vertical line we want to draw on screen
            scale_rect = pygame.Rect(x, draw_start, 1, height)

            # put the area of the image we want into the space we want to put on screen
            scaled = pygame.transform.scale(image_slice, scale_rect.size)

            # draw the scaled line where we want to on the screen.
            if (side == Side.LeftOrRight):
                self._darken(scaled)

            self.SCREEN.blit(scaled, scale_rect)


    def _draw_walls(self, player):
        for x in range(0, settings.SCREEN_WIDTH):

            # calculate ray position and direction

            # what percentage of the screen with is the current x value.
            x_ratio = x / settings.SCREEN_WIDTH
            # x-coordinate along camera plane, from -1 through 0 and on to 1
            camera_x = (2 * x_ratio) - 1

            ray_origin = player.position

            # The current ray is the sum of the player direction and the x-coordinate along camera plane
            ray_direction = player.direction + player.camera_plane * camera_x

            # which box of the map we're in
            map_x = int(ray_origin.x)
            map_y = int(ray_origin.y)

            # length of ray from current position to next x or y-side
            distance_to_side_x = 0
            distance_to_side_y = 0

            # length of ray from one x or y-side to next x or y-side
            # see https://gamedev.stackexchange.com/q/45013 for a better explanation.

            # calculate how the ratios of 1 to the x and y components
            # that is what number do you need to multiply x or y by to turn them into 1.
            x_ratio = 1 / self._avoid_zero(ray_direction.x)
            y_ratio = 1 / self._avoid_zero(ray_direction.y)

            # create vectors for where x/y has length 1 using these multipliers.
            scaled_x = ray_direction * x_ratio
            scaled_y = ray_direction * y_ratio

            # the length of these vectors represent how far the ray has to travel to move one unit in x or one unit in y.
            # Remember, we can get the length of a vector with the Pythagorean theorem.
            # a*a + b*b = c*c OR
            # x*x + y*y = length * length SO
            # length = sqrt(x*x + y*y)
            distance_delta_x = scaled_x.length()
            distance_delta_y = scaled_y.length()

            perceptual_wall_distance = 0

            # what direction to step in x or y-direction (either +1 or -1)
            step_x = -1 if ray_direction.x < 0 else 1
            step_y = -1 if ray_direction.y < 0 else 1

            # subtract current map square x cord from the total ray x to get the difference/distance in x from the ray origin to the left wall,
            # as if we are moving right the rayPosition.x will be the greater value and we want an absolute/non negative value for the difference.
            # this is the same as the ratio of how far the ray position is across the map grid square in x, 0 = 0% and 1 = 100%.
            # OR subtract ray.x from the NEXT square's X co-ordinate to get the difference/distance in x from the ray origin to the right wall,
            # as if we are moving right the  map x + 1 will be the greater value and we want an absolute/non negative value for the difference.
            # this is the same as the ratio of how far the ray position is across the next map grid square in x, 0 = 0% and 1 = 100%.
            x_ratio = (ray_origin.x - map_x) if ray_direction.x < 0 else (map_x + 1 - ray_origin.x)
            y_ratio = (ray_origin.y - map_y) if ray_direction.y < 0 else (map_y + 1 - ray_origin.y)

            # multiply distance_delta by this ratio to get the true distance we need to go in the direction of the ray to hit the wall.
            distance_to_side_x = distance_delta_x * x_ratio
            distance_to_side_y = distance_delta_y * y_ratio

            hit = False  # was there a wall hit?
            side = Side.LeftOrRight  # was a NS or a EW wall hit?

            # perform DDA
            while not hit:

                # jump to next map square, OR in x-direction, OR in y-direction - whichever is the closest side.
                if distance_to_side_x < distance_to_side_y:

                    # increase the distance to side x by 1 map unit in x on the direction of this vector.
                    # This means we will go from touching the next left/right side wall the the wall 1 unit after that.
                    distance_to_side_x += distance_delta_x

                    # increase the mapX index by 1/-1 depending on direction.
                    map_x += step_x

                    # we are moving in x, so the current side to check is the left or right side.
                    side = Side.LeftOrRight

                else:
                    # increase the distance to side x by 1 map unit in y on the direction of this vector.
                    # This means we will go from touching the next top/bottom side wall the the wall 1 unit after that.
                    distance_to_side_y += distance_delta_y

                    # increase the mapY index by 1/-1 depending on direction.
                    map_y += step_y

                    # we are moving in y, so the current side to check is the top or bottom side.
                    side = Side.TopOrBottom

                # Check if ray has hit a wall
                if settings.MAP[map_x][map_y] > 0:
                    hit = True

            # Calculate distance projected on camera direction (oblique distance will give fisheye effect!)
            if side == Side.LeftOrRight:
                # this difference is how far the ray has travelled in x before hitting a side wall.
                distance_in_x = map_x - ray_origin.x
                # if step = 1/positive x/right, make this 0. if step = -1/negative x/left make it 1.
                one_or_zero = (1 - step_x) / 2
                perceptual_wall_distance = (
                    distance_in_x + one_or_zero) / ray_direction.x

            else:
                # this difference is how far the ray has travelled in y before hitting a wall.
                distance_in_y = map_y - ray_origin.y
                # if step = 1/positive y/up, make this 0. if step = -1/negative y/down make it 1.
                one_or_zero = (1 - step_y) / 2
                perceptual_wall_distance = (
                    distance_in_y + one_or_zero) / ray_direction.y

            perceptual_wall_distance = self._avoid_zero(
                perceptual_wall_distance)

            # Calculate height of line to draw on screen
            # we bring this into screen space by calculating as distance 1 (at the same point as the camera plane) = screenheight. Distance 2 = 1/2 screenheight. Distance 0.5 = 2 * screenheight.
            # This makes sure the further away we are the smaller the line is and the closer the taller the line is, making sure the screen is filled by objects in the same place as the camera.
            line_height = int(settings.SCREEN_HEIGHT /
                              perceptual_wall_distance)

            # calculate lowest and highest pixel to fill in current stripe
            # a start of a line can be through of as half the line up (-y) from the center of the screen in y (screen height /2).

            draw_start = -line_height / 2 + settings.HALF_SCREEN_HEIGHT

            # a end of a line can be through of as half the line down (+y) from the center of the screen in y (screen height /2).
            draw_end = line_height / 2 + settings.HALF_SCREEN_HEIGHT

            # clamp draw start and draw end - there is no point drawing off the top or bottom of the screen.
            # remember, we draw from top to bottom.
            draw_start = max(draw_start, 0)
            draw_end = min(draw_end, settings.SCREEN_HEIGHT)

            # get texture to use. -1 so we can start at index 0 of texxture array
            texture_index = settings.MAP[map_x][map_y] - 1
            texture_index = max(0, texture_index)
            texture = self.WALL_TEXTURES[texture_index]

            # attempt tp calculate Y pos of texture
            texture_line_height = draw_end - draw_start

            # give x and y sides different brightness
            if side == Side.TopOrBottom:
                # TODO half brightness of side textures?
                pass

            # where exactly the wall was hit in terms of a value between 0 and 1. TODO HOW DOES THIS WORK?
            wall_x = 0
            if (side == Side.LeftOrRight):
                wall_x = ray_origin.y + perceptual_wall_distance * ray_direction.y
            else:
                wall_x = ray_origin.x + perceptual_wall_distance * ray_direction.x
            wall_x -= math.floor((wall_x))

            # get which pixel in x from the texture we want to use
            # it's too expensive to set each pixel directly so we
            # map the line we want from the texture and draw that directly
            # to the screens surface.

            self._draw_wall_line(x, ray_direction, wall_x, texture, side, draw_start, texture_line_height)


    def render(self, player, fps):
        """This method draws everything to the screen"""
        self._draw_ceiling_and_floor()
        self._draw_walls(player)
        self._draw_ui(player, fps)

        # Go ahead and update the screen with what we've drawn.
        # This MUST happen after all the other drawing commands.
        pygame.display.update()
