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
    scale = 30

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
        
        L_Uleg_pos_parity = 0.7
        R_Uleg_pos_parity = -0.7
        
        L_Lleg_vel_parity = 1
        L_ankle_vel_parity = 1
        R_Lleg_vel_parity = 1
        R_ankle_vel_parity = 1
        
        Lower_leg_integral = 0
        
        frequency_penalty_counter = 0
        frequency_bonus_counter = 0
        
        Leg_correct_vel_counter = 0
        
        r_u_leg_TEMPLIST = []
        l_u_leg_TEMPLIST = []
        l_u_parity = []
        r_u_parity = []
        
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
            L_leg_vel_integral += abs(step_result[6])
            #integrate the input values over the step for the R leg
            #R_leg_pos.append(step_result[2])
            R_leg_pos_integral += step_result[3]
            R_leg_vel_integral += abs(step_result[9])
            
            #motivate it to bend knees at upright positions
            if step_result[0] < 0.1 and step_result[0] > -0.1:
                Lower_leg_integral += -step_result[1]
            if step_result[3] < 0.1 and step_result[3] > -0.1:
                Lower_leg_integral += -step_result[4]
            
            #integrate the position z over the step
            z_pos_integral += abs(step_result[14]-1.1)
            
            #integrate the y velocity values over the step
            #target velocity is 1
            y_vel_integral += (step_result[19])
            
            #integrate the rotation values over the step for the x,y,z values
            #this is done by summing the absolute values of the rotation values
            rot_integral += abs(step_result[15]-(-0.1))
            
            #get the frequency of the leg movement
            #the leg parity is positive and set at 0.2
            #if step_result[0] > L_Uleg_vel_parity and L_Uleg_vel_parity > 0:
            #    frequency_bonus_counter += 1
            #    L_Uleg_pos_parity *= -1
            #the leg parity is negative and set at -0.2
            #elif step_result[0] < L_Uleg_vel_parity and L_Uleg_vel_parity < 0:
            #    frequency_bonus_counter += 1
            #    L_Uleg_pos_parity *= -1
            
            #Incentivize robot to move his legs in a coordinated fashion
            #[!]WARNING: THIS CODE REPLACES THE PREVIOUS, DO NOT HAVE BOTH ACTIVE   
            #Left Leg  
            #if leg is behind the target, the velocity should be positive
            if step_result[0] < L_Uleg_pos_parity and L_Uleg_pos_parity > 0:
                if step_result[6] > 0:
                    Leg_correct_vel_counter += 1
                else:
                    Leg_correct_vel_counter -= 1
            #if the leg is in front of the target, the velocity should be negative
            elif step_result[0] > L_Uleg_pos_parity and L_Uleg_pos_parity < 0:
                if step_result[6] < 0:
                    Leg_correct_vel_counter += 1
                else:
                    Leg_correct_vel_counter -= 1
            #the only other combinations is that the leg is out of the [-0.7 and 0.7 range]
            #in which case, invert the target position
            else:
                L_Uleg_pos_parity *= -1
                
            l_u_parity.append(L_Uleg_pos_parity)  
            
            #Right Leg
            #if leg is behind the target, the velocity should be positive
            if step_result[3] < R_Uleg_pos_parity and R_Uleg_pos_parity > 0:
                if step_result[9] > 0:
                    Leg_correct_vel_counter += 1
                else:
                    Leg_correct_vel_counter -= 1
            #if the leg is in front of the target, the velocity should be negative
            elif step_result[3] > R_Uleg_pos_parity and R_Uleg_pos_parity < 0:
                if step_result[9] < 0:
                    Leg_correct_vel_counter += 1
                else:
                    Leg_correct_vel_counter -= 1
            #the only other combinations is that the leg is out of the [-0.7 and 0.7 range]
            #in which case, invert the target position
            else:
                R_Uleg_pos_parity *= -1
                
            r_u_leg_TEMPLIST.append(Leg_correct_vel_counter)
            r_u_parity.append(R_Uleg_pos_parity)    
            
            
            if step_result[7] * L_Lleg_vel_parity < 0:
                frequency_penalty_counter += 1
                L_Lleg_vel_parity *= -1
            if step_result[8] * L_ankle_vel_parity < 0:
                frequency_penalty_counter += 1
                L_ankle_vel_parity *= -1
            if step_result[10] * R_Lleg_vel_parity < 0:
                frequency_penalty_counter += 1
                R_Lleg_vel_parity *= -1
            if step_result[11] * R_ankle_vel_parity < 0:
                frequency_penalty_counter += 1
                R_ankle_vel_parity *= -1
          
        contributions = []  
        
        #get the final distance travelled 
        distance_travelled = sim_results[robot_ID][-1][13]

        '''STANDING TRAINING'''
        '''
        #initial value is target_score
        contributions.append(target_score)
        
        #deduct points for the z position integral
        #the integral should be scaled by the max value of the integral *  area of the rectangle with height 1 and width step_count)
        contributions.append(-abs(z_pos_integral/(1.1*step_count)) * 2 * scale)
        
        #update the objective value for a penalty related to the rotation integral
        #the integral should be scaled by the max value of the integral *  area of the rectangle with height 1 and width step_count)
        contributions.append(-abs(((rot_integral)/(1*step_count))) * 1 * scale)
        
        #also remove points for velocity
        contributions.append(-abs((y_vel_integral)/(2*step_count)) * 1 * scale)
        '''
        
        
        '''WALKING TRAINING'''
        
        #initial value is target_score
        contributions.append(50)
        
        #deduct points for the z position integral
        #the integral should be scaled by the max value of the integral *  area of the rectangle with height 1 and width step_count)
        contributions.append(-abs(z_pos_integral/(1.1*step_count)) * 5 * scale)
        
        #update the objective value for a penalty related to the rotation integral
        #the integral should be scaled by the max value of the integral *  area of the rectangle with height 1 and width step_count)
        contributions.append(-abs(((rot_integral)/(1*step_count))) * 3 * scale)
        
        #give contribution for the bent knees
        #the integral should be scaled by the max value of the integral *  area of the rectangle with height 1 and width step_count)
        #contributions.append((Lower_leg_integral/(2*step_count)) * 10 * scale)
        
        #update the objective value with distance travelled
        #contributions.append(distance_travelled * 0.1 * scale)
        
        #add bonus points for velocity matched
        #divide by the integral of the desired velocity
        #contributions.append((y_vel_integral)/(2*step_count) * 2 * scale)
        
        #penalize for twitching
        #normalized by the number of steps which would correspond to full twitching behaviour
        #times 4 due to all the joints being studied
        #contributions.append(-abs(frequency_penalty_counter/(step_count*4)) * 1 * scale)
        
        #add bonus for alternating legs
        #normalized by the number of steps which would correspond to full alternating behaviour
        #times 2 due to all the joints being studied
        contributions.append((Leg_correct_vel_counter/(step_count*4)) * 3 * scale)  
        
        #get objective value
        obj_value.append(sum(contributions))
                         
        r_u_leg_TEMPLIST = [Leg_correct_vel_counter/max(r_u_leg_TEMPLIST) for Leg_correct_vel_counter in r_u_leg_TEMPLIST]
        #plot all the inputs
        plt.figure()
        for stored_index in [0,6]:
            plt.plot(stored_inputs[stored_index], label = f"input {stored_index}")
        plt.plot(r_u_leg_TEMPLIST, label = "R_Uleg_pos_parity")
        plt.plot(l_u_parity, label = "L_Uleg_pos_parity")
        plt.plot()
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
dir = "NeatAI/pop_saves/sim1724335223/"
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
maxi = [float(dataline[1]) for dataline in sim_data_lines]
avg = [float(dataline[3]) for dataline in sim_data_lines]
min = [float(dataline[2]) for dataline in sim_data_lines]
time = [float(dataline[4]) for dataline in sim_data_lines]
target_score = [50]*len(maxi)

#plot score plot
plt.figure()
plt.plot(maxi,color='green')
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
    
    
    
    
    