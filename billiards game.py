''' known issues
--randomly crashes when degrees is not set. 
-fix??: <= 360. 360 laid between more than and less than and the interpreter didn't know what to do with that. more testing may be needed.
-- the cuestick moved in a sort of sin wave formation. 
-fix: using a polygon and adjusting its coordinates to mimic that of a rectangle that was rotating around the shape.
-- the cuestick would not move/crash
- fix: no while loops and initialising the class outside of the movemode.'''
'make it move'
import pygame
import time
import math
import pymunk
import pymunk.pygame_util
# pygame setup
time1 = time.time() 
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
rect_1 = pygame.Rect(550,114,217,478,width = 15, border_radius = 15) # rect takes (x,y,width,height)
## for the sake of translation of board shapes.
moveinx = 503
moveinx2 = moveinx - 170
moveinx3 = moveinx - 176 # for left sided traps
moveiny = 185
moveiny2 = -250 # for bottom sided traps
#initialise variables
backgroundColour = "purple" # edit this value to change screen.fill
count = 0 
cx = 550 + 105 # centre of circle x coordinate
cy = 130 + 112 # centre of circle y coordinate
radius = 6
g = 9.81
ballMass = 0.170097 #mass of ALL balls
cueStickMass = 0.539
##MAY NEED TO CHANGE
u0 = 0.6 # coefficient of friction between tip and ball. the static friction this creates needs to be overcome for the ball to move.
u1 = 0.2 # coefficient of friction between ball and cloth. the kinetic friction this creates is constant and when this is equal to the driving force, no acceleration occurs.
u2 = 0.03 # coefficient of friction between ball and ball. the static friction this creates needs to be overcome for the other ball to move.
nf1 = ballMass*g # normal force for the balls.
kineticFriction = nf1 * u1 # 100 is the placeholder value for the unit of measurement conversion from metres to pixels
staticFriction = nf1 * u0 #MAY NEED TO CHANGE THIS the maximum static friction i.e. the force that needs to be overcome for the balls to move. 
##MAY NEED TO CHANGE
# velocity of cuestick for certain shots
conversionFactor = 500
softV = 1.4 * conversionFactor
mediumV = 2.2 * conversionFactor
fastV = 4.5 * conversionFactor
breakV = 6 * conversionFactor
doOnce = True 
hit = False
## stores the coordinates for all the walls that need collision shapes (or to make certain shapes look like they have collision shapes)
rects = [
    (550,114,15,470), #left rect
    (550+204,114,15,470), # right rect
    (550,114+470,217,15), # bottom rect
    (550,114,217,15) # top rect
]
# from left to right, top right, top left, bottom left, bottom right for the points of the trapezium
polygons = [((238 + moveinx,395),(238 + moveinx,516.5),(250 + moveinx,545),(250 +  moveinx,371.5)),
            ((238 + moveinx,141.99 + 40),(238+moveinx,217+80),(250 + moveinx,272.5 + 52),(250 +  moveinx,197.5-35)),
            ((375 + moveinx2,326-moveiny),(278+moveinx2,326-moveiny),(266+moveinx2,(324.5 - 10)-moveiny),(387 + moveinx2 ,(324.5 - 10)-moveiny)),
            # these traps below are parallel and therefore are, bottom left, bottom right, top left, top right
            ((238 + moveinx3,197.5-35),(238+moveinx3, 272.5 + 52),(250 + moveinx3,217+80),(250 +  moveinx3, 141.99 + 40)),
            (((238 + moveinx3,371.5),(238 + moveinx3,545),(250 + moveinx3, 516.5),(250 +  moveinx3, 395))),
            (((387 + moveinx2,326-moveiny2),(266+moveinx2,326-moveiny2),( 278+moveinx2,(324.5 - 10)-moveiny2),( 375 + moveinx2,(324.5 - 10)-moveiny2)))
    ]
