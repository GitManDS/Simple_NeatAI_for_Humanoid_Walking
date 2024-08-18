# Report support file
This file is used to compliment the results of the report by providing visual references to the simulation results in gif format

## Performance evaluation
In order to verify the NeatAI is capable of correctly achieving neuroevolution and converging to a specific solution, a test was made to see if it could obbey 3 simple rules in training a network on a arbitrary run

### training rules.
  - Position restriction: The network is **penalized** for the distance of the current torso position to the original/upright torso position (only in the z axis)
  - Rotation restriction: The network is **penalized** for the rotation of the torso in relation to the uppright position (x axis)
  - Velocity restriction: The network is **penalized** for any torso velocity

### results:
- gen 1 through 3

![Gif of the physics simulation of the first few networks](gifs/standing_60_firstgens.gif)

-gen 22 and 23 (mid training)

![Gif of the physics simulation of the middle few networks](gifs/standing_60_midgens.gif)

-last/best gen (gen = 57)

![Gif of the physics simulation of last gen](gifs/standing_60_gen57.gif)

- other results

