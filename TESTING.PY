#libraries
import pybullet as pb
import sys, os
import matplotlib.pyplot as plt

#files from other directories
from simulation_env import pybullet_supporting_functions as pbsf
from NeatAI import NeatAI_support_functions as NAIsf
from simulation_env import main_pybullet as mpb
from NeatAI import classes as cl

#main dir files
import sim_AI_connection_functions as sim_AI

def objective_function_calculator(main_body_positions):
    
    obj_value = 0
    
    #add contribution of y value
    obj_value += main_body_positions[1]
    
    #OLD
    #scale objective value by the z-1.11 (height) value of the body position
    obj_value += abs((main_body_positions[2])-1)*0.75*obj_value
    
    return obj_value

#7 NOI (3 robot position + 4 robot joint positions) and 8 NOO (4 robot joint torques)
NeatAI_pop = cl.population(NOI = 11, NOO = 4, 
                            Starting_brain_count= 1, 
                            MaxSpecialDist= 0.15,
                            max_offspring= 5,
                            max_pop_brains= 30,
                            max_mutations_per_gen=2,
                            import_brains_from_file="test.txt")
maxlist = []

plt.figure()
while True:
    positions, sim_data = mpb.simulate(NeatAI_pop, 
                    robot_type= "biped_freeman_simple.urdf",
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
                    cam_focus_ID="S0:B0")
    
    #calculate objective value
    res = [objective_function_calculator(positions[robot]) for robot in positions]
    maxlist.append(max(res))
    plt.plot(maxlist)
    plt.pause(1)
    plt.clf()