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
def objective_function_calculator(sim_results):
    
    #main obj value
    obj_value = []
    current_robot_input = []
    robot_count = len(sim_results.keys())
    step_count_list = []

    #go robot by robot
    for robot_index, robot_ID in enumerate(sim_results):
        
        #last values of a inputs entry is the last step
        step_count = sim_results[robot_ID][-1][-1]
        step_count_list.append(step_count)
            
              
        #add contribution of the inputs
        #first for every robot, a list is created with the joint positions of the 2 upper legs at every step
        L_leg_integral = 0
        R_leg_integral = 0
        L_leg_vel = []
        R_leg_vel = []
        alternating_leg_integral = 0
        rot_integral = 0
        z_pos_integral = 0
        stored_inputs = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
        for entry_ind, step_result in enumerate(sim_results[robot_ID]):
            
            ##DEBUG
            [stored_inputs[i].append(step_result[i]) for i in range(len(step_result)-1)]
                  
            #integrate the input values over the step for the L leg
            #L_leg_pos.append(step_result[0])
            L_leg_integral += abs(step_result[0])
            L_leg_vel.append(step_result[4])
            #integrate the input values over the step for the R leg
            #R_leg_pos.append(step_result[2])
            R_leg_integral += abs(step_result[2])
            R_leg_vel.append(step_result[6])
            
            #get the alternating leg integral
            alternating_leg_integral += step_result[4]+step_result[6]
            
            #integrate the position z over the step
            z_pos_integral += abs(step_result[10])
            
            #integrate the rotation values over the step for the x,y,z values
            #this is done by summing the absolute values of the rotation values
            rot_integral += abs(step_result[11])
            
        #get the final distance travelled 
        distance_travelled = sim_results[robot_ID][-1][9]

        '''STANDING TRAINING'''

        #scale objective value by the z-1.11 (height) value of the body position
        #if final height is 0.24, the obj value is set to ~0

        #[!]
        obj_value.append(0)
        obj_value[robot_index] += abs(1-(z_pos_integral/(1*step_count))) * 1
        
        #update the objective value for a penalty related to the rotation integral
        #the integral should be scaled by the max value of the integral (3 (rotation values) *  area of the rectangle with height 1 and width step_count)
        obj_value[robot_index] += abs(1-((rot_integral)/(0.75*step_count))) * 1
        
        #take points away for using leg muscles
        #the integral should be scaled by the max value of the integral (2 (legs) *  area of the rectangle with height 1.5 and width step_count)
        obj_value[robot_index] -= abs(1-((L_leg_integral+R_leg_integral)/(2*1.5*step_count))) * 1
             
        
        '''WALKING TRAINING'''
        '''
        #add bonus points for time survived
        obj_value[robot_index] += abs(step_count/(sum(step_count_list)/len(step_count_list))) * 0.25 * distance_travelled
        
        #add bonus points for balancing one leg movement with the opposite movement of the other leg
        #2 now means the area created when the 2 legs are at the same position
        obj_value[robot_index] += abs(1-((abs(alternating_leg_integral))/(2*1*step_count))) * 1
        
        '''
             
        #plot all the inputs
        plt.figure()
        for stored_index in [0,2,4,6,10,11]:
            plt.plot(stored_inputs[stored_index], label = f"input {stored_index}")
        plt.legend()
        plt.grid()
        plt.title("all inputs")
        
        '''  
        plt.figure()  
        plt.plot([x[0] for x in current_robot_input], label = "L leg")
        plt.plot([x[1] for x in current_robot_input], label = "R leg")
        plt.legend()
        plt.title(f"Robot {robot_ID}")
        
        
        plt.figure()
        plt.plot([inputs["S0:B0"][step][5] for step in range(step_count)],label = "x_rot")
        plt.legend()
        plt.title(f"Robot {robot_ID}")
        '''
        plt.pause(4)
            
    
    
    return obj_value


#7 NOI (3 robot position + 4 robot joint positions) and 8 NOO (4 robot joint torques)
NeatAI_pop = cl.population(NOI = 11, NOO = 4, 
                            Starting_brain_count= 1, 
                            MaxSpecialDist= 0.15,
                            max_offspring= 5,
                            max_pop_brains= 30,
                            max_mutations_per_gen=2,
                            import_brains_from_file=None)

maxlist = []

NeatAI_pop.save_population("test_pop")
NeatAI_pop.load_population("test_pop")


sim = mpb.sim_client(robot_type= "biped_2d_simple.urdf")
sim.add_robot("S0:B0")
for i in range(sim.Client.getNumJoints(1)):
    print(sim.Client.getJointInfo(1, i))

plt.figure()
gen = 0
for gen in range(1000000):
    sim_results, sim_data = mpb.simulate(NeatAI_pop, 
                    robot_type= "biped_2d_simple.urdf",
                    joint_friction=10,
                    torque_multiplier=50,
                    max_single_process_brains=70,
                    GUI=True,
                    time_controlled = False, 
                    step_limit = 600,
                    time_limit = 100,
                    max_TPS= None,
                    debug= False,
                    show_IDs=False,
                    show_timer=False,
                    show_coords=True,
                    show_axis=False,
                    cam_focus_ID=None)
    
    #calculate objective value
    if gen == 0:
        res = objective_function_calculator(sim_results)
        maxlist.append(max(res))
        plt.plot(maxlist)
        plt.pause(1)
        plt.clf()