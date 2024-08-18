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
        target_score = 50
            
              
        #add contribution of the inputs
        #first for every robot, a list is created with the joint positions of the 2 upper legs at every step
        L_leg_integral = 0
        R_leg_integral = 0
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
            L_leg_integral += abs(step_result[0])
            L_leg_vel.append(step_result[6])
            #integrate the input values over the step for the R leg
            #R_leg_pos.append(step_result[2])
            R_leg_integral += abs(step_result[3])
            R_leg_vel.append(step_result[9])
            
            #integrate the position z over the step
            z_pos_integral += abs(step_result[14])
            
            #integrate the y velocity values over the step
            #target velocity is 1
            y_vel_integral += abs(step_result[19] - 1)
            
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
        contributions.append(+abs((y_vel_integral)/(2*step_count)) * 1 * scale)
        
        #blend z pos and y vel penalties together
        contributions[-1] *= abs(z_pos_integral/(1.1*step_count)) * 2.5 * scale
        
        #update the objective value for a penalty related to the rotation integral
        #the integral should be scaled by the max value of the integral *  area of the rectangle with height 1 and width step_count)
        contributions.append(- abs(((rot_integral)/(0.75*step_count))) * 1.25 * scale)
        
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
        
           
           
        #plot all the inputs
        plt.figure()
        for stored_index in [9,6]:
            plt.plot(stored_inputs[stored_index], label = f"input {stored_index}")
        plt.legend()
        plt.grid()
        plt.title("all inputs")
        plt.show()
        
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
        
        plt.pause(4)
        '''
            
    
    
    return obj_value


#7 NOI (3 robot position + 4 robot joint positions) and 8 NOO (4 robot joint torques)
NeatAI_pop = cl.population(NOI = 15, NOO = 6, 
                            Starting_brain_count= 0, 
                            MaxSpecialDist= 0.15,
                            max_offspring= 5,
                            max_pop_brains= 30,
                            max_mutations_per_gen=2,
                            import_brains_from_file=None,
                            import_population_from_file=None,
                            dir=None)

maxlist = []

#load all robots in a dir
dir = "NeatAI/pop_saves/sim_walking_wip/"
NeatAI_pop.add_new_species()

allfiles=os.listdir(dir)
allfiles.sort()
allfiles = [file_name for file_name in allfiles if (file_name.find("best_brain")!=-1) and (file_name.find("txt") != -1)]
allfiles_numbers = [int(filename[14:filename.find(".txt")]) for filename in allfiles]
allfiles_numbers, allfiles = zip(*sorted(zip(allfiles_numbers, allfiles),reverse=True))
allfiles = list(allfiles)
allnames = [name.strip(".txt") for name in allfiles]
custum_id_list = {}

for file_index,filename in enumerate(allfiles):
    new_brain = cl.brain_fenotype(15,6, import_from_file=filename, dir=dir)
    NeatAI_pop.species[0].add_brain(new_brain)
    id = f"S0:B{file_index}"
    custum_id_list.update({id : allnames[file_index]})

#save the mental brain
#NeatAI_pop.species[0].brains[0].save_mental_map(filename="best_brain_mental_map.pdf", 
#                                                dir=dir,
#                                                hide_direct_connections = True)


#read from sim_data_file
sim_file = open(dir + "sim_data.txt", "r")
sim_data_lines = sim_file.readlines()
sim_file.close()

sim_data_lines = [dataline.replace(","," ").split() for dataline in sim_data_lines]
max = [float(dataline[1]) for dataline in sim_data_lines]
avg = [float(dataline[3]) for dataline in sim_data_lines]
min = [float(dataline[2]) for dataline in sim_data_lines]
time = [float(dataline[4]) for dataline in sim_data_lines]
target_score = [50]*len(max)

#plot score plot
plt.figure()
plt.plot(max,color='green')
plt.plot(avg,color='blue')
plt.plot(min,color='red')
plt.plot(target_score, linestyle='dashed', color='red')
plt.legend(["max","min","avg","neutral score line"])
plt.xlabel("Generation [-]")
plt.ylabel("score [-]")
plt.grid()
plt.savefig(dir + "score_plot_post.pdf")
plt.close()
            
            
#plot time plot
total_time = sum(time)
h = total_time//3600
m = (total_time - h*3600)//60
s = total_time - h*3600 - m*60
plt.figure()
plt.plot(time)
plt.xlabel("Generation [-]")
plt.ylabel("time [s]")
plt.title(f"Total simulation time: {h}h {m}m {s}s")
plt.grid()
plt.savefig(dir + "time_plot_post.pdf")
plt.close()

NeatAI_pop.species[0].brains = [NeatAI_pop.species[0].brains[0]]

    
plt.figure()
gen = 0
for gen in range(1000000):
    sim_results, sim_data = mpb.simulate(NeatAI_pop, 
                    robot_type= "biped_2d_simple.urdf",
                    joint_friction=5,
                    torque_multiplier=400,
                    max_single_process_brains=70,
                    target_joint_velocity=2.5,
                    GUI=True,
                    time_controlled = False, 
                    step_limit = 2000,
                    time_limit = 100,
                    max_TPS= None,
                    debug= True,
                    show_IDs=True,
                    show_timer=False,
                    show_coords=False,
                    show_axis=False,
                    cam_focus_ID=None,
                    custum_id_list = custum_id_list)
    
    #calculate objective value
    res = objective_function_calculator(sim_results)
    print(res)
    maxlist.append(max(res))
    plt.figure()
    plt.plot(maxlist)
    plt.pause(1)
    plt.clf()
    
    
    
    
    