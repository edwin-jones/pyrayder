"""This module defines the renderer object and related methods"""

import math
import os

import pygame
from pygame.math import Vector2

import asset_loader
import colors
import constants
import settings

from plotter import Plotter
from side import Side
from sprite import Sprite


class Renderer:
    """The default software renderer of the game"""

    def __init__(self):
        self.SCREEN = pygame.display.set_mode(settings.SCREEN_SIZE)
        self.plotter = Plotter()

        current_directory = os.path.dirname(os.path.realpath(__file__))
        wall_texture_folder_path = os.path.join(
            current_directory, "assets/textures/surfaces")

        sprite_texture_folder_path = os.path.join(
            current_directory, "assets/textures/objects")

        self.WALL_TEXTURES = asset_loader.get_textures(
            wall_texture_folder_path)

        self.SPRITE_TEXTURES = asset_loader.get_textures(
            sprite_texture_folder_path)

        # init the z buffer to the size of the screen. This is faster than using append() and clear()
        self._wall_z_buffer = [None] * settings.SCREEN_WIDTH

    def _darken(self, surface):
        "This method takes in a surface and drops its brightness in half"

        # we create a new rectangle with the same dimensions as the texture
        darkened_surface = pygame.Surface(surface.get_size())

        # we set the brightness of this surface to 128/half (255 is max)
        darkened_surface.set_alpha(128)

        # Apply the darken mask to the original surface from its origin (x:0, y:0)
        surface.blit(darkened_surface, (0, 0))

    def _draw_ui(self, player, fps):
        if(__debug__):
            start_position = Vector2(10, 5)
            self._draw_debug(player, fps, start_position)

    def _draw_debug_text(self, font, text, position):

        text = font.render(text, True, colors.YELLOW)

        self.SCREEN.blit(text, (position.x, position.y))
        position.y = position.y + 35

    def _draw_debug(self, player, fps, start_position):
        basicfont = pygame.font.SysFont(None, 48)

        fps_text = f'fps: {fps}'
        player_x_text = f'x: {player.position.x:.2f}'
        player_y_text = f'y: {player.position.y:.2f}'
        player_rotation_text = f'rotation: {player.get_rotation_degrees():.0f}'

        self._draw_debug_text(basicfont, fps_text, start_position)
        self._draw_debug_text(basicfont, player_x_text, start_position)
        self._draw_debug_text(basicfont, player_y_text, start_position)
        self._draw_debug_text(basicfont, player_rotation_text, start_position)

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

    def _get_wall_texture_slice(self, ray_direction, wall_x_percentage_across, texture, side):
        # wall x will be somewhere between 0 and 1 (eg, 25% across will be 0.25)
        # figure out how many pixels across the texture to be in x
        # we cast to an int to floor the value as we cannot start drawing at a non integral
        # x value
        texture_x = int(wall_x_percentage_across * texture.get_width())

        # get the width of the texture where column 1 = 0, col 2 = 1 and so on.
        zero_indexed_width = texture.get_width() - 1

        # if side is left/right and we are travelling right, we have hit a LEFT side
        # draw the texture from right to left (NOT left to right as normal)
        # as otherwise we will draw the texture backwards like we are behind it.
        if side == Side.LeftOrRight and ray_direction.x > 0:
            texture_x = zero_indexed_width - texture_x

        # if side is top/bottom and we are travelling down, we have hit a TOP side.
        # draw the texture from right to left (NOT left to right as normal)
        # as otherwise we will draw the texture backwards like we are behind it.
        if side == Side.TopOrBottom and ray_direction.y < 0:
            texture_x = zero_indexed_width - texture_x

        # get the part of the image we want to draw from the texture
        image_location = pygame.Rect(texture_x, 0, 1, texture.get_height())
        image_slice = texture.subsurface(image_location)

        return image_slice

    def _perform_dda(self, distance_to_side, distance_delta, step, side, map_pos):

        # jump to next map square, OR in x-direction, OR in y-direction - whichever is the closest side.
        if distance_to_side.x < distance_to_side.y:

            # increase the distance to side x by 1 map unit in x on the direction of this vector.
            # This means we will go from touching the next left/right side wall the the wall 1 unit after that.
            distance_to_side.x += distance_delta.x

            # increase the mapX index by 1/-1 depending on direction.
            map_pos.x += step.x

            # we are moving in x, so the current side to check is the left or right side.
            side = Side.LeftOrRight

        else:
            # increase the distance to side x by 1 map unit in y on the direction of this vector.
            # This means we will go from touching the next top/bottom side wall the the wall 1 unit after that.
            distance_to_side.y += distance_delta.y

            # increase the mapY index by 1/-1 depending on direction.
            map_pos.y += step.y

            # we are moving in y, so the current side to check is the top or bottom side.
            side = Side.TopOrBottom

        # Check if ray has hit a wall
        map_tile = settings.MAP[int(map_pos.x)][int(map_pos.y)]

        # we return two values here to get around the immutability of ints in python (an enum is basically an int!)
        if map_tile > 0 and map_tile < 9:
            return True, side
        else:
            return False, side

    def _perform_wall_dda(self, distance_to_side, distance_delta, step, side, map_pos):

        # jump to next map square, OR in x-direction, OR in y-direction - whichever is the closest side.
        if distance_to_side.x < distance_to_side.y:

            # increase the distance to side x by 1 map unit in x on the direction of this vector.
            # This means we will go from touching the next left/right side wall the the wall 1 unit after that.
            distance_to_side.x += distance_delta.x

            # increase the mapX index by 1/-1 depending on direction.
            map_pos.x += step.x

            # we are moving in x, so the current side to check is the left or right side.
            side = Side.LeftOrRight

        else:
            # increase the distance to side x by 1 map unit in y on the direction of this vector.
            # This means we will go from touching the next top/bottom side wall the the wall 1 unit after that.
            distance_to_side.y += distance_delta.y

            # increase the mapY index by 1/-1 depending on direction.
            map_pos.y += step.y

            # we are moving in y, so the current side to check is the top or bottom side.
            side = Side.TopOrBottom

        # Check if ray has hit a wall
        map_tile = settings.MAP[int(map_pos.x)][int(map_pos.y)]

        # we return two values here to get around the immutability of ints in python (an enum is basically an int!)
        if map_tile == 1 or (map_tile > 8 and map_tile < 10):
            return True, side
        else:
            return False, side

    def _get_wall_texture_for_block(self, map_pos):
        # get wall texture to use. -1 so we can start at index 0 of texture array
        texture_index = settings.MAP[int(map_pos.x)][int(map_pos.y)] - 1
        texture_index = max(0, texture_index)
        return self.WALL_TEXTURES[texture_index]

    def _draw_walls(self, player):

        for x in range(0, settings.SCREEN_WIDTH):

            # which box of the map we're in
            map_pos = Vector2()
            map_pos.x = int(player.position.x)
            map_pos.y = int(player.position.y)

            ray_direction = self.plotter.get_ray_direction(x, player)

            distance_delta = self.plotter.get_distance_delta(ray_direction)

            # length of ray from current position to next x or y-side
            distance_to_side = self.plotter.get_distance_to_side(
                player.position, map_pos, ray_direction, distance_delta)

            # what direction to step in x or y-direction (either +1 or -1)
            step = Vector2()
            step.x = -1 if ray_direction.x < 0 else 1
            step.y = -1 if ray_direction.y < 0 else 1

            side = Side.LeftOrRight  # was a NS or a EW wall hit?

            # perform DDA
            hit = False
            while not hit:
                hit, side = self._perform_dda(
                    distance_to_side, distance_delta, step, side, map_pos)

            # Calculate distance projected on camera direction (oblique distance will give fisheye effect!)
            perceptual_wall_distance = self.plotter.get_perceptual_wall_distance(
                side, player, map_pos, step, ray_direction)

            # Calculate height of line to draw on screen
            # we bring this into screen space by calculating as distance 1 (at the same point as the camera plane) = screenheight. Distance 2 = 1/2 screenheight. Distance 0.5 = 2 * screenheight.
            # This makes sure the further away we are the smaller the line is and the closer the taller the line is, making sure the screen is filled by objects in the same place as the camera.
            line_height = self.plotter.get_object_size_based_on_distance(
                perceptual_wall_distance)

            # calculate lowest and highest pixel to fill in current stripe
            # a start of a line can be through of as half the line up (-y) from the center of the screen in y (screen height /2).
            draw_start = (-line_height / 2) + settings.HALF_SCREEN_HEIGHT

            texture = self._get_wall_texture_for_block(map_pos)

            wall_x_across_percentage = self.plotter.get_wall_x_across_percentage(
                side, player.position, ray_direction, perceptual_wall_distance)

            # get which pixel in x from the texture we want to use
            # it's too expensive to set each pixel directly so we
            # map the line we want from the texture and draw that directly
            # to the screens surface.
            texture_slice = self._get_wall_texture_slice(
                ray_direction, wall_x_across_percentage, texture, side)

            self._draw_wall_line(
                x, draw_start, line_height, texture_slice, side)

            # add this to z buffer
            self._wall_z_buffer[x] = (perceptual_wall_distance)

    def _get_sprite_positions(self, player):
        # find all sprites on the map!
        sprite_positions = []

        for column in range(len(settings.MAP)):

            for y in range(len(settings.MAP[column])):

                value = settings.MAP[column][y]

                if value > 10 and value < 20:  # ignore non sprite objects
                    sprite_pos = Vector2(column + 0.5, y + 0.5)
                    distance_from_player = abs(
                        (player.position - sprite_pos).length())
                    sprite = Sprite(
                        value, sprite_pos, distance_from_player)
                    sprite_positions.append(sprite)

        # sort sprite positions so the ones furthest away are drawn first
        sprite_positions.sort(
            key=lambda column: column.distance_from_player, reverse=True)

        return sprite_positions

    def _draw_sprite_columns(self, distance_from_player, sprite_draw_start, sprite_texture):

        current_width = sprite_texture.get_width()
        current_height = sprite_texture.get_height()

        for column in range(current_width):

                # check z buffer (clamp index first)
            x_check = int(sprite_draw_start.x + column)
            x_check = max(x_check, 0)
            x_check = min(x_check, settings.SCREEN_WIDTH - 1)

            if self._wall_z_buffer[x_check] > distance_from_player:

                    # draw sprite vertical line
                location = pygame.Rect(column, 0, 1, current_height)
                slice = sprite_texture.subsurface(location)

                sprite_image_location = (
                    sprite_draw_start.x + column, sprite_draw_start.y)

                self.SCREEN.blit(slice, sprite_image_location)

    def _get_sprite_distance_from_player(self, player, sprite):

        sprite_pos = sprite.map_position
        distance_vector = sprite_pos - player.position
        distance = distance_vector.length()

        return distance

    def _get_sprite_screen_x_position(self, player, sprite):

        # get the distance between the sprite and player
        distance_vector = sprite.map_position - player.position

        distance = distance_vector.length()

        # Find angle between player and sprite
        # we do this by finding the angle between the sprite and player position,
        # THEN subtracting the player's current rotation from that.
        player_rotation = player.get_rotation()

        angle_between_sprite_and_player = math.atan2(
            distance_vector.y, distance_vector.x) - player_rotation

        # calculate what angle one column of pixels on screen represents
        radians_per_stripe = settings.FOV / settings.SCREEN_WIDTH

        # find the sprite horizontal center by converting the angle into a distance in pixels from the center of screen.
        angle_between_sprite_and_player_in_pixels = (
            angle_between_sprite_and_player / radians_per_stripe)
        sprite_x_center = settings.HALF_SCREEN_WIDTH - \
            angle_between_sprite_and_player_in_pixels

        sprite_size = self.plotter.get_object_size_based_on_distance(distance)

        # find the x position of the leftmost part of the sprite.
        sprite_leftmost_col_x = sprite_x_center - (sprite_size / 2)

        return sprite_leftmost_col_x

    def _draw_sprites(self, player):
        # find all sprites on the map!
        sprite_positions = self._get_sprite_positions(player)

        # this is rendering sprites slightly incorrectly due to a fisheye effect
        # because I am taking the full distance of the sprite from the player, not the perpedicular distance
        # from the camera plane. TODO - Fix this!
        for sprite in sprite_positions:

            index = sprite.sprite_index - 11
            sprite_texture = self.SPRITE_TEXTURES[index]

            sprite_distance = self._get_sprite_distance_from_player(
                player, sprite)
            sprite_size = self.plotter.get_object_size_based_on_distance(
                sprite_distance)
            sprite_screen_x_position = self._get_sprite_screen_x_position(
                player, sprite)

            sprite_draw_start_y = settings.HALF_SCREEN_HEIGHT - \
                (sprite_size / 2)

            # clamp draw start and draw end - there is no point drawing off the top or bottom of the screen.
            # remember, we draw from top to bottom.
            sprite_draw_start_y = max(sprite_draw_start_y, 0)

            sprite_texture = pygame.transform.scale(
                sprite_texture, (sprite_size, sprite_size))

            sprite_draw_start = Vector2(
                sprite_screen_x_position, sprite_draw_start_y)
            self._draw_sprite_columns(
                sprite_distance, sprite_draw_start, sprite_texture)

    def _draw_sky(self, player):
        # load the sky texture
        current_directory = os.path.dirname(os.path.realpath(__file__))
        sky_texture_folder_path = os.path.join(
            current_directory, "assets/textures/skies/sky1.png")
        sky_texture = pygame.image.load(sky_texture_folder_path)

        # calculate how much of the sky texture should be on screen
        # based on how much the current FOV
        fov_over_circle_ratio = settings.FOV / constants.FULL_CIRCLE_IN_RADIANS

        sky_texture_window_width = sky_texture.get_width() * fov_over_circle_ratio

        sky_texture_window_width = sky_texture_window_width * \
            (constants.HALF_CIRCLE_IN_RADIANS / settings.FOV)

        # avoid a divide by zero
        player_rotation_in_degrees = max(player.get_rotation_degrees(), 1)

        # use degrees here to avoid a negative value (player radian rotation can be negative)
        portion = player_rotation_in_degrees / 360

        x_start_pos = portion * sky_texture_window_width

        # get the part of the image we want to draw from the texture
        image_location = pygame.Rect(
            x_start_pos, 0, sky_texture_window_width, sky_texture.get_height())
        sky_texture_slice = sky_texture.subsurface(image_location)

        # scale that slice so it will fit the top half of the screen
        sky_texture_slice_scaled = pygame.transform.scale(
            sky_texture_slice, (int(settings.SCREEN_WIDTH),
                                int(settings.HALF_SCREEN_HEIGHT)))

        # the sky texture scaled slice should be draw from the top left (x = 0, y = 0)
        self.SCREEN.blit(sky_texture_slice_scaled, (0, 0))

    def _draw_doors(self, player):
        for x in range(0, settings.SCREEN_WIDTH):

            # which box of the map we're in
            map_pos = Vector2()
            map_pos.x = int(player.position.x)
            map_pos.y = int(player.position.y)

            ray_direction = self.plotter.get_ray_direction(x, player)

            distance_delta = self.plotter.get_distance_delta(ray_direction)

            # length of ray from current position to next x or y-side
            distance_to_side = self.plotter.get_distance_to_side(
                player.position, map_pos, ray_direction, distance_delta)

            # what direction to step in x or y-direction (either +1 or -1)
            step = Vector2()
            step.x = -1 if ray_direction.x < 0 else 1
            step.y = -1 if ray_direction.y < 0 else 1

            side = Side.LeftOrRight  # was a NS or a EW wall hit?

            # perform DDA
            hit = False
            while not hit:
                hit, side = self._perform_wall_dda(
                    distance_to_side, distance_delta, step, side, map_pos)

            # Calculate distance projected on camera direction (oblique distance will give fisheye effect!)
            perceptual_wall_distance = self.plotter.get_perceptual_wall_distance(
                side, player, map_pos, step, ray_direction)

            # Calculate height of line to draw on screen
            # we bring this into screen space by calculating as distance 1 (at the same point as the camera plane) = screenheight. Distance 2 = 1/2 screenheight. Distance 0.5 = 2 * screenheight.
            # This makes sure the further away we are the smaller the line is and the closer the taller the line is, making sure the screen is filled by objects in the same place as the camera.
            line_height = self.plotter.get_object_size_based_on_distance(
                perceptual_wall_distance)

            # calculate lowest and highest pixel to fill in current stripe
            # a start of a line can be through of as half the line up (-y) from the center of the screen in y (screen height /2).
            draw_start = (-line_height / 2) + settings.HALF_SCREEN_HEIGHT

            # skip non doors
            if settings.MAP[int(map_pos.x)][int(map_pos.y)] != 9:
                continue

            # skip anything that is closer in the z buffer
            if self._wall_z_buffer[x] < (perceptual_wall_distance):
                continue

            texture = self._get_wall_texture_for_block(map_pos)

            wall_x_across_percentage = self.plotter.get_wall_x_across_percentage(
                side, player.position, ray_direction, perceptual_wall_distance)

            # get which pixel in x from the texture we want to use
            # it's too expensive to set each pixel directly so we
            # map the line we want from the texture and draw that directly
            # to the screens surface.
            texture_slice = self._get_wall_texture_slice(
                ray_direction, wall_x_across_percentage, texture, side)

            self._draw_wall_line(
                x, draw_start, abs(line_height), texture_slice, side)

            # add this to z buffer
            self._wall_z_buffer[x] = (perceptual_wall_distance)

    def render(self, player, fps):
        """This method draws everything to the screen"""
        self._draw_floor()
        self._draw_sky(player)
        self._draw_walls(player)
        self._draw_doors(player)
        self._draw_sprites(player)
        self._draw_ui(player, fps)

        # Go ahead and update the screen with what we've drawn.
        # This MUST happen after all the other drawing commands.
        pygame.display.update()
