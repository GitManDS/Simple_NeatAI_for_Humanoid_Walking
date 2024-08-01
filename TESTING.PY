#libraries
import pybullet as pb
import sys, os

#files from other directories
from simulation_env import pybullet_supporting_functions as pbsf
from NeatAI import NeatAI_support_functions as NAIsf
from simulation_env import main_pybullet as mpb
from NeatAI import classes as cl

#main dir files
import sim_AI_connection_functions as sim_AI


mainl, li1 = NAIsf.sort_lists([3,4,2,6,9,2],[[1,2,3,4,5,6],[6,5,4,3,2,1]])

#sim
mpb.sim_init(GUI = True)

#robot
robot_list = {}
robot_list.update(mpb.create_robot(robot_ID="testrobot",robot_list=robot_list, robot_type="biped_freeman.urdf"))

#run
mpb.sim_loop(robot_list, cl.population(NOI = 11, NOO = 8, Starting_brain_count= 1),
             time_controlled = True, 
             step_limit = 500, 
             show_axis= True,
             show_timer= True,
             debug= True, 
             max_TPS = 60,
             cam_focus_ID="testrobot")
    
pb.disconnect()