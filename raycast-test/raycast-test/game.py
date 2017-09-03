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

    MAP = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 5, 3, 0, 0, 0, 1],
        [1, 0, 0, 0, 1, 4, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]


    SCREEN_WIDTH = 640
    SCREEN_HEIGHT = 480

    ROTATION_SPEED = 2.5 #rotation speed is defined degrees per frame
    MOVE_SPEED = 0.05 #move speed is defined as squares per frame.


    SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
    SCREEN = pygame.display.set_mode(SCREEN_SIZE)

    PLAYER_START_POSITION = Vector2(2, 2)
    PLAYER_START_DIRECTION = Vector2(1, 0)
    PLAYER_START_CAMERA_PLANE = Vector2(0, -0.5)

    WALL_PALETTE = [colors.BLACK, colors.WHITE, colors.RED, colors.GREEN, colors.BLUE, colors.YELLOW]

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

    def draw_ui(self):
        if(__debug__):
            self.draw_debug()

    def draw_debug(self):
        basicfont = pygame.font.SysFont(None, 48)
        text = basicfont.render('fps: {}'.format(self.fps), True, colors.YELLOW)
        textrect = text.get_rect()
        textrect.centerx = 150
        textrect.centery = 20
        self.SCREEN.blit(text, textrect)

    def render(self, player):
        """This method draws everything to the screen"""
        for x in range(0, self.SCREEN_WIDTH):
            #calculate ray position and direction
            cameraX = 2 * x / self.SCREEN_WIDTH - 1 #x-coordinate in camera space
            rayPosition = player.position

            rayDir = player.direction + player.camera_plane * cameraX

            #which box of the map we're in
            mapX = int(rayPosition.x)
            mapY = int(rayPosition.y)

            #length of ray from current position to next x or y-side
            sideDistX = 0
            sideDistY = 0

            #length of ray from one x or y-side to next x or y-side
            tempDirX = (rayDir.x * rayDir.x)
            tempDirY = (rayDir.y * rayDir.y)

            tempDirX = self.avoid_zero(tempDirX)
            tempDirY = self.avoid_zero(tempDirY)

            deltaDistX = math.sqrt(1 + (rayDir.y * rayDir.y) / tempDirX)
            deltaDistY = math.sqrt(1 + (rayDir.x * rayDir.x) / tempDirY)
            perpWallDist = 0

            #what direction to step in x or y-direction (either +1 or -1)
            stepX = 0
            stepY = 0

            hit = False #was there a wall hit?
            side = Side.LeftOrRight #was a NS or a EW wall hit?

          #calculate step and initial sideDist
            if rayDir.x < 0:
                stepX = -1
                sideDistX = (rayPosition.x - mapX) * deltaDistX
       
            else:
                stepX = 1
                sideDistX = (mapX + 1.0 - rayPosition.x) * deltaDistX
       
            if rayDir.y < 0:
                stepY = -1
                sideDistY = (rayPosition.y - mapY) * deltaDistY
       
            else:    
                stepY = 1
                sideDistY = (mapY + 1.0 - rayPosition.y) * deltaDistY

            #perform DDA
            while (hit == False):
        
                #jump to next map square, OR in x-direction, OR in y-direction
                if (sideDistX < sideDistY):
                    sideDistX += deltaDistX
                    mapX += stepX
                    side = Side.LeftOrRight
            
                else:
                    sideDistY += deltaDistY
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

        self.draw_ui()

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
            pygame.draw.rect(self.SCREEN, colors.SKY_BLUE, (0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT/2))

            self.simulate(player)
            self.render(player)

			#delay until next frame.
            clock.tick(self.TARGET_FPS)
            self.fps = int(clock.get_fps())

        pygame.quit()

