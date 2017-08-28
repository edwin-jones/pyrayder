import math
import colors
import pygame
import vector

"""To rotate a vector, multiply it with the rotation matrix

[ cos(a) -sin(a) ]
[ sin(a)  cos(a) ]"""

ONE_DEGREE_IN_RADIANS = math.pi / 180

FRAME_SPEED = int(1000 / 60) #frame time for 1000 / N fps, 33.3 for 30 fps and 16.6 for 60fps.

MAP =   [
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


SCREEN_WIDTH = 400
SCREEN_HEIGHT = 400

FAKE_ZERO = 0.000001


#pygame/visual initialization
pygame.init()



size = (SCREEN_WIDTH, SCREEN_HEIGHT)
screen = pygame.display.set_mode(size)

playerPos = vector.Vector2(2,2)
playerDir = vector.Vector2(1,0)
cameraPlane = vector.Vector2(0,-0.5)

time = 0
oldTime = 0

done = False

WALL_PALETTE = [colors.BLACK, colors.WHITE, colors.RED, colors.GREEN, colors.BLUE, colors.YELLOW]

#use this function to avoid zero if we risk a divide by zero expression.
def Avoid_Zero(value):
    if value == 0:
        return FAKE_ZERO
    else:
        return value

while not done:

    #delay until next frame.
    pygame.time.wait(FRAME_SPEED)

    screen.fill(colors.FLOOR_GRAY)

    pygame.draw.rect(screen, colors.SKY_BLUE, (0,0, SCREEN_WIDTH, SCREEN_HEIGHT/2))

    rotSpeed = 0.25 #rotation speed is defined as squares per second.
    movSpeed = 0.25 #move speed is defined as squares per second.

    #handle input
    for event in pygame.event.get():

        #quit if user presses exit
        if event.type == pygame.QUIT:
            done=True
        
        #handle rotation
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                playerPos.x += playerDir.x * movSpeed
                playerPos.y += playerDir.y * movSpeed
            
            if event.key == pygame.K_DOWN:
                playerPos.x -= playerDir.x * movSpeed
                playerPos.y -= playerDir.y * movSpeed

            if event.key == pygame.K_LEFT:
                #both camera direction and camera plane must be rotated
                oldDirX = playerDir.x
                playerDir.x = playerDir.x * math.cos(rotSpeed) - playerDir.y * math.sin(rotSpeed)
                playerDir.y = oldDirX * math.sin(rotSpeed) + playerDir.y * math.cos(rotSpeed)
                oldPlaneX = cameraPlane.x
                cameraPlane.x = cameraPlane.x * math.cos(rotSpeed) - cameraPlane.y * math.sin(rotSpeed)
                cameraPlane.y = oldPlaneX * math.sin(rotSpeed) + cameraPlane.y * math.cos(rotSpeed)

            if event.key == pygame.K_RIGHT:            
                #both camera direction and camera plane must be rotated
                oldDirX = playerDir.x
                playerDir.x = playerDir.x * math.cos(-rotSpeed) - playerDir.y * math.sin(-rotSpeed)
                playerDir.y = oldDirX * math.sin(-rotSpeed) + playerDir.y * math.cos(-rotSpeed)
                oldPlaneX = cameraPlane.x
                cameraPlane.x = cameraPlane.x * math.cos(-rotSpeed) - cameraPlane.y * math.sin(-rotSpeed)
                cameraPlane.y = oldPlaneX * math.sin(-rotSpeed) + cameraPlane.y * math.cos(-rotSpeed)

    #draw screen
    for x in range(0, SCREEN_WIDTH):
        #calculate ray position and direction
        cameraX = 2 * x / SCREEN_WIDTH - 1 #x-coordinate in camera space
        rayPosX = playerPos.x
        rayPosY = playerPos.y
        rayDirX = playerDir.x + cameraPlane.x * cameraX
        rayDirY = playerDir.y + cameraPlane.y * cameraX

        #which box of the map we're in
        mapX = int(rayPosX)
        mapY = int(rayPosY)

        #length of ray from current position to next x or y-side
        sideDistX = 0
        sideDistY = 0

        #length of ray from one x or y-side to next x or y-side
        tempDirX = (rayDirX * rayDirX)
        tempDirY = (rayDirY * rayDirY)

        tempDirX = Avoid_Zero(tempDirX)
        tempDirY = Avoid_Zero(tempDirY)

        deltaDistX = math.sqrt(1 + (rayDirY * rayDirY) / tempDirX)
        deltaDistY = math.sqrt(1 + (rayDirX * rayDirX) / tempDirY)
        perpWallDist = 0

        #what direction to step in x or y-direction (either +1 or -1)
        stepX = 0
        stepY = 0

        hit = False #was there a wall hit?
        side = 0 #was a NS or a EW wall hit?

      #calculate step and initial sideDist
        if rayDirX < 0:
            stepX = -1
            sideDistX = (rayPosX - mapX) * deltaDistX
       
        else:
            stepX = 1
            sideDistX = (mapX + 1.0 - rayPosX) * deltaDistX
       
        if rayDirY < 0:
            stepY = -1
            sideDistY = (rayPosY - mapY) * deltaDistY
       
        else:    
            stepY = 1
            sideDistY = (mapY + 1.0 - rayPosY) * deltaDistY

        #perform DDA
        while (hit == False):
        
            #jump to next map square, OR in x-direction, OR in y-direction
            if (sideDistX < sideDistY):
                sideDistX += deltaDistX
                mapX += stepX
                side = 0
            
            else:
                sideDistY += deltaDistY
                mapY += stepY
                side = 1
            
            #Check if ray has hit a wall
            if (MAP[mapX][mapY] > 0):
                 hit = True

        #Calculate distance projected on camera direction (oblique distance will give fisheye effect!)
        if (side == 0):
            perpWallDist = (mapX - rayPosX + (1 - stepX) / 2) / rayDirX
        
        else:
            perpWallDist = (mapY - rayPosY + (1 - stepY) / 2) / rayDirY
        
        perpWallDist = Avoid_Zero(perpWallDist)

        #Calculate height of line to draw on screen
        lineHeight = int(SCREEN_HEIGHT / perpWallDist)

        #calculate lowest and highest pixel to fill in current stripe
        drawStart = -lineHeight / 2 + SCREEN_HEIGHT / 2

        if(drawStart < 0):
            drawStart = 0

        drawEnd = lineHeight / 2 + SCREEN_HEIGHT / 2

        if(drawEnd >= SCREEN_HEIGHT):
            drawEnd = SCREEN_HEIGHT - 1

        #choose wall color
        mapColorIndex = MAP[mapX][mapY]

        color = WALL_PALETTE[mapColorIndex]
      
     

        #give x and y sides different brightness
        if (side == 1):
            color = (color[0]/2, color[1]/2, color[2]/2)

      #draw the pixels of the stripe as a vertical line
        pygame.draw.line(screen, color, (x, drawStart), (x, drawEnd))
   

    # Go ahead and update the screen with what we've drawn.
    # This MUST happen after all the other drawing commands.
    pygame.display.flip()

pygame.quit()