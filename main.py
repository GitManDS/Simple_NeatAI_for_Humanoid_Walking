#libraries
import pybullet as pb
import sys, os
import matplotlib.pyplot as plt
import time
import math

#files from other directories
from simulation_env import pybullet_supporting_functions as pbsf
from NeatAI import NeatAI_support_functions as NAIsf
from simulation_env import main_pybullet as mpb
from NeatAI import classes as cl

#main dir files
import sim_AI_connection_functions as sim_AI


#main function to calculate objective value
def objective_function_calculator(main_body_positions):
    
    obj_value = 0
    
    #add contribution of y value
    obj_value += math.exp(main_body_positions[1])
    
    #OLD
    #scale objective value by the z-1.11 (height) value of the body position
    obj_value -= abs((main_body_positions[2])-1)*0.80*obj_value
    
    return obj_value

#this helps catch the error of the mulltiprocesses getting into a recursive loading loop
if __name__ == "__main__":

    ################### AI SETUP ###################
    #initialize AI population
    #7 NOI (3 robot position + 4 robot joint positions) and 8 NOO (4 robot joint torques)
    NeatAI_pop = cl.population(NOI = 11, NOO = 4, 
                            Starting_brain_count= 4, 
                            MaxSpecialDist= 0.25,
                            max_offspring= 5,
                            max_pop_brains= 30,
                            max_mutations_per_gen=4,
                            preserve_top_brain=True)



    ################### SETUP AND RUN ###################

    max_generations = 100
    max_y = 0
    maxlist = []
    minlist = []
    avglist = []
    
    #options
    options = {"robot_type" : "biped_freeman.urdf",
            "joint_friction" : 10,
            "torque_multiplier" : 100,
            "GUI" : False,
            "max_single_process_brains" : 7,
            "max_processes" : 4,
            "time_controlled":False, 
            "time_limit" : 5,
            "step_limit" : 1000, 
            "max_TPS" : None,
            "debug" : False,
            "show_timer" : False, 
            "show_axis" : False, 
            "show_IDs" : False,
            "show_coords" : False,
            "cam_focus_ID" : None}

    #create new plot for debug
    plt.figure()

    for gen in range(max_generations):
        
        ################### SIMULATION SETUP ###################
        
        if True:
            #load options from file
            options = pbsf.load_options_from_file()
        
        max_single_process_brains = options["max_single_process_brains"]
        robot_type= options["robot_type"]
        joint_friction=options["joint_friction"]
        torque_multiplier=options["torque_multiplier"]
        GUI=options["GUI"]
        time_controlled = options["time_controlled"]
        step_limit = options["step_limit"]
        max_processes = options["max_processes"]
        time_limit = options["time_limit"]
        max_TPS= options["max_TPS"]
        debug= options["debug"]
        show_IDs=options["show_IDs"]
        show_timer=options["show_timer"]
        show_coords=options["show_coords"]
        
        #do general mutations and reorganization round
        #THIS HAS TO BE DONE BEFORE THE ROBOTS ARE CREATED SINCE IT SCREWS AROUND WITH THE BRAIN ORDER
        NeatAI_pop.mutate_all()

        #simulate the brains/robots in parallel
        clock_start = time.time()
        positions, sim_data = mpb.simulate(NeatAI_pop, 
                                max_single_process_brains = max_single_process_brains,
                                robot_type= robot_type,
                                joint_friction=joint_friction,
                                torque_multiplier=torque_multiplier,
                                GUI=GUI,
                                time_controlled = time_controlled, 
                                step_limit = step_limit,
                                max_processes = max_processes,
                                time_limit = time_limit,
                                max_TPS= max_TPS,
                                debug= debug,
                                show_IDs=show_IDs,
                                show_timer=show_timer,
                                show_coords=show_coords)
        
        print("[!] sim time",time.time()-clock_start)
    
        
        #debug

        ################### RESULTS AND AI UPDATE ###################
        #update the population with the results
        #results of interest are y positions
        res = [objective_function_calculator(positions[robot]) for robot in positions]
        if NeatAI_pop.preserve_top_brain:
            max_index = res.index(max(res))
            specie_index, brain_index = NAIsf.get_species_brain_index_from_single_index(NeatAI_pop,max_index)
            NeatAI_pop.species[specie_index].brains[brain_index].preserve = True
        NeatAI_pop.update_results(results=res)
        
        #save best brain
        maxlist.append(max(res))
        minlist.append(min(res))
        avglist.append(sum(res)/len(res))
        if maxlist[-1] > max_y:
            maxi = maxlist[-1]
            max_y=maxi
            print("new max y",maxi)
            ind = res.index(maxi)
            specie_index, brain_index = NAIsf.get_species_brain_index_from_single_index(NeatAI_pop,ind)
            NeatAI_pop.species[specie_index].brains[brain_index].save_mental_connections(f"best_brain.txt",overwrite=True)
            NeatAI_pop.species[specie_index].brains[brain_index].save_mental_picture(f"best_brain_pic.png",overwrite=True)
        
        #print results and other data
        NeatAI_pop.print(include_results=True,ordered_by_score=True, simplified=False)
        print(f"max diff distance : {NeatAI_pop.get_max_speciation_difference_per_species()[0]}")   
            
        #prepare new gen with the best brains
        NeatAI_pop.create_new_generation()
        
        #plot if debug is on
        plt.plot(maxlist, color='green')
        plt.plot(minlist, color='red')
        plt.plot(avglist, color='blue')
        plt.legend(["max","min","avg"])
        plt.xlabel("Generation")
        plt.ylabel("max_score")
        
        plt.pause(1)
        if gen < max_generations-1:
            plt.clf()
            
        #CHECK FOR IMMEDIATE TERMINATION FILE
        if os.path.exists("stop_sim_now"):
            break
            
        
    #save population
    plt.savefig("max_score.png")
    NeatAI_pop.save_population("final_pop.txt")



