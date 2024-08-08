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
        y_pos_integral = 0
        for entry in inputs[robot_ID]:
            #get the first value (L leg) and the third value (R leg)
            current_robot_input.append([entry[0],entry[2]])  
            
            #integrate the input values over the step for the L leg
            L_leg_integral += abs(current_robot_input[-1][0])
            #integrate the input values over the step for the R leg
            R_leg_integral += abs(current_robot_input[-1][1])
            
            #integrate the position z over the step
            y_pos_integral += abs(entry[4])
            
            #integrate the rotation values over the step for the x,y,z values
            #this is done by summing the absolute values of the rotation values
            rot_integral += sum([abs(x) for x in entry[4:-1]])
            


        #scale objective value by the z-1.11 (height) value of the body position
        #if final height is 0.24, the obj value is set to ~0
        #obj_value[robot_index] -= abs((main_body_positions[robot_ID][2])-0.25) * 100
        obj_value[robot_index] -= abs(y_pos_integral/(0.2*step_count)) * 100
        
        '''
        #update the objective value for a penalty related to the integrals
        #the integral should be scaled by the max value of the integral (2 (legs) *  area of the rectangle with height 1.5 and width step_count)
        obj_value[robot_index] += (abs(L_leg_integral+R_leg_integral)/(2*1.5*step_count)) * 0.25 * 100
        
        #update the objective value for a penalty related to the rotation integral
        #the integral should be scaled by the max value of the integral (3 (rotation values) *  area of the rectangle with height 1 and width step_count)
        obj_value[robot_index] -= (abs(rot_integral)/(3*1*step_count)) * 0.25 * 100
        
        #add bonus points for time survived
        obj_value[robot_index] += step_count/max(step_count_list) * 0.05 * 100
        ''' 
        
    
    return obj_value

#this helps catch the error of the mulltiprocesses getting into a recursive loading loop
if __name__ == "__main__":

    ################### AI SETUP ###################
    #initialize AI population
    #7 NOI (3 robot position + 4 robot joint positions) and 8 NOO (4 robot joint torques)
    NeatAI_pop = cl.population(NOI = 14, NOO = 4, 
                            Starting_brain_count= 8, 
                            MaxSpecialDist= 0.25,
                            max_offspring= 8,
                            max_pop_brains= 50,
                            max_mutations_per_gen=2,
                            preserve_top_brain=False)



    ################### SETUP AND RUN ###################

    max_generations = 100
    max_y = 0
    maxlist = []
    minlist = []
    avglist = []
    
    #options
    options = {"robot_type" : "biped_freeman_abs.urdf",
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
    
    #delete old stop file
    if os.path.exists("stop_sim_now"):
        os.remove("stop_sim_now")

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
        positions, inputs, sim_data = mpb.simulate(NeatAI_pop, 
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
        res = objective_function_calculator(positions, inputs)
        
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
        NeatAI_pop.print(include_results=True, ordered_by_score=True, simplified=True)
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
        
        if gen < max_generations-1:
            plt.pause(1)
            plt.clf()
            
        #CHECK FOR IMMEDIATE TERMINATION FILE
        if os.path.exists("stop_sim_now"):
            break
            
        
    #save population
    plt.savefig("max_score.png")
    NeatAI_pop.save_population("final_pop.txt")



