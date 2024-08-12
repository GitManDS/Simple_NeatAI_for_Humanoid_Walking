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


#main function to calculate objective value
#does so for all the robots in the dictionary of main body positions
def objective_function_calculator(sim_results):
    
    #main obj value
    obj_value = []
    current_robot_input = []
    robot_count = len(sim_results.keys())
    step_count_list = []
    scale = 3

    #go robot by robot
    for robot_index, robot_ID in enumerate(sim_results):
        
        #last values of a inputs entry is the last step
        step_count = sim_results[robot_ID][-1][-1]
        step_count_list.append(step_count)
            
              
        #add contribution of the inputs
        #first for every robot, a list is created with the joint positions of the 2 upper legs at every step
        L_leg_vel_integral = 0
        R_leg_vel_integral = 0
        L_leg_pos_integral = 0
        R_leg_pos_integral = 0
        L_leg_vel = []
        R_leg_vel = []
        y_vel_integral = 0
        rot_integral = 0
        z_pos_integral = 0
        stored_inputs = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
        for entry_ind, step_result in enumerate(sim_results[robot_ID]):
            
            ##DEBUG
            [stored_inputs[i].append(step_result[i]) for i in range(len(step_result)-1)]
                  
            #integrate the input values over the step for the L leg
            #L_leg_pos.append(step_result[0])
            L_leg_pos_integral += step_result[0]
            L_leg_vel_integral += step_result[6]
            #integrate the input values over the step for the R leg
            #R_leg_pos.append(step_result[2])
            R_leg_pos_integral += step_result[3]
            L_leg_vel_integral += step_result[9]
            
            #integrate the position z over the step
            z_pos_integral += abs(step_result[14]-1)
            
            #integrate the y velocity values over the step
            #target velocity is 1
            y_vel_integral += (step_result[19])
            
            #integrate the rotation values over the step for the x,y,z values
            #this is done by summing the absolute values of the rotation values
            rot_integral += abs(step_result[15])
          
        contributions = []  
        
        #get the final distance travelled 
        distance_travelled = sim_results[robot_ID][-1][13]

        '''STANDING TRAINING'''

        #scale objective value by the z-1.11 (height) value of the body position
        #if final height is 0.24, the obj value is set to ~0
        #[!]
        contributions.append(target_score)
        #contributions.append(-abs(((z_pos_integral-(1*step_count))/(1*step_count))) * 2.5 * scale)
        
        #add bonus points for velocity matched
        #divide by the integral of the desired velocity
        contributions.append((y_vel_integral)/(2*step_count) * 0.25 * scale)
        
        #blend z pos and y vel penalties together
        #however if the velocity is 0, its not penalized for falling, an extra deduction is made down below
        #contributions[-1] *= abs(z_pos_integral/(1.1*step_count)) * 1.25 * scale
        
        #deduct points for the z position integral
        #the integral should be scaled by the max value of the integral *  area of the rectangle with height 1 and width step_count)
        contributions.append(-abs(z_pos_integral/(1.1*step_count)) * 1.5 * scale)
        
        #deduct points for not keeping legs in upright position
        #contributions.append(-abs(((L_leg_pos_integral+R_leg_pos_integral)/(2*1.5*step_count))) * 2 * scale)
        
        #deduct points for extending legs but not retracting them back to the original position
        contributions.append(-((abs(L_leg_pos_integral)+abs(R_leg_pos_integral))/(2*1.5*step_count)) * 1.25 * scale)
        
        #add points for using leg muscles
        #the integral should be scaled by the max value of the integral (2 (legs) *  area of the rectangle with target vel 1 and width step_count)
        contributions.append(1-abs(((abs(L_leg_vel_integral)+abs(R_leg_vel_integral))/(2*1*step_count))) * 1 * scale)
        
        #update the objective value for a penalty related to the rotation integral
        #the integral should be scaled by the max value of the integral *  area of the rectangle with height 1 and width step_count)
        contributions.append(-abs(((rot_integral)/(0.75*step_count))) * 1.5 * scale)
        
        #take points away for using leg muscles
        #the integral should be scaled by the max value of the integral (2 (legs) *  area of the rectangle with height 1.5 and width step_count)
        #contributions.append(- abs(((L_leg_integral+R_leg_integral)/(2*1.5*step_count))) * 1 * scale)
        
        #add bonus points for time survived
        #obj_value[robot_index] -= (1 - step_count/300) * 0.25 * scale
        
        
        '''WALKING TRAINING'''
        
        #add bonus points for distance travelled
        #0.5 points per unit travelled
        #obj_value[robot_index] += abs(distance_travelled/1) * 0.5 * scale
        
        
        #get objective value
        obj_value.append(sum(contributions))
        
        if robot_ID == "S0:B0":
            print(contributions)
        
    
    return obj_value


