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
displayedBall = [0]*9
cueBallPocketed = False
cueBallPlaced = False
foul = False 
## stores the coordinates for all the walls that need collision shapes (or to make certain shapes look like they have collision shapes)
rects = [
    (550,114,15,470), #left rect
    (550+204,114,15,470), # right rect
    (550,114+470,217,15), # bottom rect
    (550,114,217,15) # top rect
]
def getMousePos():
    print(pygame.mouse.get_pos())
# from left to right, top right, top left, bottom left, bottom right for the points of the trapezium

### Pymunk Setup

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
    def __init__(self, cx = 0, cy = 0, velocity = pygame.math.Vector2(0,0), displacement = [0,0],ballNumber = 0, colour = 0):
        self.cx = cx
        self.cy = cy
        self.velocity = velocity
        self.displacement = displacement
        self.ballNumber = ballNumber
        self.colour = colour
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
    def getCollisionShape(self):
        shape = self.collisionShape
        return shape
    
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
def collide(arbiter,space,data): # check this
    global hit
    global cueBallPocketed
    print("collision successful")
    hit = True
    print("the pair of shapes collided with are:",arbiter.shapes)
    if arbiter.shapes[1].collision_type == 10: # only in the case of a collision with the pockets.
        arbiter.shapes[0].body.position = (5000,5000)
        x = arbiter.shapes[0].collision_type
        #space.remove(arbiter.shapes[0])
        print("This numbered shape",x,"will be removed from displayedBall")
        if x != 0: # collision type 0 is the cueball, which isn't included in the displayedBall array
            displayedBall[x - 1] = "pocketed"
        if x == 0:
            cueBallPocketed = True
        
        print("the length of displayedBall is", len(displayedBall)) # debug code
        #assume that the location they're stored in memory is in the order of their making in their class.

    return True
'''def pocketCollision(arbiter,space,data): # detects which bodies are needed, given that separate is false (made contact). 
    pocket =  # comes out with the body of the balls 
    print("pocket is",pocket)
    return False'''
## for multiple collisions
handlers = [space.add_collision_handler(0, i+1) for i in range(0,10)] # use this when you need to process a collision.
for i, handler in enumerate(handlers):
    handler.begin = collide

#to allow the other balls to be pocketed besides the cueball. where cueball has collision handler 0.
for i in range(1,10):
    handlers2 = [space.add_collision_handler(i,10) for i in range(0,10)]

for i, handler in enumerate(handlers2):
    handler.begin = collide

def getShapes():
    shapes = []
    for i in range (0,len(displayedBall)):
        shapes.append(ball[i].getCollisionShape)
        print(ball[i].getCollisionShape)
    return shapes



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

#pockets
pocket_body = pymunk.Body(body_type=pymunk.Body.STATIC)
space.add(pocket_body)

def drawPockets():
    circleCoords = [(576.88, 720 -566.5),((576.88 + 217) - 52, 720 - 566.5), (576.88 - 9,720 - (566.5 - 217)),((576.88 + 226) - 52,720 - (566.5 - 217)),(576,720 - 141.99),((576 + 217) - 52,720 - 141.99)]
    circleRadii = [26/1.5, 24/1.5, 26.8/1.5, 26.8/1.5, 26/1.5, 24/1.5]
    pockets = [] # or circleCoords. they're interchangeable but idk how tuples are counted
    for i in range(0,6):
        #pocket_body.position = (circleCoords[i][0], circleCoords[i][1])
        pockets.append(pymunk.Circle(pocket_body,radius = circleRadii[i],offset = (circleCoords[i][0],circleCoords[i][1])))
        pockets[i].sensor = True
        pockets[i].collision_type = 10
        space.add(pockets[i])
    return pockets
pockets = drawPockets()

draw_options = pymunk.pygame_util.DrawOptions(screen)


### Everything related to rendering something is here. (minus cuestick)

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

    drawBallPocketTracker()


