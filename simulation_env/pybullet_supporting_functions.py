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
    
    #EDIT THESE LINES AND UPDATE THEM WITH THE CORRECT LIMITS IF THE ERROR IS LOCATED INSIDE THIS FUNCTION
    #limit ranges in the correct order
    limit_range_torso_upperleg = [-1.5, 1.5]
    limit_range_torso_lowerleg = [-1.5, 0.2]
    limit_range_torso_lowerleg = [-0.7,0.7]
    limit_ranges = [limit_range_torso_upperleg, limit_range_torso_lowerleg, limit_range_torso_lowerleg, limit_range_torso_upperleg, limit_range_torso_lowerleg,limit_range_torso_lowerleg]
    
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

#will load sim options from a file:
def load_options_from_file():
    #storage
    options = {}
    #expected options
    expected_keys = {"robot_type": str,
                     "joint_friction": float,
                     "torque_multiplier": float,
                     "target_joint_velocity" : float,
                     "GUI": bool , 
                     "max_single_process_brains": int,
                     "max_processes": int,
                     "time_controlled": bool, 
                     "step_limit": int, 
                     "time_limit": int, 
                     "max_TPS": int, 
                     "debug": bool, 
                     "show_IDs": bool, 
                     "show_timer": bool, 
                     "show_coords": bool, 
                     "show_axis": bool,
                     "cam_focus_ID": str}
    
    #open file
    f = open("sim_options.txt", "r") 
    
    #read each line and extract the option
    for line in f:
        #split the line into key and value
        key, value = line.split("=")
        #take out any whitespace and remove the \n from the value
        key = key.strip()
        value = value.strip()
        value = value.replace("\n", "")
        
        #check if the key is expected and convert the variable type of the value
        if key in expected_keys:
            if value == "None":
                value = None
            elif value == "True":
                value = True
            elif value == "False":
                value = False
            else:
                value = expected_keys[key](value)
        else:
            print(f"[!] Unexpected key: {key}")
            continue
        
        #add the key and value to the options
        options[key] = value
    
    return options