# Billiards-Game-EPQ
This is a playable billiards game using python + pygame and pymunk with nine-ball pool rules.

## Highlights
- Collision detection and interactions between collision objects with pymunk's collision shape function.
- Billiards physics logic engineered with the aid of pymunk
- Animated ball movement (with pygame's blit function)
- Fully functional cue-stick that orbits the ball in the way you choose.

## Demos
### Prototype 1
![hippo](https://media.giphy.com/media/ZO7USoRlgSSn4mtQfm/giphy.gif)
### Prototype 2
![hippo](https://media.giphy.com/media/e0qNc19NBTHBrteHv1/giphy.gif)
## Overview
### Requirements
- Python + pygame and pymunk installed (TBC)
### User Instructions
To play the game, open the python script and run it with pygame installed. 
To see the cue stick and move it around, hold left mouse. When you’ve decided on the angle to hit it at, hold right mouse and let go of the left mouse. Red bars will appear to the right. 4 is the max, with the highest power, and 1 is the lowest with soft power. 
They will increase the longer you hold it. When you reach 4 bars and are still holding the right mouse button, the bars will decrease until the 1st bar. From the 1st bar onwards, it will increase. From the 4th bar, it will begin to decrease to the 1st bar.
Then, when you’ve decided on the desired power, release the right mouse button. 

You will not be able to hit the cue-ball until the cue-ball has finished its motion

### Issues
One collision pair affects every ball (minus the cue ball). 
The rail and the cushion cannot be collided with yet.