####
#HANDLES UPDATING EACH OF THE BALL'S MOVEMENT WHEN COLLIDED WITH
####
def drawOtherBalls(): # only run to change the balls/draw the balls once as the images need to be drawn over them every time this is ran.
    #initialising local variables
    global ball
    global doOnce
    global hit
    global displayedBall
    radius = 6
    colours = ["khaki1","blue3","brown1","blue4","orangered1","palegreen4","red4","black","gold"]
    if doOnce == True:
        cy = 326 + 142.24
        cx = 550+105 # issue could appear here where the balls don't move. (this is fixed by doOnce)
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
            ball[i].colour = colours[i]
            ball[i].updateBodyPosition()
        
        #initialise the individual's ball's speed
        for i in range(10):
            ball[i].velocity = pygame.math.Vector2(0,0)
        
       
        doOnce = False
    elif doOnce == False:
        
        for i in range(0,len(displayedBall)):
            if displayedBall[i] != "pocketed":
                displayedBall[i]  = pygame.draw.circle(screen,ball[i].colour,center = (ball[i].cx,ball[i].cy), radius = radius) # number 1
            
    if hit == False:
        for i in range(0,len(displayedBall)):
            ball[i].updateBodyPosition()
    # balls = the surface version of each of these balls.
    # drawnballs is the drawn version of these balls.
    balls = [0]*len(displayedBall)
    drawnBalls = []
    for i in range(0,len(displayedBall)):
        drawnBalls.append(displayedBall[i])
    for i in range(len(balls)):
        balls[i] = pygame.Surface((12,12),pygame.SRCALPHA)
        balls[i].fill((255,255,255,0))
        if displayedBall[i] != "pocketed":
            drawnBalls[i] = balls[i].get_rect(center = drawnBalls[i].center)
            screen.blit(balls[i], drawnBalls[i],special_flags = pygame.BLEND_RGBA_MULT)
        
    
    return drawnBalls





def drawBallPocketTracker():
        width = 1280-776
        height = 720-665
        rectX = 776
        rectY = 665
        cx = 802 # has no effect on the cx cy used for the cueball. this is used to create the circles to be filled in to signify pocketed balls.
        cy = 694
        
        pocketedBalls = []
        'to distribute them evenly, assume 9 to 18 pixel spacing (subtract 9 from a version of width and height thats divisible by 9) and divide by 9'
        pygame.draw.rect(screen,"brown",[rectX,rectY,width,height],width = 0) 
        for i in range(1,10):
            #pygame.draw.circle(screen, (0,0,0), ((776+(55*i)),(665+(72*i))),radius) 
            pygame.draw.circle(screen,"grey", ((cx) + (i*50),cy), radius *3)
            pocketedBalls.append(((cx) + i*50, cy))
        #search for the balls that need to be displayed here.
        if doOnce == False:
            pygame.draw.rect(screen,"brown",[rectX,rectY,width,height],width = 0) 
            for i in range(0,9):
                if displayedBall[i] == "pocketed":
                    pygame.draw.circle(screen, ball[i].colour, (pocketedBalls[i][0],pocketedBalls[i][1]),radius * 3)
                    print("THIS SECTION HAS BEEN RAN")
                else:
                    pygame.draw.circle(screen,"grey",(pocketedBalls[i][0], pocketedBalls[i][1]),radius*3) 
        

###
#Physics related section
###

#initialising the ball - initialised cause i dont want to turn a local variable into a global variable for a subroutine that will just return true or false.
displayedCueBall = pygame.draw.circle(screen,(255,255,255), center = (cx,cy), radius = 6)

