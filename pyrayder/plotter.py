"""This module contains a type to store calculate distances between the player and walls/objects"""

from pygame.math import Vector2

import settings
from side import Side


class Plotter:
    """This type calculates sizes, distances and directions of in game objects in relation to the player"""

    def _avoid_zero(self, value):
        """use this function to avoid zero if we risk a divide by zero expression."""
        if value == 0:
            return 0.000001
        else:
            return value

    def get_object_size_based_on_distance(self, distance):
        """Returns a value between 1 (100%) and 0 (0%) describing how much of the vertical screen an object 
           should consume based on its distance from the player"""

        size = int(settings.SCREEN_HEIGHT /
                   self._avoid_zero(distance))

        return size

    def get_distance_to_side(self, player_pos, map_pos, ray_direction, distance_delta):
        """get length of ray from current position to next x or y-side"""

        # subtract current map square x cord from the total ray x to get the difference/distance in x from the ray origin to the left wall,
        # as if we are moving right the rayPosition.x will be the greater value and we want an absolute/non negative value for the difference.
        # this is the same as the ratio of how far the ray position is across the map grid square in x, 0 = 0% and 1 = 100%.
        # OR subtract ray.x from the NEXT square's X co-ordinate to get the difference/distance in x from the ray origin to the right wall,
        # as if we are moving right the  map x + 1 will be the greater value and we want an absolute/non negative value for the difference.
        # this is the same as the ratio of how far the ray position is across the next map grid square in x, 0 = 0% and 1 = 100%.
        x_ratio = (
            player_pos.x - map_pos.x) if ray_direction.x < 0 else (map_pos.x + 1 - player_pos.x)
        y_ratio = (
            player_pos.y - map_pos.y) if ray_direction.y < 0 else (map_pos.y + 1 - player_pos.y)

        # multiply distance_delta by this ratio to get the true distance we need to go in the direction of the ray to hit the wall.
        distance_to_side = Vector2()
        distance_to_side.x = distance_delta.x * x_ratio
        distance_to_side.y = distance_delta.y * y_ratio

        return distance_to_side

    def get_ray_direction(self, x, player):
        """get a vector that represents the direction a ray travels from the player
           through the screen/camera plane at horizontal position / pixel column x"""

        # what percentage of the screen with is the current x value.
        x_ratio = x / settings.SCREEN_WIDTH

        # x-coordinate along camera plane, from -1 through 0 and on to 1
        camera_x = (2 * x_ratio) - 1

        # The current ray is the sum of the player direction and the x-coordinate along camera plane
        return player.direction + player.camera_plane * camera_x

    def get_distance_delta(self, ray_direction):
        """length of ray from one x or y-side to next x or y-side"""
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
        distance_delta = Vector2()
        distance_delta.x = scaled_x.length()
        distance_delta.y = scaled_y.length()

        return distance_delta

    def get_wall_x_across_percentage(self, side, player_pos, ray_direction, perceptual_wall_distance):
        """get where exactly a wall was hit in terms of a value between 0 and 1."""
        distance_ray_has_travelled_in_one_axis = 0

        # if we had hit a left or right side, we need to know how far in y the ray has travelled
        # from the player.
        if (side == Side.LeftOrRight):
            distance_ray_has_travelled_in_one_axis = player_pos.y + \
                (perceptual_wall_distance * ray_direction.y)

        # if we have hit a top or bottom side, we need to know how far in x the ray has travelled
        # from the player
        else:
            distance_ray_has_travelled_in_one_axis = player_pos.x + \
                perceptual_wall_distance * ray_direction.x

        # we only want a measure of how far across the wall we have hit as a
        # percentage, so we use the modulo operator to get rid of
        # the whole part of the number. This would make 10.77 into 0.77
        return distance_ray_has_travelled_in_one_axis % 1

    def get_perceptual_wall_distance(self, side, player, map_pos, step, ray_direction):
        """Calculate distance projected on camera direction (oblique distance will give fisheye effect!)"""
        if side == Side.LeftOrRight:
            # this difference is how far the ray has travelled in x before hitting a side wall.
            distance_in_x = map_pos.x - player.position.x
            # if step = 1/positive x/right, make this 0. if step = -1/negative x/left make it 1.
            one_or_zero = (1 - step.x) / 2
            perceptual_wall_distance = (
                distance_in_x + one_or_zero) / ray_direction.x

        else:
            # this difference is how far the ray has travelled in y before hitting a wall.
            distance_in_y = map_pos.y - player.position.y

            if settings.MAP[int(map_pos.x)][int(map_pos.y)] == 9:

                if(player.position.y < map_pos.y):
                    distance_in_y += 0.5
                elif (player.position.y > map_pos.y):
                    distance_in_y -= 0.5

            # if step = 1/positive y/up, make this 0. if step = -1/negative y/down make it 1.
            one_or_zero = (1 - step.y) / 2
            perceptual_wall_distance = (
                distance_in_y + one_or_zero) / ray_direction.y

        perceptual_wall_distance = self._avoid_zero(
            perceptual_wall_distance)

        return perceptual_wall_distance
