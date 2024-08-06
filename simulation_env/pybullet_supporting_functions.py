import pybullet as pb 
import numpy as np
import time

################### MISCELANEOUS ###################

#used to get the keys of the robot list before creating the robots
#used for the multiprocessing function and for the matching function
def create_robot_list_keys(pop):
    key_list = []
    
    for specie_index, specie in enumerate(pop.species):
        for brain_index, brains in enumerate(specie.brains):
            key_list.append(f"S{specie_index}:B{brain_index}")
            
    return key_list

#convert input of -1 to 1 to joint motion ranges
#used for position control
def convert_input_to_joint_ranges(inputs):
    
    limit_range_torso_upperleg = [-1.5, 1.5]
    limit_range_torso_lowerleg = [-1.5, 0.2]
    
    #limit ranges in the correct order
    limit_ranges = [limit_range_torso_upperleg, limit_range_torso_lowerleg, limit_range_torso_upperleg, limit_range_torso_lowerleg]
    
    positions = []
    #[!] Joint index is not the same as the one in the client robot
    #Joint index here is in relation to the joints in limit_ranges and in inputs (which is also not the same as in the robot)
    for joint_index, input in enumerate(inputs):
        if input < -1:
            #lower limit
            positions.append(limit_ranges[joint_index][0])
        elif input > 1:
            #upper limit
            positions.append(limit_ranges[joint_index][1])
        else:
            #in between
            #pos interp will be centered around 0, which means that pos_interp can go from -a to a
            pos_interp = ((limit_ranges[joint_index][1]-limit_ranges[joint_index][0])/2)*input
            #to correct for it, we add the middle value of the range
            pos_corrected = pos_interp + (limit_ranges[joint_index][1]+limit_ranges[joint_index][0])/2
            
            positions.append(pos_corrected)
            
    
    return positions