"""This module defines the renderer object and related methods"""

from side import Side
from pygame.math import Vector2

import side
import settings
import pygame
import colors
import os
import math


import asset_loader


class SpriteInfo:
    def __init__(self, sprite_index, map_position, distance_from_player):
        self.sprite_index = sprite_index
        self.map_position = map_position
        self.distance_from_player = distance_from_player


class Renderer:

    def __init__(self):
        self.SCREEN = pygame.display.set_mode(settings.SCREEN_SIZE)

        current_directory = os.path.dirname(os.path.realpath(__file__))
        wall_texture_folder_path = os.path.join(
            current_directory, "assets/textures/surfaces")

        sprite_texture_folder_path = os.path.join(
            current_directory, "assets/textures/objects")

        self.WALL_TEXTURES = asset_loader.get_textures(
            wall_texture_folder_path)

        self.SPRITE_TEXTURES = asset_loader.get_textures(
            sprite_texture_folder_path)

        self._wall_z_buffer = []

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
        player_rotation_text = f'rotation: {player.get_rotation_degrees():.0f}'

        self._draw_debug_text(basicfont, fps_text, 150, 20)
        self._draw_debug_text(basicfont, player_x_text, 150, 60)
        self._draw_debug_text(basicfont, player_y_text, 150, 90)
        self._draw_debug_text(basicfont, player_rotation_text, 150, 120)

    def _draw_floor(self):
        # fill screen with back buffer color and then draw the ceiling/sky.
        self.SCREEN.fill(colors.FLOOR_GRAY)

    def _draw_wall_line(self, x, start, height, image_slice, side=Side.TopOrBottom):
        # figure out the position and size of the vertical line we want to draw on screen
        scale_rect = pygame.Rect(x, start, 1, height)

        # put the area of the image we want into the space we want to put on screen
        scaled = pygame.transform.scale(image_slice, scale_rect.size)

        # draw the scaled line where we want to on the screen.
        if (side == Side.LeftOrRight):
            self._darken(scaled)

        self.SCREEN.blit(scaled, scale_rect)

    def _get_texture_slice(self, ray_direction, wall_x, texture, side):
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

        return image_slice

    def _draw_walls(self, player):
        # clear z buffer
        self._wall_z_buffer.clear()

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
            x_ratio = (
                ray_origin.x - map_x) if ray_direction.x < 0 else (map_x + 1 - ray_origin.x)
            y_ratio = (
                ray_origin.y - map_y) if ray_direction.y < 0 else (map_y + 1 - ray_origin.y)

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
                map_tile = settings.MAP[map_x][map_y]
                if map_tile > 0 and map_tile < 10:
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

            # get texture to use. -1 so we can start at index 0 of texture array
            texture_index = settings.MAP[map_x][map_y] - 1
            texture_index = max(0, texture_index)
            texture = self.WALL_TEXTURES[texture_index]

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
            texture_slice = self._get_texture_slice(
                ray_direction, wall_x, texture, side)
            self._draw_wall_line(
                x, draw_start, line_height, texture_slice, side)

            # add this to z buffer
            self._wall_z_buffer.append(perceptual_wall_distance)

    def _draw_sprites(self, player):
        # SPRITE TEST
        # get the part of the image we want to draw from the texture

        # find all sprites on the map!
        sprite_positions = []

        for x in range(len(settings.MAP)):
            for y in range(len(settings.MAP[x])):
                value = settings.MAP[x][y]
                if value > 10 and value < 20:  # ignore non sprite objects
                    sprite_pos = Vector2(x + 0.5, y + 0.5)
                    distance_from_player = abs(
                        (player.position - sprite_pos).length())
                    sprite_info = SpriteInfo(
                        value, sprite_pos, distance_from_player)
                    sprite_positions.append(sprite_info)

        # sort sprite positions so the ones furthest away are drawn first
        sprite_positions.sort(
            key=lambda x: x.distance_from_player, reverse=True)

        for sprite_info in sprite_positions:

            index = sprite_info.sprite_index - 11
            sprite_texture = self.SPRITE_TEXTURES[index]

            sprite_pos = sprite_info.map_position

            distance_vector = sprite_pos - player.position

            distance = distance_vector.length()

            theta = player.get_rotation()
            theta = theta * 57.2958  # Convert to degrees
            if (theta < 0):
                theta += 360  # Make sure its in proper range

            # Find angle between player and sprite
            thetaTemp = math.atan2(distance_vector.y, distance_vector.x)
            thetaTemp = thetaTemp * 57.2958  # Convert to degrees
            if (thetaTemp < 0):
                thetaTemp += 360  # Make sure its in proper range

            fov = 66
            half_fov = fov / 2

            # Wrap things around if needed
            # Theta + half_fov  = angle of ray that generates leftmost collum of the screen
            yTmp = theta + half_fov - thetaTemp
            if (thetaTemp > 270 and theta < 90):
                yTmp = theta + half_fov - thetaTemp + 360
            if (theta > 270 and thetaTemp < 90):
                yTmp = theta + half_fov - thetaTemp - 360

            # Compute the screen x coordinate
            xTmp = yTmp * settings.SCREEN_WIDTH / fov

            sprite_height = int(settings.SCREEN_HEIGHT /
                                self._avoid_zero(distance))

            sprite_draw_start = settings.HALF_SCREEN_HEIGHT - \
                (sprite_height / 2)

            # clamp draw start and draw end - there is no point drawing off the top or bottom of the screen.
            # remember, we draw from top to bottom.
            sprite_draw_start = max(sprite_draw_start, 0)

            sprite_texture = pygame.transform.scale(
                sprite_texture, (sprite_height, sprite_height))

            current_width = sprite_texture.get_width()
            current_height = sprite_texture.get_height()

            for x in range(current_width):

                # check z buffer (clamp index first)
                x_check = int(xTmp + x)
                x_check = max(x_check, 0)
                x_check = min(x_check, settings.SCREEN_WIDTH - 1)
                if self._wall_z_buffer[x_check] > distance:

                    # draw sprite vertical line
                    location = pygame.Rect(x, 0, 1, current_height)
                    slice = sprite_texture.subsurface(location)

                    sprite_image_location = pygame.Rect(
                        xTmp + x, sprite_draw_start, 10, 10)

                    self.SCREEN.blit(slice, sprite_image_location)

    def _draw_sky(self, player):

        # TODO CLEAN UP AND COMMENT THIS
        sky_texture = pygame.image.load("assets/textures/skies/sky1.png")

        fov = 66
        view_portion = fov / 360

        width_on_screen = sky_texture.get_width() * view_portion

        width_on_screen = width_on_screen * 2.7

        player_rotation_in_degrees = player.get_rotation_degrees()

        player_rotation_in_degrees = player_rotation_in_degrees if player_rotation_in_degrees > 1 else 1

        portion = player_rotation_in_degrees / 360

        x_start_pos = portion * width_on_screen
        x_end_pos = x_start_pos + width_on_screen

        # get the part of the image we want to draw from the texture
        image_location = pygame.Rect(
            x_start_pos, 0, width_on_screen, sky_texture.get_height())
        image_slice = sky_texture.subsurface(image_location)

        sky_texture = pygame.transform.scale(
            image_slice, (int(settings.SCREEN_WIDTH),
                          int(settings.HALF_SCREEN_HEIGHT)))
        sky_location = pygame.Rect(0, 0, 0, 0)

        self.SCREEN.blit(sky_texture, sky_location)

    def render(self, player, fps):
        """This method draws everything to the screen"""
        self._draw_floor()
        self._draw_sky(player)
        self._draw_walls(player)
        self._draw_sprites(player)
        self._draw_ui(player, fps)

        # Go ahead and update the screen with what we've drawn.
        # This MUST happen after all the other drawing commands.
        pygame.display.update()
