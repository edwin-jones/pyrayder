#inspiration loving taken from here http://lodev.org/cgtutor/raycasting.html
#and here https://www.essentialmath.com/GDC2012/GDC2012_JMV_Rotations.pdf (see 2D vec rotations)

import math
import colors
import pygame
#import vector
from player import Player
from pygame.math import Vector2
from side import Side


class Game(object):
    """primary game engine"""



    """To rotate a vector, multiply it with the rotation matrix
    [ cos(a) -sin(a) ]
    [ sin(a)  cos(a) ]"""

    ONE_DEGREE_IN_RADIANS = math.pi / 180
    ONE_RADIAN_IN_DEGREES = 180 / math.pi

    TARGET_FPS = 60 

    #flip grid 90 left for 'real' map. +y is up, +x is right.
    MAP = (
            (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
            (1, 2, 0, 0, 0, 0, 0, 0, 0, 1),
            (1, 0, 0, 0, 0, 0, 0, 0, 0, 1),
            (1, 0, 0, 0, 0, 0, 0, 0, 0, 1),
            (1, 0, 0, 0, 2, 3, 0, 0, 0, 1),
            (1, 0, 0, 0, 5, 6, 0, 0, 0, 1),
            (1, 0, 0, 0, 0, 0, 0, 0, 0, 1),
            (1, 0, 0, 0, 0, 0, 0, 0, 4, 1),
            (1, 3, 3, 0, 0, 0, 0, 0, 4, 1),
            (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
          )

    #MAP2 (2,3,3)


    SCREEN_WIDTH = 640
    SCREEN_HEIGHT = 480

    ROTATION_SPEED = 2.5 #rotation speed is defined degrees per frame
    MOVE_SPEED = 0.05 #move speed is defined as squares per frame.


    SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
    SCREEN = pygame.display.set_mode(SCREEN_SIZE)

    PLAYER_START_POSITION = Vector2(3, 3)
    PLAYER_START_DIRECTION = Vector2(1, 0)
    PLAYER_START_CAMERA_PLANE = Vector2(0, -0.66) #66 degree fov. Length 1 would be a 90 degree fov, 0.5 would be 45. Camera plane must be perpendicular to player direction!

    WALL_PALETTE = [colors.BLACK, colors.WHITE, colors.RED, colors.GREEN, colors.BLUE, colors.YELLOW, colors.PURPLE, colors.ORANGE]

    fps = 0

    def avoid_zero(self, value):
        """use this function to avoid zero if we risk a divide by zero expression."""
        if value == 0:
            return 0.000001
        else:
            return value

    def handle_input(self, player):
        """This function handles control input for this program"""

        for event in pygame.event.get():
            #quit if user presses exit
            if event.type == pygame.QUIT:
                self.running = False
                return
        
        pressed = pygame.key.get_pressed()

        if pressed[pygame.K_ESCAPE]:
            self.running = False
            return

        #handle movement

		#forward and backward
        if pressed[pygame.K_UP]:
            player.position += player.direction * self.MOVE_SPEED
          
        if  pressed[pygame.K_DOWN]:
            player.position -= player.direction * self.MOVE_SPEED

        #strafe left and right
        if pressed[pygame.K_a]:
            player.position -= player.camera_plane * self.MOVE_SPEED
          
        if  pressed[pygame.K_d]:
            player.position += player.camera_plane * self.MOVE_SPEED
        
		#rotate left and right
        # note, to rotate a vector a by an angle to become vector r(a):
        # j+k = a so r(j) + r(k) = r(a)
        # The vectors (a.x, 0) and (0, a.y) meet the criteria so if we rotate then sum them, we get r(a).
        # It is easy to rotate a vector with one zero axis around the origin (0,0) with SOHCAH(toa) as the sine/cosine are the new elements in a unit circle.
        # See http://mathworld.wolfram.com/images/eps-gif/RotationMatrixAxes_1000.gif for more a better explanation for the rotating the vector (1,1)

        if  pressed[pygame.K_LEFT]:
            #both camera direction and camera plane must be rotated
            player.direction = player.direction.rotate(self.ROTATION_SPEED)
            player.camera_plane = player.camera_plane.rotate(self.ROTATION_SPEED)

        if pressed[pygame.K_RIGHT]:            
            #both camera direction and camera plane must be rotated
            player.direction = player.direction.rotate(-self.ROTATION_SPEED)
            player.camera_plane = player.camera_plane.rotate(-self.ROTATION_SPEED)


    def simulate(self, player):
        """This method runs all simulation for the program"""
        self.handle_input(player)

    def draw_ui(self, player):
        if(__debug__):
            self.draw_debug(player)

    def draw_debug(self, player):
        basicfont = pygame.font.SysFont(None, 48)
        text = basicfont.render('fps: {}'.format(self.fps), True, colors.YELLOW)
        textrect = text.get_rect()
        textrect.centerx = 150
        textrect.centery = 20
        self.SCREEN.blit(text, textrect)

        text = basicfont.render('x: {:.2f}'.format(player.position.x), True, colors.YELLOW)
        textrect = text.get_rect()
        textrect.centerx = 150
        textrect.centery = 60
        self.SCREEN.blit(text, textrect)

        text = basicfont.render('y: {:.2f}'.format(player.position.y), True, colors.YELLOW)
        textrect = text.get_rect()
        textrect.centerx = 150
        textrect.centery = 90
        self.SCREEN.blit(text, textrect)

    def render(self, player):
        """This method draws everything to the screen"""
        for x in range(0, self.SCREEN_WIDTH):
           
		   #calculate ray position and direction

            x_ratio = x / self.SCREEN_WIDTH # what percentage of the screen with is the current x value.
            cameraX = (2 * x_ratio) - 1 # x-coordinate along camera plane, from -1 through 0 and on to 1

            rayPosition = player.position

            #The current ray is the sum of the player direction and the x-coordinate along camera plane
            rayDir = player.direction + player.camera_plane * cameraX

            #which box of the map we're in
            mapX = int(rayPosition.x)
            mapY = int(rayPosition.y)

            #length of ray from current position to next x or y-side
            distance_to_side_x = 0
            distance_to_side_y = 0

            #length of ray from one x or y-side to next x or y-side
            #see https://gamedev.stackexchange.com/q/45013 for a better explanation.

			#calculate how the ratios of 1 to the x and y components
			#that is what number do you need to multiply x or y by to turn them into 1.
            xRatio = 1 / self.avoid_zero(rayDir.x)
            yRatio = 1 / self.avoid_zero(rayDir.y)

            #create vectors for where x/y has length 1 using these multipliers.
            scaled_x = rayDir * xRatio  
            scaled_y = rayDir * yRatio

            #the length of these vectors represent how far the ray has to travel to move one unit in x or one unit in y.
            # Remember, we can get the length of a vector with the Pythagorean theorem. 
            # a*a + b*b = c*c OR 
            # x*x + y*y = length * length SO
            # length = sqrt(x*x + y*y)
            distance_delta_x = scaled_x.length()
            distance_delta_y = scaled_y.length()

            perpWallDist = 0

            #what direction to step in x or y-direction (either +1 or -1)
            stepX = 0
            stepY = 0

            hit = False #was there a wall hit?
            side = Side.LeftOrRight #was a NS or a EW wall hit?

            #calculate step and initial sideDist
            if rayDir.x < 0:

                # a negative x means we are moving left
                stepX = -1 

                # subtract current map square x cord from the total ray x to get the difference/distance in x from the ray origin to the left wall,
                # as if we are moving right the rayPosition.x will be the greater value and we want an absolute/non negative value for the difference.
                # this is the same as the ratio of how far the ray position is across the map grid square in x, 0 = 0% and 1 = 100%.              
                x_ratio = (rayPosition.x - mapX)

                # multiply distance_delta by this ratio to get the true distance we need to go in the direction of the ray to hit the left wall.
                distance_to_side_x = distance_delta_x * x_ratio
       
            else:

                # a positive x means we are moving right
                stepX = 1

                # subtract ray.x from the NEXT square's X co-ordinate to get the difference/distance in x from the ray origin to the right wall,
                # as if we are moving right the  map x + 1 will be the greater value and we want an absolute/non negative value for the difference.
                # this is the same as the ratio of how far the ray position is across the next map grid square in x, 0 = 0% and 1 = 100%.              
                x_ratio = (mapX + 1 - rayPosition.x)

                # multiply distance_delta by this ratio to get the true distance we need to go in the direction of the ray to hit the right wall.
                distance_to_side_x = distance_delta_x * x_ratio
       
            # the same principles as above apply for  distance checks for the distance for the ray to go to hit the square below and above.
            if rayDir.y < 0:

                #a negative y means mean we are going down
                stepY = -1
                y_ratio = (rayPosition.y - mapY)
                distance_to_side_y =  distance_delta_y * y_ratio
       
            else:
                #a positive y means mean we are going up
                stepY = 1
                y_ratio = (mapY + 1 - rayPosition.y)
                distance_to_side_y = distance_delta_y * y_ratio

            #perform DDA
            while (hit == False):
        
                #jump to next map square, OR in x-direction, OR in y-direction
                if (distance_to_side_x < distance_to_side_y):
                    distance_to_side_x += distance_delta_x
                    mapX += stepX
                    side = Side.LeftOrRight
            
                else:
                    distance_to_side_y += distance_delta_y
                    mapY += stepY
                    side = Side.BottomOrTop
            
                #Check if ray has hit a wall
                if (self.MAP[mapX][mapY] > 0):
                     hit = True

            #Calculate distance projected on camera direction (oblique distance will give fisheye effect!)
            if (side == Side.LeftOrRight):
                perpWallDist = (mapX - rayPosition.x + (1 - stepX) / 2) / rayDir.x
        
            else:
                perpWallDist = (mapY - rayPosition.y + (1 - stepY) / 2) / rayDir.y

            perpWallDist = self.avoid_zero(perpWallDist)

            #Calculate height of line to draw on screen
            lineHeight = int(self.SCREEN_HEIGHT / perpWallDist)

            #calculate lowest and highest pixel to fill in current stripe
            drawStart = -lineHeight / 2 + self.SCREEN_HEIGHT / 2

            if drawStart < 0:
                drawStart = 0

            drawEnd = lineHeight / 2 + self.SCREEN_HEIGHT / 2

            if drawEnd >= self.SCREEN_HEIGHT:
                drawEnd = self.SCREEN_HEIGHT - 1

            #choose wall color
            mapColorIndex = self.MAP[mapX][mapY]

            color = self.WALL_PALETTE[mapColorIndex]

            #give x and y sides different brightness
            if side == Side.BottomOrTop:
                color = (color[0]/2, color[1]/2, color[2]/2)

          #draw the pixels of the stripe as a vertical line
            pygame.draw.line(self.SCREEN, color, (x, drawStart), (x, drawEnd))

        self.draw_ui(player)

        # Go ahead and update the screen with what we've drawn.
        # This MUST happen after all the other drawing commands.
        pygame.display.update()


    running = True

    def run(self):  
        """Run the game with this method"""
        pygame.init()

        player = Player(self.PLAYER_START_POSITION, self.PLAYER_START_DIRECTION, self.PLAYER_START_CAMERA_PLANE)

        clock = pygame.time.Clock()

        while self.running:

            #fill screen with back buffer color and then draw the ceiling/sky.
            self.SCREEN.fill(colors.FLOOR_GRAY)
            pygame.draw.rect(self.SCREEN, colors.CEILING_GRAY, (0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT/2))

            self.simulate(player)
            self.render(player)

			#delay until next frame.
            clock.tick(self.TARGET_FPS)
            self.fps = math.floor(clock.get_fps())

        pygame.quit()

