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

NeatAI_pop = cl.population(NOI = 11, NOO = 8,Starting_brain_count= 4, MaxSpecialDist= 0.2,max_offspring= 2,max_pop_brains= 10,max_mutations_per_gen=1)

brain = cl.brain_fenotype(11,8)
brain.load_mental_connections("best_brain.txt")

positions, sim_data = mpb.simulate(brains_list=[brain],keys_list=["best_brain"], 
                GUI=True,
                time_controlled = False, 
                step_limit = 500,
                time_limit = 10,
                max_TPS= None,
                debug= True,
                show_IDs=True,
                show_timer=True)