space = pymunk.Space()
space.damping = 0.2 # placeholder value. this is for friction.
# making the rigid body for the balls
## dynamic bodies react to collisions and can have forces acting on it.
# make 10 of these, with center of ball being THEIR respective center.
# attach a circle collision shape to each of them.
class Balls():
    def __init__(self, cx = 0, cy = 0, velocity = pygame.math.Vector2(0,0), displacement = [0,0],ballNumber = 0):
        self.cx = cx
        self.cy = cy
        self.velocity = velocity
        self.displacement = displacement
        self.ballNumber = ballNumber
        self.body = pymunk.Body(mass = ballMass,moment = (pymunk.moment_for_circle(ballMass,0,radius)))
        self.body.position = (self.cx,720 - self.cy) # 720 is the height of the screen, since pymunk calculates its coordinates from bottom left, while pygame does it from top left.
        self.collisionShape = pymunk.Circle(self.body, radius)
        self.collisionShape.density = 1 # may be an issue with speed of the ball.
        self.collisionShape.elasticity = 1        
        self.collisionShape.collision_type = ballNumber # so that multiple balls can have different collision logics.
        space.add(self.body, self.collisionShape)
    def getMagnitude(self): # the euclidean magnitude to get a hypotenuse that can then be trig'd on to find corresponding vx and vy
        magnitude = self.velocity.magnitude()
        return magnitude 
    def getVx(self): # velocity in the x direction
        vx = self.velocity[0]
        return vx 
    def getVy(self): #velocity in the y direction
        vy = self.velocity[1]
        return vy
    def updateBodyPosition(self):
        self.body.position = (self.cx, 720-self.cy)
    
#initialises numbered balls so they can be editted.
ball = [Balls() for _ in range(10)]
for i in range(9):
    ball[i].ballNumber = i + 1 # so that the numbered balls have their correct number and the cueball is just ball 0.
    ball[i].collisionShape.collision_type = i + 1
    print("Ball number is",ball[i].ballNumber, "for", i) # debug code.

# initialises cueball so tbhey can be editted.
cueBall = Balls(cx,cy,ballNumber = 0)
# to make the simulation work.
space.gravity = (0,0) # change gravity value later if this an issue. 

# to check for collisions
def collide(arbiter,space,data):
    global hit
    print("collision successful")
    hit = True
    return True


## for multiple collisions
handlers = [space.add_collision_handler(0, i+1) for i in range(0,9)] # use this when you need to process a collision. these collision types are placeholder values (the collision between cueball and the 1 ball)
for i, handler in enumerate(handlers):
    handler.begin = collide

#segment walls here.
#draw the segment walls
segment_body = pymunk.Body(body_type=pymunk.Body.STATIC)
pymunk.pygame_util.positive_y_is_up = True # to draw it in the pymunk way whic is the way it initialises the bodies.
'''cushion = pymunk.Segment(segment_body,(238+moveinx, 516.5), (238+moveinx,395), radius = 1)'''
cushion = [0]*len(polygons) # initialise this so it makes sense in the code below.
space.add(segment_body)
## adding cushions
for h in range(0,3):
        if h == 0:
            for i in range(len(polygons)):
                #1st refers to what shape, 2nd refers to what set of coords, 3rd refers to whether its x or y
                cushion[i] = pymunk.Segment(segment_body,(polygons[i][0][0], 720 - polygons[i][0][1]),(polygons[i][1][0], 720 - polygons[i][1][1]), radius = 1)
                
                if i >= 3:
                    cushion[i] = pymunk.Segment(segment_body,(polygons[i][2][0], 720 - polygons[i][2][1]),(polygons[i][3][0],720 - polygons[i][3][1]),radius = 1)
                
                cushion[i].elasticity = 1 # temp value
                space.add(cushion[i])
        if h == 1: # adds top right to bottom right
            for i in range(len(polygons)):
                #1st refers to what shape, 2nd refers to what set of coords, 3rd refers to whether its x or y
                cushion[i] = pymunk.Segment(segment_body,(polygons[i][0][0],720 - polygons[i][0][1]),(polygons[i][3][0],720 - polygons[i][3][1]), radius = 1)
                
                if i >= 3:
                    cushion[i] = pymunk.Segment(segment_body,(polygons[i][3][0],720 - polygons[i][3][1]),(polygons[i][0][0],720 - polygons[i][0][1]),radius = 1)
                
                cushion[i].elasticity = 1 # temp value
                space.add(cushion[i])
        if h == 2: # adds top left to bottom left
            for i in range(len(polygons)):
                #1st refers to what shape, 2nd refers to what set of coords, 3rd refers to whether its x or y
                cushion[i] = pymunk.Segment(segment_body,(polygons[i][1][0],720 - polygons[i][1][1]),(polygons[i][2][0],720 - polygons[i][2][1]), radius = 1)
            
                if i >= 3:
                    cushion[i] = pymunk.Segment(segment_body,(polygons[i][2][0],720 - polygons[i][2][1]),(polygons[i][1][0],720 - polygons[i][1][1]),radius = 1)
                
                cushion[i].elasticity = 1 # temp value
                space.add(cushion[i])