# handles how the balls move after being hit by either the cueball or by the cuestick.
def motionLogic(vType,massType,dx,dy,degrees):
    global hit
    global cx
    global cy
    global displayedCueBall
    hit = False
    motionExists = True
    print("displayedBall is", displayedBall)
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
        pocketedBalls = []
        pocketTheseBalls = [] # change the names of these
        for i in range(0,len(pockets)):
            pocketedBalls.append(space.shape_query(pockets[i]))
        for x in range (100): # animation takes place over 100 frames. 

            #detect the collision between pockets and balls
            
            for i in range(0,len(pocketedBalls)):
                if pocketedBalls[i] != None:
                    pocketTheseBalls.append(pocketedBalls[i])
                    pocketIt= pocketTheseBalls[i][0].contact_point_set
                    if pocketIt.points[0].distance < 0:
                        pass
                
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
            # detect if its collided with a pocket
            # have the pockets have their collision IGNORED.When they're ignored, their distance in contactPoint is negative. If this value is negative, a collision has happened
            #Then, delete the ball that has had their collision ignored by the ball.
            
            if hit == True: # base displacement is used to make the ball's current position 0,0 and everything else an offset of that. 
                # the balls should each follow the coordinates of their body position
                # the balls should move in the way that pymunk wants them to.
                #PYMUNK IS HANDLING THE MOVEMENT OF THE BALLS BY TYING THE BODY POSITION TO THE BALL'S MOVEMENT COORDINATES. 720 IS USED AS THE Y AXIS OF THE RESOLUTION.
                for i in range (0,len(displayedBall)):
                    ball[i].cx = ball[i].body.position.x
                    ball[i].cy = 720  - ball[i].body.position.y
                    ball[i].updateBodyPosition()
                drawOtherBalls()
            '''if len(pocketBall) > 0:
                
                # get rid of the ball that's been pocketed and track what ball it is.'''

                
            screen.blit(ballSurface, displayedCueBall) # necessary for the smooth animation. 
            drawnBalls = drawOtherBalls()
            pygame.display.update()
            #check if any of the balls have been pocketed.

            



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
        print(len(pocketedBalls))
class Point:
        def __init__(self,x= 0, y = 0):
            self.x = x
            self.y = y
# creating a class for the ball physics logic


### game stuff
def gameOverCheck(): # might change this to rule check.
    global cueBallPocketed
    global foul
    pocket = 0

    # to check for a scratch foul
    if cueBallPocketed == True:
        cueBallPocketed = False
        foul = True

    
    # to check if the game has been won.
    elif cueBallPocketed == False:
        for i in range (0,9):
            if displayedBall[i] == "pocketed":
                pocket = pocket +1
            if pocket == 9: # to determine if every ball has been pocketed
                gameRestart()
def gameRestart():
    # what variables need to change
    global doOnce
    global cx
    global cy
    global displayedCueBall
    global cueBallPlaced

    #variable setting
    cx = 550 + 105 # centre of circle x coordinate
    cy = 130 + 112 # centre of circle y coordinate
    cueBall.cx = cx
    cueBall.cy = cy
    cueBall.updateBodyPosition()
    doOnce = True
    cueBallPlaced = False

    #drawing
    drawBoard()
    displayedCueBall = pygame.draw.circle(screen,(255,255,255), center = (cx,cy), radius = 6)
    pygame.draw.circle(screen,(255,255,255), center = displayedCueBall.center, radius = 6)
    drawOtherBalls()
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
    degrees = pos[1]
    # as the user moves their mouse up or down, the more they increase or decrease degrees up to a max of 360 and a minimum of 0
    
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


