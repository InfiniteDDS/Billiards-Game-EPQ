# Billiards-Game-EPQ
This is a playable billiards game using python + pygame and pymunk with nine-ball pool rules.

## Highlights
- Collision detection and interactions between collision objects with pymunk's collision shape function.
- Billiards physics logic engineered with the aid of pymunk
- Animated ball movement (with pygame's blit function)
- Fully functional cue-stick that orbits the ball in the way you choose.

## Demo
![til](https://github.com/InfiniteDDS/Billiards-Game-EPQ/blob/main/complete-demo.gif)

## Overview
### Requirements
- Billiards-game.exe
### Install Instructions 
To play the game, go to the dist folder in the repo, download billiards-game.exe. 
Once it's finished downloading, double click it and it will open in a 1280x720 interface.
### User Instructions
To see the cue stick and move it around, hold left mouse. When you’ve decided on the angle to hit it at, hold right mouse and let go of the left mouse. Red bars will appear to the right. 4 is the max, with the highest power, and 1 is the lowest with soft power. 
They will increase the longer you hold it. When you reach 4 bars and are still holding the right mouse button, the bars will decrease until the 1st bar. From the 1st bar onwards, it will increase. From the 4th bar, it will begin to decrease to the 1st bar.
Then, when you’ve decided on the desired power, release the right mouse button. 

You will not be able to hit the cue-ball until the cue-ball has finished its motion

Hold E to see the numbers on the balls.

At the bottom right is where the balls are tracked. From left to right it's: 1,2,3,4,5,6,7,8,9

### Known Issues
The ball may move too fast, low power is needed to get somewhat good control.
Collision tunneling
Balls will disappear when displaying foul text
if the balls are near the rail on a breakshot, it will be counted as a foul if none of them has been pocketed.
If you pocket the cueball as you pocket the nine ball, the game won't restart if you keep pocketing the cueball

# Prototypes
## Prototype 1
This one was where I hand-coded the physics, so only the cueball had physics after colliding with the rail.
![til](https://github.com/InfiniteDDS/Billiards-Game-EPQ/blob/main/image2.gif)
## Prototype 2
This one involved PyMunk but I didn't know how to transfer my hand-coded physics to PyMunk's physics.
![til](https://github.com/InfiniteDDS/Billiards-Game-EPQ/blob/main/image1.gif)
## Prototype 3
This implementation fully involved PyMunk but had no game rules. No ability to pocket or restart the game/foul.
![til](https://github.com/InfiniteDDS/Billiards-Game-EPQ/blob/main/prototype3.gif)



