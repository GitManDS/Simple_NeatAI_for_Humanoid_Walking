#libraries
import pybullet as pb
import sys, os
import matplotlib.pyplot as plt
import time

#files from other directories
from simulation_env import pybullet_supporting_functions as pbsf
from NeatAI import NeatAI_support_functions as NAIsf
from simulation_env import main_pybullet as mpb
from NeatAI import classes as cl

#main dir files
import sim_AI_connection_functions as sim_AI

#this helps catch the error of the mulltiprocesses getting into a recursive loading loop
if __name__ == "__main__":

    ################### AI SETUP ###################
    #initialize AI population
    #8 inputs(joint positions) + 3 inputs(position of robot) = 11 inputs
    #8 outputs(forces on joints)
    NeatAI_pop = cl.population(NOI = 11, NOO = 8, 
                            Starting_brain_count= 4, 
                            MaxSpecialDist= 0.15,
                            max_offspring= 3,
                            max_pop_brains= 20,
                            max_mutations_per_gen=2)



    ################### SETUP AND RUN ###################

    max_generations = 1000
    max_y = 0
    maxlist = []

    #create new plot for debug
    plt.figure()

    for gen in range(max_generations):
        
        ################### SIMULATION SETUP ###################
        
        #do general mutations and reorganization round
        #THIS HAS TO BE DONE BEFORE THE ROBOTS ARE CREATED SINCE IT SCREWS AROUND WITH THE BRAIN ORDER
        NeatAI_pop.mutate_all()

        #simulate the brains/robots in parallel
        clock_start = time.time()
        positions, sim_data = mpb.multiprocess_simulations(NeatAI_pop, 
                                GUI=False,
                                time_controlled = False, 
                                step_limit = 500,
                                max_processes = 4,
                                time_limit = 10,
                                max_TPS= None,
                                debug= False,
                                show_IDs=True,
                                show_timer=True)
        
        print("[!] sim time",time.time()-clock_start)
    
        
        #debug
        #print(f"[SIM END] -- t={sim_data[0]}s -- avg_TPS={sim_data[1]}")

        ################### RESULTS AND AI UPDATE ###################
        #update the population with the results
        #results of interest are y positions
        res = [positions[robot][1] for robot in positions]
        NeatAI_pop.update_results(results=res)
        
        #save best brain
        maxlist.append(max(res))
        if maxlist[-1] > max_y:
            maxi = maxlist[-1]
            max_y=maxi
            print("new max y",maxi)
            ind = res.index(maxi)
            specie_index, brain_index = NAIsf.get_species_brain_index_from_single_index(NeatAI_pop,ind)
            NeatAI_pop.species[specie_index].brains[brain_index].save_mental_connections(f"best_brain.txt",overwrite=True)
        
        #print results and other data
        NeatAI_pop.print(include_results=True, ordered_by_score=True)
        print(f"max diff distance : {NeatAI_pop.get_max_speciation_difference_per_species()[0]}")   
            
        #prepare new gen with the best brains
        NeatAI_pop.create_new_generation(prioritize_smaller_brains=False)
        
        #plot if debug is on
        plt.plot(maxlist)
        plt.xlabel("Generation")
        plt.ylabel("max_score")
        
        plt.pause(1)
        plt.clf()



