#libraries
import pybullet as pb
import sys, os
import matplotlib.pyplot as plt
import math

#files from other directories
from simulation_env import pybullet_supporting_functions as pbsf
from NeatAI import NeatAI_support_functions as NAIsf
from simulation_env import main_pybullet as mpb
from NeatAI import classes as cl

#main dir files
import sim_AI_connection_functions as sim_AI

#main function to calculate objective value
#does so for all the robots in the dictionary of main body positions
def objective_function_calculator(main_body_positions, inputs):
    
    #main obj value
    obj_value = []
    current_robot_input = []
    robot_count = len(main_body_positions.keys())
    step_count_list = []
    
    for robot_index in inputs:
        step_count_list.append(inputs[robot_index][-1][-1])
    
    for robot_index, robot_ID in enumerate(main_body_positions):
        
        #last values of a inputs entry is the last step
        step_count = inputs[robot_ID][-1][-1]
               
        #WALKING TRAINING
        #add contribution of y value
        #obj_value.append(math.exp(main_body_positions[robot_ID][1]))
        
        #STANDING TRAINING
        obj_value.append(0)
              
        #add contribution of the inputs
        #first for every robot, a list is created with the joint positions of the 2 upper legs at every step
        L_leg_integral = 0
        R_leg_integral = 0
        rot_integral = 0
        y_vel_integral = 0
        for entry in inputs[robot_ID]:
            #get the first value (L leg) and the third value (R leg)
            current_robot_input.append([entry[0],entry[2]])  
            
            #integrate the input values over the step for the L leg
            L_leg_integral += abs(current_robot_input[-1][0])
            #integrate the input values over the step for the R leg
            R_leg_integral += abs(current_robot_input[-1][1])
            
            #integrate the velocity y velocity over the step
            y_vel_integral += abs(entry[4])
            
            #integrate the rotation values over the step for the x,y,z values
            #this is done by summing the absolute values of the rotation values
            rot_integral += sum([abs(x) for x in entry[4:-1]])
            


        #scale objective value by the z-1.11 (height) value of the body position
        #if final height is 0.24, the obj value is set to ~0
        obj_value[robot_index] -= abs((main_body_positions[robot_ID][2])-0.25) * 100
            
        #update the objective value for a penalty related to the integrals
        #the integral should be scaled by the max value of the integral (2 (legs) *  area of the rectangle with height 1.5 and width step_count)
        obj_value[robot_index] -= ( 1- (abs(L_leg_integral+R_leg_integral)/(2*1.5*step_count)) )* 0.25 * 100
        
        #update the objective value for a penalty related to the rotation integral
        #the integral should be scaled by the max value of the integral (3 (rotation values) *  area of the rectangle with height 1 and width step_count)
        obj_value[robot_index] -= ( 1- (abs(rot_integral)/(3*1*step_count)) )* 0.25 * 100
        
        #add bonus points for time survived
        obj_value[robot_index] += step_count/max(step_count_list) * 0.25 * 100
          
        plt.figure()  
        plt.plot([x[0] for x in current_robot_input], label = "L leg")
        plt.plot([x[1] for x in current_robot_input], label = "R leg")
        plt.legend()
        plt.title(f"Robot {robot_ID}")
        
        plt.figure()
        plt.plot([inputs["S0:B0"][step][4] for step in range(step_count)])
        plt.legend()
        plt.title(f"Robot {robot_ID}")
        
        plt.pause(1)
            
    
    
    return obj_value


#7 NOI (3 robot position + 4 robot joint positions) and 8 NOO (4 robot joint torques)
NeatAI_pop = cl.population(NOI = 14, NOO = 4, 
                            Starting_brain_count= 1, 
                            MaxSpecialDist= 0.15,
                            max_offspring= 5,
                            max_pop_brains= 30,
                            max_mutations_per_gen=2,
                            import_brains_from_file=None)
maxlist = []

plt.figure()
gen = 0
for gen in range(1000000):
    positions, inputs, sim_data = mpb.simulate(NeatAI_pop, 
                    robot_type= "biped_freeman_abs.urdf",
                    joint_friction=10,
                    torque_multiplier=100,
                    max_single_process_brains=70,
                    GUI=True,
                    time_controlled = False, 
                    step_limit = 600,
                    time_limit = 100,
                    max_TPS= 40,
                    debug= False,
                    show_IDs=True,
                    show_timer=False,
                    show_coords=False,
                    show_axis=False,
                    cam_focus_ID=None)
    
    #calculate objective value
    if gen == 0:
        res = objective_function_calculator(positions, inputs)
        maxlist.append(max(res))
        plt.plot(maxlist)
        plt.pause(1)
        plt.clf()