def moveCueBall(pos,firstTime):
    ballSurface = pygame.Surface((12,12),pygame.SRCALPHA)
    ballSurface.fill((255,255,255,0))
    cueBall.cx = pos[0]
    
    
    if firstTime == True:
        cueBall.cy = (130+112.75)
        if cueBall.cx < 580:
            cueBall.cx = cueBall.cx - (cueBall.cx - 580)
        elif cueBall.cx > (520+210):
            cueBall.cx = cueBall.cx - (cueBall.cx - (520+210)) 
    if firstTime == False:
        cueBall.cy = pos[1]
        if cueBall.cx < 595:
            cueBall.cx = cueBall.cx - (cueBall.cx - 590)
        elif cueBall.cx > (520+190):
            cueBall.cx = cueBall.cx - (cueBall.cx - (520+190)) 
        
        # for the y conditions. 
        if cueBall.cy < (150):
            cueBall.cy = cueBall.cy - (cueBall.cy - (150))
        elif cueBall.cy > (535): 
            cueBall.cy = cueBall.cy - (cueBall.cy - (535))

        # for the balls (WIP)
        for i in range(0,9):
            if cueBall.cx == ball[i].cx:
                cueBall.cx = cueBall.cx - (cueBall.cx - (ball[i].cx))
            if cueBall.cy == ball[i].cy:
                cueBall.cy = cueBall.cy - (cueBall.cy - (ball[i].cy))
    # these lines of code cause the balls to flash but not the board to flash.
    pygame.draw.circle(ballSurface,(255,255,255), center = (6,6), radius = 6)
    displayedCueBall = ballSurface.get_rect(center = (cueBall.cx, cueBall.cy))
    screen.blit(ballSurface, displayedCueBall,special_flags = pygame.BLEND_RGBA_MULT)
    screen.blit(screen,(0,0))
    position = list(displayedCueBall.center) # this moves the rect form of the circle for blit to work
    screen.blit(ballSurface, position)
    pygame.display.update()

# used at the start of a game to move the ball around the headstring. 
def setupCueBall():
    global cx
    global cy
    global cueBallPlaced 
    global displayedCueBall
    pos = pygame.mouse.get_pos()
    if pygame.mouse.get_pressed()[0] == False:
        # code to move the ball.
        moveCueBall(pos,firstTime = True)
    if pygame.mouse.get_pressed()[0] == True:
        # displayedCueBall is the initial position of the cueBall. 
        displayedCueBall = pygame.draw.circle(screen,(255,255,255), center = (cueBall.cx +  radius ,cueBall.cy + radius), radius = 6)
        cx = cueBall.cx + radius # have to offset by the radius because this code is moving the center.
        cy = cueBall.cy + radius

        # so that the impulse isn't applied to the wrong point
        cueBall.cx = cueBall.cx + radius
        cueBall.cy = cueBall.cy + radius
        cueBall.updateBodyPosition() # so the motion logic works (transfers from pygame to pymunk well)
        cueBallPlaced = True

# use this when a player fouls.
def placeCueBall(): # identical to setup cueBall except this is used when a player fouls. 
    global cx
    global cy
    global cueBallPlaced 
    global displayedCueBall
    global foul
    pos = pygame.mouse.get_pos()
    if pygame.mouse.get_pressed()[0] == False:
        moveCueBall(pos,firstTime = False)
    if pygame.mouse.get_pressed()[0] == True:
        cueBallPlacedPostStart = True
        # displayedCueBall is the initial position of the cueBall. 
        displayedCueBall = pygame.draw.circle(screen,(255,255,255), center = (cueBall.cx +  radius ,cueBall.cy + radius), radius = 6)
        cx = cueBall.cx + radius # have to offset by the radius because this code is moving the center.
        cy = cueBall.cy + radius

        # so that the impulse isn't applied to the wrong point
        cueBall.cx = cueBall.cx + radius
        cueBall.cy = cueBall.cy + radius
        cueBall.updateBodyPosition() # so the motion logic works (transfers from pygame to pymunk well)
        foul = False


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
    if cueBallPlaced == False:
        setupCueBall()
    if foul == True:
        placeCueBall()
    #draws the numbered balls
    drawOtherBalls()
    #space.debug_draw(draw_options) #(this is for debug)
    getMousePos() # debug only
    #to move the cuestick
    if cueBallPlaced == True and foul == False:
        pygame.draw.circle(screen,(255,255,255), center = displayedCueBall.center, radius = 6)
        moveMode()
        # flip() the display to put your work on screen
    
        gameOverCheck() 
        #draws the display to track which balls have been pocketed. (turn into a subroutine that takes a parameter of numberedBalls that colours in the ball that's been pocketed
    
    
    
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60
    
    
    
pygame.quit()