#rail drawing
rail = [0]*len(rects)
for i in range(0,len(rail), 2):
    #constants are to translate it in the right place. radius is 3 because this is the sweet spot for the constants to put them in accurate positions.
    #translates them individually
    print(i)
    rail[i] = pymunk.Segment(segment_body,(rects[i][0] + 10,720 - rects[i][1]),(rects[i][0] + 10, 720 - (rects[i][1] + rects[i][3])),radius = 3)
    rail[i + 1] = pymunk.Segment(segment_body,(rects[i + 1][0] + 4,720 - rects[i + 1][1]),(rects[i + 1][0] + 4,720 - (rects[i+1][1] + rects[i][3])),radius = 3)
    if i == 2:
        rail[i] = pymunk.Segment(segment_body,(rects[i][0],720 - (rects[i][1] - 6)),(rects[i][0] + rects[i][2],720 - (rects[i][1] - 6)),radius = 3)
        rail[i + 1] = pymunk.Segment(segment_body,(rects[i+1][0],720 - (rects[i+1][1] + 10)),(rects[i+1][0] + rects[i+1][2],720 - (rects[i+1][1] + 10)),radius = 3)
    
    rail[i].elasticity = 1 # temp value
    rail[i+1].elasticity = 1
    space.add(rail[i])
    space.add(rail[i +1])
