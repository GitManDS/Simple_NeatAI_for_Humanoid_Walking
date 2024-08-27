# Report support file
This file is used to compliment the results of the report by providing visual references to the simulation results in gif format

- [Report support file](#report-support-file)
  * [Performance evaluation <a name="PE"></a>](#performance-evaluation--a-name--pe----a-)
    + [Training rules <a name="PE:T"></a>](#training-rules--a-name--pe-t----a-)
    + [Results <a name="PE:R"></a>](#results--a-name--pe-r----a-)
  * [Training of Bipedal controller <a name="BC"></a>](#training-of-bipedal-controller--a-name--bc----a-)
    + [Training rules <a name="BC:T"></a>](#training-rules--a-name--bc-t----a-)
    + [Results <a name="BC:R"></a>](#results--a-name--bc-r----a-)
    + [Additional Results <a name="BC:AR"></a>](#additional-results--a-name--bc-ar----a-)


## Performance evaluation <a name="PE"></a>
In order to verify the NeatAI is capable of correctly achieving neuroevolution and converging to a specific solution, a test was made to see if it could obbey 3 simple rules in training a network on a arbitrary run

### Training rules <a name="PE:T"></a>
  - Position restriction: The network is **penalized** for the distance of the current torso position to the original/upright torso position (only in the z axis)
  - Rotation restriction: The network is **penalized** for the rotation of the torso in relation to the uppright position (x axis)
  - Velocity restriction: The network is **penalized** for any torso velocity

### Results <a name="PE:R"></a>
- gen 1 through 3

![Gif of the physics simulation of the first few networks](report_files/standing_60_firstgens.gif)

-gen 22 and 23 (mid training)

![Gif of the physics simulation of the middle few networks](report_files/standing_60_midgens.gif)

-last/best gen (gen = 57)

![Gif of the physics simulation of last gen](report_files/standing_60_gen57.gif)

- other results
score graph over the generations, showing max, min and average score for the entire population and phenotype of the last network
<p float="left">
  <img src="report_files/score_standing.png" width="500" />
  <img src="report_files/network_standing.png" width="500" /> 
</p>


## Training of Bipedal controller <a name="BC"></a>
Training the algorithm to walk is a challenge since walking requires the network to purposely lose balance (forwards) and use the legs in a coordinated manner to maintain temporary balance. 

### Training rules <a name="BC:T"></a>
  - Distance travelled incentive: The network is given points for the y distance it travelled 
    - EXCEPTIONS: The network does NOT gain points if it was travelling upside down
    - EXCEPTIONS: The network does NOT gain any additional points for any distance travelled with legs that haven't cycled for more than 150 simulation steps

  - Leg cycling: The network is rewarded for cycling its legs in the correct direction, every simulation step, a point is deducted to deter stagnation in the leg movement

  '''python

    #Right leg case
    #if leg is behind the target, the velocity should be positive
                  #current R dir stores the target velocity direction of the right leg
                  #1 is forwards, -1 is backwards
                  if current_R_dir == 1:
                      #intermediate_pos_R has 20 "checkpoints" until the target position
                      #the if the right leg crosses a checkpoint, the checkpoint is removed
                      #and 3 points are added
                      while R_leg_pos > intermediate_pos_R[0]:
                          intermediate_pos_R.pop(0)
                          Leg_correct_vel_counter += 3
                          if len(intermediate_pos_R) == 0:
  '''
                
  - EXCEPTIONS: If the network is upside down, the network does not gain any points and is severelly penalized every simulation step
    

### Results <a name="BC:R"></a>
6 Simulations were run for this algorithm under these training rules, of which 2 managed to displayed human walking patterns, 3 converged to random solutions and 1 converged to a skipping pattern

- Best simulation (Sim B)

<p float="left">
  <img src="report_files\sim_walking_B_20.gif" width="500" />
  <img src="report_files\sim_walking_B_40.gif" width="500" /> 
  <img src="report_files\sim_walking_B_60.gif" width="500" /> 
  <img src="report_files\sim_walking_B_80.gif" width="500" /> 
</p>

- Alternative sucessful simulation (Sim A)

![Sim A best network gif (gen 80)](report_files\sim_walking_A.gif)

- Other simulations that converged to random results (Sim C, D and E)

<p float="left">
  <img src="report_files/sim_nonwalking_c.gif" width="300" />
  <img src="report_files/sim_nonwalking_d.gif" width="300" /> 
  <img src="report_files/sim_nonwalking_e.gif" width="300" /> 
</p>

- Convergence data and phenotype of the resulting networks

![Convergence graph of all simulations](report_files/sim_walking_graphs.png)

  - Phenotype of best network of Sim A (input-output direct connections hidden for readability)
  ![Phenotype diagramn of Sim A](report_files\simA_phenotype.png)

  - Phenotype of best network of Sim B (input-output direct connections hidden for readability)
  ![Phenotype diagramn of Sim B](report_files\simB_phenotype.png)
     
### Additional Results <a name="BC:AR"></a>

As mentioned, one other result of this training was skipping, which was achieved by simply increasing the simulation step counter from 150 simulation steps to 250 simulation steps

![Skipping Sim graph](report_files\sim_skipping_graph.png)
