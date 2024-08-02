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


new_sim = mpb.sim_client(GUI = False)


#disconnect   
pb.disconnect()