draw_options = pymunk.pygame_util.DrawOptions(screen)
####
#HANDLES UPDATING EACH OF THE BALL'S MOVEMENT WHEN COLLIDED WITH
####
def drawOtherBalls(): # only run to change the balls/draw the balls once as the images need to be drawn over them every time this is ran.
    #initialising local variables
    global ball
    global doOnce
    global hit
    radius = 6
    displayedBall = [0]*9
    if doOnce == True:
        cy = 326 + 142.24
        cx = 550+105 # issue could appear here where the balls don't move.
        tby = 8 # translate by to make them all diagonal to oneanother.
        
        

        #drawing the balls
        displayedBall[0] = pygame.draw.circle(screen,"khaki1",center = (cx,cy), radius = radius) # number 1
        displayedBall[1] = pygame.draw.circle(screen,"blue3",center = (cx - tby,cy + tby),radius = radius) # number 2
        displayedBall[2] = pygame.draw.circle(screen,"brown1",center = (cx+tby,cy+tby),radius = radius) # number 3
        displayedBall[3] = pygame.draw.circle(screen,"blue4",center = (cx - (2*tby), cy + (2*tby)),radius = radius) # number 4
        displayedBall[8] = pygame.draw.circle(screen, "gold",center = (cx, cy + (2*tby)),radius = radius) # number 9
        displayedBall[4] = pygame.draw.circle(screen,"orangered1",center = (cx + (2*tby), cy + (2*tby)), radius = radius) # number 5
        displayedBall[5] = pygame.draw.circle(screen, "palegreen4",center = (cx - (tby), cy + (3*tby)),radius = radius) # number 6
        displayedBall[6] = pygame.draw.circle(screen, "red4",center = (cx + (tby), cy + (3*tby)),radius = radius)# number 7
        displayedBall[7] = pygame.draw.circle(screen,"black",center = (cx, cy + (4*tby)),radius = radius) # number 8
        for i in range(0,9):
            # cx and cy transfers this coordinates to either the updating state (to ensure they move) or the displaying state (to ensure they're being drawn).
            ball[i].cx = displayedBall[i].center[0]
            ball[i].cy = displayedBall[i].center[1]
            ball[i].updateBodyPosition()
        
        #initialise the individual's ball's speed
        for i in range(10):
            ball[i].velocity = pygame.math.Vector2(0,0)
        
       
        doOnce = False
    elif doOnce == False:
        displayedBall[0]  =pygame.draw.circle(screen,"khaki1",center = (ball[0].cx,ball[0].cy), radius = radius) # number 1
        displayedBall[1] = pygame.draw.circle(screen,"blue3",center = (ball[1].cx,ball[1].cy),radius = radius) # number 2
        displayedBall[2] = pygame.draw.circle(screen,"brown1",center = (ball[2].cx,ball[2].cy),radius = radius) # number 3
        displayedBall[3] = pygame.draw.circle(screen,"blue4",center = (ball[3].cx, ball[3].cy),radius = radius) # number 4
        displayedBall[8] = pygame.draw.circle(screen, "gold",center = (ball[8].cx, ball[8].cy),radius = radius) # number 9
        displayedBall[4] = pygame.draw.circle(screen,"orangered1",center = (ball[4].cx, ball[4].cy), radius = radius) # number 5
        displayedBall[5] = pygame.draw.circle(screen, "palegreen4",center = (ball[5].cx, ball[5].cy),radius = radius) # number 6
        displayedBall[6] = pygame.draw.circle(screen, "red4",center = (ball[6].cx, ball[6].cy),radius = radius)# number 7
        displayedBall[7] = pygame.draw.circle(screen,"black",center = (ball[7].cx, ball[7].cy),radius = radius) # number 8
    if hit == False:
        for i in range(0,9):
            ball[i].updateBodyPosition()
    # balls = the surface version of each of these balls.
    # drawnballs is the drawn version of these balls.
    balls = [0, 0, 0, 0, 0, 0, 0,0,0]
    drawnBalls = [displayedBall[0],displayedBall[1],displayedBall[2],displayedBall[3],displayedBall[4],displayedBall[5],displayedBall[6],displayedBall[7],displayedBall[8]]
    for i in range(len(balls)):
        balls[i] = pygame.Surface((12,12),pygame.SRCALPHA)
        balls[i].fill((255,255,255,0))
        drawnBalls[i] = balls[i].get_rect(center = drawnBalls[i].center)
        screen.blit(balls[i], drawnBalls[i],special_flags = pygame.BLEND_RGBA_MULT)
        
    
    return drawnBalls

####### 
#REDUNDANT MODULE. ONLY USED FOR THE OLD RECOMPUTING OF CENTERS WHEN THE BALL IS MOVING.
#######
def updateBalls(drawnBalls):
    global ball
    displayedBall = [0]*10
    # update every balls cx and cy, before drawing them
    displayedBall[1]  =pygame.draw.circle(screen,"khaki1",center = (ball[0].cx,ball[0].cy), radius = radius) # number 1
    displayedBall[2] = pygame.draw.circle(screen,"blue3",center = (ball[1].cx,ball[1].cy),radius = radius) # number 2
    displayedBall[3] = pygame.draw.circle(screen,"brown1",center = (ball[2].cx,ball[2].cy),radius = radius) # number 3
    displayedBall[4] = pygame.draw.circle(screen,"blue4",center = (ball[3].cx, ball[3].cy),radius = radius) # number 4
    displayedBall[9] = pygame.draw.circle(screen, "gold",center = (ball[8].cx, ball[8].cy),radius = radius) # number 9
    displayedBall[5] = pygame.draw.circle(screen,"orangered1",center = (ball[4].cx, ball[4].cy), radius = radius) # number 5
    displayedBall[6] = pygame.draw.circle(screen, "palegreen4",center = (ball[5].cx, ball[5].cy),radius = radius) # number 6
    displayedBall[7] = pygame.draw.circle(screen, "red4",center = (ball[6].cx, ball[6].cy),radius = radius)# number 7
    displayedBall[8] = pygame.draw.circle(screen,"black",center = (ball[7].cx, ball[7].cy),radius = radius) # number 8
    balls = [0, 0, 0, 0, 0, 0, 0,0,0]
    drawnBalls = [displayedBall[1],displayedBall[2],displayedBall[3],displayedBall[4],displayedBall[5],displayedBall[6],displayedBall[7],displayedBall[8],displayedBall[9]] # potential error here where the 9 ball gets overlayed by the other balls.
    for i in range(len(balls)):
        balls[i] = pygame.Surface((12,12),pygame.SRCALPHA)
        balls[i].fill((255,255,255,0))
        drawnBalls[i] = balls[i].get_rect(center = drawnBalls[i].center)
        screen.blit(balls[i], drawnBalls[i],special_flags = pygame.BLEND_RGBA_MULT)
    return drawnBalls
