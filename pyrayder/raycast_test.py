#imports
import math
import colors
import pygame
import vector

#CONSTANTS
DEGREES_IN_A_CIRCLE = 360

FRAME_SPEED = int(1000 / 60) #frame time for 1000 / N fps, 33.3 for 30 fps and 16.6 for 60fps.
CIRCLE_RADIUS = 100

CIRCLE = math.pi * 2
VIEW_DISTANCE = 1

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 400

CIRCLE_X = int(SCREEN_WIDTH/2)
CIRCLE_Y = int(SCREEN_HEIGHT/2)

ONE_DEGREE_IN_RADIANS = math.pi / 180

#pygame/visual initialization
pygame.init()
size = (SCREEN_WIDTH, SCREEN_HEIGHT)
screen = pygame.display.set_mode(size)

#default the angle to 0.
angle = 0

vec = vector.Vector2()

#create a font
myfont = pygame.font.SysFont("monospace", 24)
myfont.set_bold(True)

#hacky program loop.
done = False
while not done:

	#delay until neXt frame.
    pygame.time.wait(FRAME_SPEED)


	#covert the angle from degrees to radians.
    rad_angle = ONE_DEGREE_IN_RADIANS * angle

	#fill the screen background
    screen.fill(colors.RED)

	#print the angle
    label = myfont.render("angle: " + str(angle), 1, colors.YELLOW)
    screen.blit(label, (5,5))

	#handle input
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            done=True # Flag that we are done so we eXit this loop
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                angle -= 5
            if event.key == pygame.K_RIGHT:
                angle += 5


	#clamp the angle to a positive value
    angle %= DEGREES_IN_A_CIRCLE

    #draw a big circle in the middle of the screen for reference.
    pygame.draw.circle(screen, colors.YELLOW, [CIRCLE_X, CIRCLE_Y], CIRCLE_RADIUS)

	#calculate the co-ords of the edge of the circle given the angle.
	#cos(angle) gives us the X position in a unit circle, and sine gives us the y.

    X = math.cos(rad_angle)
    Y = math.sin(rad_angle)

    X_POS = int(X * CIRCLE_RADIUS)
    yPos = int(Y * CIRCLE_RADIUS)

    XPos2 = int(X * (CIRCLE_RADIUS/2))
    yPos2 = int(Y * (CIRCLE_RADIUS/2))

	#draw a circle at origin of big circle, in the middle and at edge according to the given angle.
    small_radius = 10
    
    pygame.draw.circle(screen, colors.BLUE, [CIRCLE_X, CIRCLE_Y], small_radius)

    pygame.draw.circle(screen, colors.BLUE, [CIRCLE_X + XPos2, CIRCLE_Y + yPos2], small_radius)

    pygame.draw.circle(screen, colors.BLUE, [CIRCLE_X + X_POS, CIRCLE_Y + yPos], small_radius)

	#print the angle we retrieved from the cos calculation.
    X_pos_unit = math.cos(rad_angle)
    rads = math.acos(X_pos_unit)
    newDegs = int(rads / ONE_DEGREE_IN_RADIANS)

    y_pos_unit = math.sin(rad_angle)
    rads2 = math.asin(y_pos_unit)
    newDegs2 = int(rads2 / ONE_DEGREE_IN_RADIANS)

    label2 = myfont.render("acos angle: " + str(newDegs), 1, colors.YELLOW)
    screen.blit(label2, (5,25))

    label3 = myfont.render("asin angle: " + str(newDegs2), 1, colors.YELLOW)
    screen.blit(label3, (5,45))

	# Go ahead and update the screen with what we've drawn.
    # This MUST happen after all the other drawing commands.
    pygame.display.flip()

#quit game
pygame.quit()