#this helps catch the error of the mulltiprocesses getting into a recursive loading loop
if __name__ == "__main__":
    
    #################################### TRAINING PARAMETERS ####################################

    #simulation specific
    max_generations = 5000
    load_from_sim_options_file = True
    options = {"robot_type" : "biped_freeman_abs.urdf",
                "joint_friction" : 10,
                "torque_multiplier" : 100,
                "target_joint_velocity" : 0.1,
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



    #AI specific
    Number_of_inputs = 15
    Number_of_outputs = 6
    save_pop_dir = f"NeatAI/pop_saves/sim{int(time.time())}/"
    #Starting_brain_count= 12 
    starting_brain_count = 40
    MaxSpecialDist= 0.25
    max_offspring= 4
    min_offspring= 1
    max_pop_brains= 40
    max_mutations_per_gen=8
    preserve_top_brain = False
    dynamic_mutation_rate = True
    do_explicit_fitness_sharing = False
    import_pop_dir = None
    import_pop_file = None
    target_score = 50
    fitness_sharing_c1 = 1.5
    fitness_sharing_c2 = 1.5
    fitness_sharing_c3 = 0.4
    


    ##############################################################################################


    #Miscelaneous storage initializations 
    maxlist = []
    minlist = []
    avglist = []
    target_list = []


    
    ##############################################################################################
    
    #get storage directory
    if not os.path.exists(save_pop_dir):
        os.makedirs(save_pop_dir[0:-1])

    ################### AI SETUP ###################
    #1 - initialize AI population
    #11 NOI (2 robot velocities) + 4 (robot joint positions) + 4 (robot joint velocities) + 1 (robot rotation)  
    #4 NOO (4 robot joint torques)
    #define additional settings for the population
    NeatAI_pop = cl.population(NOI = Number_of_inputs, NOO = Number_of_outputs, 
                            Starting_brain_count= Starting_brain_count, 
                            MaxSpecialDist= MaxSpecialDist,
                            min_offspring = min_offspring,
                            max_offspring= max_offspring,
                            max_pop_brains= max_pop_brains,
                            max_mutations_per_gen=max_mutations_per_gen,
                            preserve_top_brain=preserve_top_brain,
                            dynamic_mutation_rate=dynamic_mutation_rate,
                            target_score=target_score,
                            do_explicit_fitness_sharing=do_explicit_fitness_sharing,
                            import_population_from_file=import_pop_file,
                            dir=import_pop_dir)

    NeatAI_pop.compatability_c1 = fitness_sharing_c1
    NeatAI_pop.compatability_c2 = fitness_sharing_c2
    NeatAI_pop.compatability_c3 = fitness_sharing_c3

    ################### SETUP AND RUN ###################
    
    #create new plot for the debug graph
    plt.figure()
    
    #delete old stop file
    if os.path.exists("stop_sim_now"):
        os.remove("stop_sim_now")

    for gen in range(max_generations):
        
        ################### SIMULATION SETUP ###################
        
        if load_from_sim_options_file:
            #load options from file
            options = pbsf.load_options_from_file()
        
        max_single_process_brains = options["max_single_process_brains"]
        robot_type= options["robot_type"]
        joint_friction=options["joint_friction"]
        torque_multiplier=options["torque_multiplier"]
        target_joint_velocity = options["target_joint_velocity"]
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
        
        #2 - do general mutations and reorganization round
        #THIS HAS TO BE DONE BEFORE THE ROBOTS ARE CREATED SINCE IT SCREWS AROUND WITH THE BRAIN ORDER
        NeatAI_pop.mutate_all()
    
        #3 - simulate the brains/robots in parallel
        clock_start = time.time()
        sim_results, sim_data = mpb.simulate(NeatAI_pop, 
                                max_single_process_brains = max_single_process_brains,
                                robot_type= robot_type,
                                joint_friction=joint_friction,
                                torque_multiplier=torque_multiplier,
                                target_joint_velocity=target_joint_velocity,
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
        
        #debug
        elapsed_time = time.time()-clock_start
        print("[!] sim time",round(elapsed_time,2))
    
    
        ################### RESULTS AND AI UPDATE ###################
        #4 - update the population with the results
        #results of interest are y positions
        res = objective_function_calculator(sim_results)
        
        #5 - update the results of the population
        #also give the initial max score
        if gen == 0: NeatAI_pop.initial_max_score = max(res)
        NeatAI_pop.update_results(results=res)
        
        NeatAI_pop = NAIsf.order_by_score(NeatAI_pop)
        
        #optional preservation of the top performing brain
        #the .preserve attribute is used to keep the brain from being mutated
        #once it mutates, this attribute is set to False
        if NeatAI_pop.preserve_top_brain:
            specie_index, brain_index = NeatAI_pop.get_highest_score_brain()
            NeatAI_pop.species[specie_index].brains[brain_index].preserve = True
            
        
        #(debug) print results and other data
        NeatAI_pop.print(include_results=True, ordered_by_score=True, simplified=True)
        print(f"max diff distance : {NeatAI_pop.get_max_speciation_difference_per_species()[0]}") 
        print(f"next max mutations : {NeatAI_pop.maxmutations} mutations per gen") 
        
        #6 - (optional) save best brain (connections) every generation
        #also save the brain_map of the current best brain as a .png
        maxlist.append(max(res))
        minlist.append(min(res))
        avglist.append(sum(res)/len(res))
        target_list.append(target_score)
        specie_index, brain_index = NeatAI_pop.get_highest_score_brain()   
        NeatAI_pop.species[specie_index].brains[brain_index].save_brain(f"best_brain_gen{NeatAI_pop.generation}.txt",
                                                                                     overwrite=True,
                                                                                     dir = save_pop_dir)
        
        
        #7 - prepare new gen with the best brains
        #this is the crossover step
        NeatAI_pop.create_new_generation()
                    
        #debug plot
        if os.path.exists("show_score_graph") or gen == max_generations-1 or os.path.exists("stop_sim_now"):
            plt.plot(maxlist, color='green')
            plt.plot(minlist, color='red')
            plt.plot(avglist, color='blue')
            plt.plot(target_list, linestyle='dashed', color='red')
            plt.legend(["max","min","avg"])
            plt.xlabel("Generation")
            plt.ylabel("max_score")
            plt.grid()
            plt.title(f"last sim time = {round(elapsed_time,2)} [s], number of brains = {NeatAI_pop.brain_count}")
                         
            plt.savefig(save_pop_dir+"max_score.png")

        #only if the score goes up
        if len(maxlist)>2 and max(res) >= maxlist[-2]:
            plt.close()
            NeatAI_pop.species[specie_index].brains[brain_index].save_mental_map("best_brain_current_gen.png",dir = save_pop_dir)
      
            
        #CHECK FOR IMMEDIATE TERMINATION FILE
        if os.path.exists("stop_sim_now"):
            break
            
        
    #save population at the end of the training
    NeatAI_pop.save_population("final_pop.txt", dir = save_pop_dir)