# checks for a collision with each of the balls. stores the collided balls into changeBalls using the list of indexes that the function collidelistall would return.
# this would then run some sort of motion logic to move the balls depending on the angle hit by them by the cueball (akin to how the cueball is hit by the cuestick)



# initialises the board as a background.
def drawBoard():
    # draws pool table
    #550 = x, y = 130, 210 = width, 460 = height
    pygame.draw.rect(screen, (0, 100, 0),[550,130,210,460],width = 0,border_radius = 15) #draws slate

    #drawing pockets because they'll be under the table outline.
    
    #adjust railings to accomodate new radius (original values were diameters not radii)
    #drawing pockets
    pygame.draw.circle(screen,"black",(576.88,566.5),26/1.5) # bottom left pocket
    pygame.draw.circle(screen,"black",((576.88 + 217) - 52,566.5),24/1.5) # bottom right pocket
    pygame.draw.circle(screen,"black",(576.88 - 9,566.5 - 217),26.8/1.5) # middle left pocket
    pygame.draw.circle(screen,"black",((576.88 + 226) - 52,566.5 - 217),26.8/1.5) # middle right pocket'''
    pygame.draw.circle(screen,"black",(576,141.99),26/1.5) # top left pocket
    pygame.draw.circle(screen,"black",((576 + 217) - 52,141.99),24/1.5) # top right pocket

    
    pygame.draw.rect(screen, (0,0,255),[550,114,217,478],width = 15,border_radius = 15) #draws table outline
    
    # from left to right, top right, top left, bottom left, bottom right for the points of the trapezium
    #drawing traps up and down the board.
    #this first one is between bottom right corner and mid right side 
    pygame.draw.polygon(screen,"green", points = [(238 + moveinx,395),(238 + moveinx,516.5),(250 + moveinx,545),(250 +  moveinx,371.5)])
    #second trap, between mid right side and top right + move in x keeps the alignment with the first trap in the x axis. 
    pygame.draw.polygon(screen,"green", points = [(238 + moveinx,141.99 + 40),(238+moveinx,217+80),(250 + moveinx,272.5 + 52),(250 +  moveinx,197.5-35)])
    #third trap, between top right and top left.
    pygame.draw.polygon(screen,"green", points = [(375 + moveinx2,326-moveiny),(278+moveinx2,326-moveiny),(266+moveinx2,(324.5 - 10)-moveiny),(387 + moveinx2 ,(324.5 - 10)-moveiny)])
    #parallel traps. to flip it in the x direction, swap the top and bottom y's with their corresponding direction (top left's y swaps with bottom right's y)
    #parallel to first trap
    pygame.draw.polygon(screen,"green", points = [(238 + moveinx3,371.5),(238 + moveinx3,545),(250 + moveinx3, 516.5),(250 +  moveinx3, 395)])
    #parallel to second trap
    pygame.draw.polygon(screen,"green", points = [(238 + moveinx3,197.5-35),(238+moveinx3, 272.5 + 52),(250 + moveinx3,217+80),(250 +  moveinx3, 141.99 + 40)])
    #parallel to third trap
    pygame.draw.polygon(screen,"green", points = [(387 + moveinx2,326-moveiny2),(266+moveinx2,326-moveiny2),( 278+moveinx2,(324.5 - 10)-moveiny2),( 375 + moveinx2,(324.5 - 10)-moveiny2)])


    
    
#speed of ball
 # speed in x, speed in y
