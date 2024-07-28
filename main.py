#libraries
import pybullet as pb
import sys, os

#files from other directories
from simulation_env import pybullet_supporting_functions as pbsf
from simulation_env import main_pybullet as mpb
from NeatAI import classes as cl

#main dir files
import sim_AI_connection_functions as sim_AI

################### AI SETUP ###################
#initialize AI population
#8 inputs(joint positions) + 3 inputs(position of robot) = 11 inputs
#8 outputs(forces on joints)
NeatAI_pop = cl.population(NOI = 11, NOO = 8, Starting_brain_count= 4)



################### SETUP AND RUN ###################

max_generations = 100

for gen in range(max_generations):
    
    ################### SIMULATION SETUP ###################
    #start the simulation
    mpb.sim_init(GUI = True)

    #create n robots (match brain count)
    NeatAI_pop.update_species_brain_count()
    robot_list = {}
    for specie_index, specie in enumerate(NeatAI_pop.species):
        for brain_index, brain in enumerate(specie.brains):
            robot_list = mpb.create_robot(robot_ID=f"S{specie_index}:B{brain_index}",robot_list=robot_list, robot_type="biped_norotation_2d.urdf")
    
    
    #do general mutations and reorganization round
    NeatAI_pop.mutate_all()
    
    ################### SIMULATION RUN ###################
    positions, sim_data = mpb.sim_loop(robot_list, NeatAI_pop, 
                time_controlled = False, 
                step_limit = 100,
                max_TPS= None,
                debug= False,
                cam_focus_ID="S0:B0")
    
    #debug
    #print(f"[SIM END] -- t={sim_data[0]}s -- avg_TPS={sim_data[1]}")

    ################### RESULTS AND AI UPDATE ###################
    #update the population with the results
    #results of interest are y positions
    res = [positions[robot][1] for robot in positions]
    NeatAI_pop.update_results(results=res)
    
    #prepare new gen with the best brains
    NeatAI_pop.create_new_generation()
    
    #end/clear simulation
    pb.disconnect() 



