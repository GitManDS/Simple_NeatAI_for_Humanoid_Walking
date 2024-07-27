#libraries
import pybullet as pb
import sys, os

#files from other directories
from simulation_env import assisting_functions as af
from simulation_env import main_pybullet as mpb

#main dir files
import sim_AI_connection_functions as sim_AI


#start the simulation
mpb.sim_init(GUI = True)

#create 2 robots
robot_list = {}
for i in range(2):
    mpb.create_robot("A32"+str(i), robot_list = robot_list)
    
#run simulation
sim_AI.sim_loop(robot_list, time_controlled = True, sim_time = 5)
    


#end simulation
pb.disconnect()