'think about using classes for individual balls'

#initialising the ball
displayedCueBall = pygame.draw.circle(screen,(255,255,255), center = (cx,cy), radius = 6)

# handles how the balls move after being hit by either the cueball or by the cuestick.
def motionLogic(vType,massType,dx,dy,degrees):
    global hit
    hit = False
    motionExists = True
    while motionExists == True:
        conversionFactor = 100 # used to convert the metres to pixels.
        def convertValues(value, conversionFactor = conversionFactor):
            convertedValue = value * conversionFactor
            return convertedValue
        ### reduces distance in exchange for limiting speed and thereby possible collision tunneling. 
        def limitVelocity(speed): 
            max_speed = 20
            if speed > max_speed:
                'speed = math.sqrt(speed)'
                speed = max_speed
                return speed
            elif speed < max_speed:
                speed = speed
                return speed
        global cx
        global cy
        global displayedCueBall
        #n your sprite, define the Surface (with a transparent background) for Block.image, draw the polygon into that surface
        ##The surface alpha value is a single value that changes the transparency for the entire image. A surface alpha of 255 is opaque, and a value of 0 is completely transparent.
        ballSurface = pygame.Surface((12,12),pygame.SRCALPHA)
        ### hand coded physics
        t = space.current_time_step + 1
        ballSurface.fill((255,255,255,0))

        # generate an impulse that moves the cueball depending on where you hit the cueball at.
         # work the impulse out myself first, because this is the impulse being applied.
        # the resulting collisions should cause the cueball to slow down due to friction and bounce back. 
        cueBall.cx = cueBall.body.position[0]
        cueBall.cy = 720 - cueBall.body.position[1] # otherwise the cueBall is mapped to the top of the numbered balls. 
        pygame.draw.circle(ballSurface,(255,255,255), center = (6,6), radius = 6)
        displayedCueBall = ballSurface.get_rect(center = (cueBall.cx, cueBall.cy))
        screen.blit(ballSurface, displayedCueBall,special_flags = pygame.BLEND_RGBA_MULT) 
        #initialising the variables
        
        

        ##handcoded physics

        'displayedCueBall = displayedCueBall.move(displacement)' # this moves the circle
        screen.blit(screen,(0,0))
        position = list(displayedCueBall.center) # this moves the rect form of the circle for blit to work
        screen.blit(ballSurface, position)
        drawnBalls = drawOtherBalls() # holds the get_rects, to check for collisions and move them
        drawnBallPosition = []
        print("Ball coords are",cueBall.cx, cueBall.cy)
        for i in range(len(drawnBalls)):
            drawnBallPosition.append(drawnBalls[i])
        pygame.display.update()
        
        cueBall.body.apply_impulse_at_world_point(((-dx)*massType*vType*conversionFactor,(dy)* massType *vType*conversionFactor),(0,(720 - cy))) # -dx to make it act in the correct direction, though this body coordinate may be irrelevant.
        
        for x in range (100): # animation takes place over 100 frames. 
            
            screen.fill(backgroundColour) 
            drawBoard()
            
            
            ## hand-coded physics
            
            clock.tick(60)
            space.step(1/60)
            
            cueBall.cx = cueBall.body.position[0]
            cueBall.cy = 720 - cueBall.body.position[1] # otherwise the cueBall is mapped to the top of the numbered balls. 
            #update the cue ball's new coordinates here
            displayedCueBall = ballSurface.get_rect(center = (cueBall.cx, cueBall.cy))
            
            #detect collision here, because the ball is moving here.
            
            collision = collide
            
            if hit == True: # base displacement is used to make the ball's current position 0,0 and everything else an offset of that. 
                # the balls should each follow the coordinates of their body position
                # the balls should move in the way that pymunk wants them to.
                #PYMUNK IS HANDLING THE MOVEMENT OF THE BALLS BY TYING THE BODY POSITION TO THE BALL'S MOVEMENT COORDINATES. 720 IS USED AS THE Y AXIS OF THE RESOLUTION.
                for i in range (0,9):
                    ball[i].cx = ball[i].body.position.x
                    ball[i].cy = 720  - ball[i].body.position.y
                    ball[i].updateBodyPosition()
                drawOtherBalls()
                
                
            screen.blit(ballSurface, displayedCueBall) # necessary for the smooth animation. 
            drawnBalls = drawOtherBalls()
            pygame.display.update()
                #move at the same/similar angle to when it collided. recalculate displacement here
                # from the point it makes the collision
        ##contingency code
        '''pygame.draw.circle(screen,(255,255,255),center = displayedCueBall.center,radius = 6)
        screen.blit(displayedCueBall, displayedCueBall)
        pygame.display.update()'''
        # MAKE SURE TO UPDATE THIS SO THAT THE CUESTICK IS IN THE RIGHT PLACE
        cx = cueBall.cx
        cy = cueBall.cy 
        motionExists = False
