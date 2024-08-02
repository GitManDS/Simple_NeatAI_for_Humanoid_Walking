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