class Point:
        def __init__(self,x= 0, y = 0):
            self.x = x
            self.y = y
# creating a class for the ball physics logic



## creating a move mode
### if left mouse button hasn't been pressed, then move mode is passed.
def moveMode():
    '''
    #issue checklist
    is the issue in regards to the loop? <-- This one.  '''
    ''' To explain: this code will still run infinitely, so no while loop is needed. In its place, just conditionals are fine.
    Why? Probably because of the while loop at the start. It'll just keep running through the code as long as the program is running'''
    global cx
    global cy 
    #initialise some variables
    # this code is necessary to be able to refer to each vertex with []
    v = [Point() for _ in range(4)]
    ## get pos, gets position of mouse pointer on screen. [1] = y, [0] = x. access each as you would with a list type.
    pos = pygame.mouse.get_pos()
    # as the user moves their mouse up or down, the more they increase or decrease degrees up to a max of 360 and a minimum of 0
    if pos[1] > 360:
        degrees = pos[1]/360
    
    elif pos[1] <= 360:
        degrees = pos[1]
    #for the sake of ease when copying and pasting this guy's code (guy on stackoverflow)
    dx = math.sin(degreesToRadians(degrees))
    dy = math.cos(degreesToRadians(degrees))
    if pygame.mouse.get_pressed()[0]:
        ## making the cue stick acting along the gradient of the circle's center and the points of its edge
        
        

        #getting the points of a circle's circumference.
        tx = cx + (radius*dx)
        ty = cy + (radius*dy)
        w = 10
        h =324.8
        
        ## drawing the cue stick, and it moves by changing its attributes by affecting tx through changing dy and dx.
        
        v[0].x = tx + dy * w/2
        v[0].y = ty - dx * w/2

        v[1].x = v[0].x + dx * h
        v[1].y = v[0].y + dy * h

        v[2].x = v[1].x - dy * w
        v[2].y = v[1].y + dx * w

        v[3].x = tx - dy * w/2
        v[3].y = ty + dx * w/2
        ''' will have to use polygon '''
        pygame.draw.polygon(screen,"antiquewhite3",[(v[0].x, v[0].y), (v[1].x,v[1].y),(v[2].x,v[2].y),(v[3].x,v[3].y)])
        
    elif event.type == pygame.MOUSEBUTTONUP:
        pygame.time.delay(500)
        hitMode(dx,dy,degrees)
        
def hitMode(dx,dy,degrees):
    global time1
    global count
    powerRects = pygame.Rect(cx+150,cy,10,50) # 200 is an arbitrary value. feel free to change the width and the height.
    rect1 = powerRects.copy()
    def reset():
        global time1
        global count
        time1 = time.time()
        count = 0
    w = 10
    h = 324.8
    # lock the position of the cue stick
    # only allow it to move up and down
    base = [Point() for _ in range(4)]
    tx = cx + (radius*dx)
    ty = cy + (radius*dy)
    base[0].x = tx + dy * w/2
    base[0].y = ty - dx * w/2

    base[1].x = base[0].x + dx * h
    base[1].y = base[0].y + dy * h

    base[2].x = base[1].x - dy * w
    base[2].y = base[1].y + dx * w

    base[3].x = tx - dy * w/2
    base[3].y = ty + dx * w/2
    # set the mouse position to the center of the ball, then let them move left and right to move cue stick. they can only move it a certain amount until the cue stick is locked, and they can only go down. the opposite is true.
    # hold left mouse button, bars will show up. the longer you hold it, the more bars will show up and therefore more power. right click to stop OR when you get to the forth bar, it will decrease in bars.
    # while loop so long as LMB is pressed. have a counter that counts up for each rect, then counts down when they disappear.
    event = pygame.event.poll()
    if pygame.mouse.get_pressed()[2] == True:
            
            timereduction = 8
             #initialise a stopwatch. use this stopwatch as a condition for the other rects to appear.
            translation = 15 # moves each subsequent bar from the first by 50 to the right. use pygame.rect.move
            SDP = time.time() - time1 
            # initialise rect to the one of the sides of the centre of the ball.
            pygame.draw.rect(screen,"brown2",powerRects)
            
            if SDP >= (10 - timereduction):
                rect1.move_ip(translation,0)
                pygame.draw.rect(screen,"brown2",rect1)
                count = 1
                rect2 = rect1.copy()
            if SDP >= (12 - timereduction):
                rect2.move_ip(translation,0)
                pygame.draw.rect(screen,"brown2",rect2)
                count = 2
                rect3 = rect2.copy()
            if SDP >= (14 - timereduction):
                rect3.move_ip(translation,0) 
                pygame.draw.rect(screen,"brown2",rect3)
                count = 3
            if (count >= 3) and (SDP >= (16-timereduction)): # to delete them and go back down
                pygame.draw.rect(screen,backgroundColour,rect3)
                count = 2
                if SDP >= (18-timereduction):
                    count = 1
                    pygame.draw.rect(screen,backgroundColour,rect2)
                if SDP >= (20-timereduction):
                    pygame.draw.rect(screen,backgroundColour,rect1)
                    count = 0
                    time1 = time.time() # to reset the clock.
            print(SDP) # for debugging
    elif event.type == pygame.MOUSEBUTTONUP:
        print("Count is", count)
        match count:
            case 0:
                motionLogic(softV,cueStickMass,dx,dy,degrees) # cue stick mass is used in this case because it's the thing causing it to move. it's transferring everything to cueball.
                reset()
            case 1:
                motionLogic(mediumV,cueStickMass,dx,dy,degrees)
                reset()
            case 2:
                motionLogic(fastV,cueStickMass,dx,dy,degrees)
                reset()
            case 3:
                motionLogic(breakV,cueStickMass,dx,dy,degrees)
                reset() 
        
    # the ball moves in the direction of where the cuestick hit it.
'call a function here to calculate how the ball moves after being hit. this is after the while loop finishes btw'
'motionLogic(breakV, cueStickMass)'

#conversion from degrees to radians
def degreesToRadians(degrees):
    radians = degrees * ((math.pi)/180)
    return radians

#game loop
while running: 
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill(backgroundColour)

    # RENDER YOUR GAME HERE
    
    #drawing headstring
    #(head string is quarter the way down of the slate, so 112.75 which is a quarter of 451 (accurate height of slate). an accurate height for the slate would be the height of the table outline - its width - 12 (height of cushion) (as it goes from cushion
    pygame.draw.line(screen,(0,0,0),(550, 130 + 112.75),(550 + 210, 130 + 112.75),width = 0)
    #drawing the ball
    #105 is half the width of the headstring (the bottom of the break box where the player is allowed to put their ball)
    #draw antialiased ball so it looks less like a diamond, may change later. 
    #x as an int, then y as an int, r is also an int instead of a keyword argument, colour comes after everything else.
    '''pygame.gfxdraw.aacircle(screen,(550 + 105),130 + 112,6,(255,255,255))
    pygame.gfxdraw.filled_circle(screen,(550+105),(130+112),6,(255,255,255))'''
    # draws the board complete with pockets, rails and cushions
    drawBoard()
    #draws the balls
    pygame.draw.circle(screen,(255,255,255), center = displayedCueBall.center, radius = 6)
    #draws the numbered balls
    drawOtherBalls()
    #space.debug_draw(draw_options) (this is for debug)
    #to move the cuestick
    moveMode()
    # flip() the display to put your work on screen
    
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60
    
    
    
pygame.quit()
