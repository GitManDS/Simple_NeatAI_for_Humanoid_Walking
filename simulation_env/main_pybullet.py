import pybullet as pb
import pybullet_data
import pybullet_utils.bullet_client as pbc   #this allows for the use of several clients of pybullet
import random as rnd
import threading as trd
from threading import Thread
from simulation_env import pybullet_supporting_functions as pbsf
from NeatAI import NeatAI_support_functions as NAIsf
import time
import math


class sim_client:
    def __init__(self, GUI = False, gravity = -9.81):
        if GUI:
            self.Client = pbc.BulletClient(connection_mode=pb.GUI)
        else:
            self.Client = pbc.BulletClient(connection_mode=pb.DIRECT)
            
        self.Client.setGravity(0,0,gravity)
        
        assets_folder = "C:/Users/diogo serra/Desktop/trabalhos, documentose afixos de programas/TUDelft-MEaer/een/even semester/AI/Bipedal agent project/simulation_env/assets"
        self.Client.setAdditionalSearchPath(assets_folder)
        
        #create physical environment (plane)
        planeId = self.Client.loadURDF("plane.urdf", useFixedBase=True) 
        
        pass
    
    def sim_loop(self, robot_list , brains_list,
             time_controlled=False, 
             limit_time = 5,
             step_limit = 1000, 
             max_TPS = None,
             debug = False,
             show_timer = False, 
             show_axis = False, 
             show_IDs = False,
             show_coords = False,
             cam_focus_ID = None):  
    
        ######################## TIME CONTROLLED ########################
        
        #run time controlled/limited (will run forever until GUI is closed)
        #uses limit time (in seconds) to stop simulation
        if time_controlled:
            
            #sets simulation to use real time
            self.Client.setRealTimeSimulation(1)
            
            clock_start = time.time()
            elapsed_time = 0
            timer_ID = None
            while True:
                ############################# OPTIONAL/debug #############################  
                if debug:
                    if show_timer:
                        timer_ID = pbsf.show_timer(clock_start, timer_ID)
                    if show_axis:
                        for robot_ID in robot_list:
                            pbsf.show_axis(robot_list = robot_list, robot_ID=robot_ID)
                    if show_IDs:
                        for robot_ID in robot_list:
                            pbsf.identify_robot(robot_ID, robot_list)
                    if show_coords:
                        for robot_ID in robot_list:
                            pbsf.show_coords(robot_list = robot_list, robot_ID=robot_ID)
                    if cam_focus_ID != None:
                        pbsf.focus_camera(robot_list = robot_list, robot_ID = cam_focus_ID)
                        
                #WRITE FUNCTIONS TO RUN IN CODE HERE!!!
                #
                    
                
                #
                #check if time limit has been reached
                elapsed_time = time.time() - clock_start
                if elapsed_time > limit_time:
                    break
                pass
            
        
        ######################## STEP CONTROLLED ########################
            
        #run without GUI and step-by-step limited (will run for simulation time and is limited by processing power)
        #needs a step limit, else it will assume one
        #if max_TPS is specified, then a pause will be added to match the TPS
        elif not time_controlled:
            #setup
            timer_ID = None
            step_ID = None
            clock_start = time.time()
            #step once to begin simulation, but define first step as step 0
            pb.stepSimulation()
            for step in range(step_limit):
                
                ############################# OPTIONAL/debug ############################# 
                if debug:
                    #all the debug functions that apply to all the robots
                    for robot_ID in robot_list:
                        pbsf.show_axis(robot_list = robot_list, robot_ID=robot_ID)
                        pbsf.identify_robot(robot_ID, robot_list)
                        pbsf.show_coords(robot_list = robot_list, robot_ID=robot_ID)
                    timer_ID = pbsf.show_timer(clock_start, timer_ID)
                    step_ID = pbsf.show_step_count(step, step_ID)
                    
                if cam_focus_ID != None:
                    pbsf.focus_camera(robot_list = robot_list, robot_ID = cam_focus_ID)   
                        
                #WRITE FUNCTIONS TO RUN IN CODE HERE!!!
                #
                
                torque_multiplier = 100      
                for i, robot_ID in enumerate(robot_list):
                    #get robot info
                    main_body_position, main_body_rotation, joint_pos_index = pbsf.get_robot_and_joints_position_rotation(robot_ID=robot_ID, robot_list=robot_list)
                    
                    #calculate the output of the brain which corresponds to the torque to apply to the robot
                    output, val = NAIsf.compute_output(brains_list[i], list(main_body_position)+list(joint_pos_index))
                    
                                
                    #multiply the output
                    output = [x*torque_multiplier for x in output]
                            
                    pbsf.apply_torque_to_robot(torque=output, robot_ID=robot_ID, robot_list=robot_list)
                    pass
                
                #
                #potential pause to match TPS
                if max_TPS != None:
                    time.sleep(1/max_TPS)
                
                #step simulation
                pb.stepSimulation()
            
            #automatic disconnect
            pb.disconnect() 
                
                
        #get simulation results
        #1- get the robot info for every robot
        position_results = {}
        for robot_ID in robot_list:
            main_body_position, main_body_rotation, joint_pos_index = pbsf.get_robot_and_joints_position_rotation(robot_list[robot_ID])
            position_results.update({robot_ID: main_body_position})
            
        #2- get simulation data
        sim_time = clock_start - time.time()
        avg_tps = step_limit/sim_time
        
        return position_results, [sim_time, avg_tps]


#way of implementing a thread with a return value
class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return



#initializes the simulation with standard conditions
#the environment includes a plane(ground/fixed) and gravity
#also defines if GUI is to be used or not
def sim_init(GUI=False, gravity = -9.81):
    if GUI == False:
        pb.connect(pb.DIRECT)  
    else:
        pb.connect(pb.GUI)
    
    #set gravity
    pb.setGravity(0,0,gravity)
    
    #advanced settings
    #pb.setAdditionalSearchPath(pybullet_data.getDataPath())
    assets_folder = "C:/Users/diogo serra/Desktop/trabalhos, documentose afixos de programas/TUDelft-MEaer/een/even semester/AI/Bipedal agent project/simulation_env/assets"
    pb.setAdditionalSearchPath(assets_folder)
    print(pybullet_data.getDataPath())
    
    #create physical environment
    planeId = pb.loadURDF("plane.urdf", useFixedBase=True) 
    
    return planeId

#MAIN SIMULATION CONTROL LOOP, EDIT HERE WHAT TO DO
#[!] time controlled simulations do not discount time spent on computations as opposed to time spent in stepping
#this is because this is a debug feature anyways and won't be used in the final version
#there are options for showing a timer, axis of the robot and the ID of the robot
#-> these only apply to time controlled simulations, step controlled simulations will show all of these if debug
#if a robot id is supplied to the cam_focus_ID arg then the camera will focus on that robot
#-> [!] setting it to "leading" will focus on the furthest robot in the y axis
#[!] debug must be set to True if any of the debug features are to be used (code efficiency)
def sim_loop(robot_list , brains_list,
             time_controlled=False, 
             limit_time = 5,
             step_limit = 1000, 
             max_TPS = None,
             debug = False,
             show_timer = False, 
             show_axis = False, 
             show_IDs = False,
             show_coords = False,
             cam_focus_ID = None):  
    
    ######################## TIME CONTROLLED ########################
    
    #run time controlled/limited (will run forever until GUI is closed)
    #uses limit time (in seconds) to stop simulation
    if time_controlled:
        
        #sets simulation to use real time
        pb.setRealTimeSimulation(1)
        
        clock_start = time.time()
        elapsed_time = 0
        timer_ID = None
        while True:
            ############################# OPTIONAL/debug #############################  
            if debug:
                if show_timer:
                    timer_ID = pbsf.show_timer(clock_start, timer_ID)
                if show_axis:
                    for robot_ID in robot_list:
                        pbsf.show_axis(robot_list = robot_list, robot_ID=robot_ID)
                if show_IDs:
                    for robot_ID in robot_list:
                        pbsf.identify_robot(robot_ID, robot_list)
                if show_coords:
                    for robot_ID in robot_list:
                        pbsf.show_coords(robot_list = robot_list, robot_ID=robot_ID)
                if cam_focus_ID != None:
                    pbsf.focus_camera(robot_list = robot_list, robot_ID = cam_focus_ID)
                    
            #WRITE FUNCTIONS TO RUN IN CODE HERE!!!
            #
                
            
            #
            #check if time limit has been reached
            elapsed_time = time.time() - clock_start
            if elapsed_time > limit_time:
                break
            pass
        
    
    ######################## STEP CONTROLLED ########################
        
    #run without GUI and step-by-step limited (will run for simulation time and is limited by processing power)
    #needs a step limit, else it will assume one
    #if max_TPS is specified, then a pause will be added to match the TPS
    elif not time_controlled:
        #setup
        timer_ID = None
        step_ID = None
        clock_start = time.time()
        #step once to begin simulation, but define first step as step 0
        pb.stepSimulation()
        for step in range(step_limit):
            
            ############################# OPTIONAL/debug ############################# 
            if debug:
                #all the debug functions that apply to all the robots
                for robot_ID in robot_list:
                    pbsf.show_axis(robot_list = robot_list, robot_ID=robot_ID)
                    pbsf.identify_robot(robot_ID, robot_list)
                    pbsf.show_coords(robot_list = robot_list, robot_ID=robot_ID)
                timer_ID = pbsf.show_timer(clock_start, timer_ID)
                step_ID = pbsf.show_step_count(step, step_ID)
                
            if cam_focus_ID != None:
                pbsf.focus_camera(robot_list = robot_list, robot_ID = cam_focus_ID)   
                    
            #WRITE FUNCTIONS TO RUN IN CODE HERE!!!
            #
            
            torque_multiplier = 100      
            for i, robot_ID in enumerate(robot_list):
                #get robot info
                main_body_position, main_body_rotation, joint_pos_index = pbsf.get_robot_and_joints_position_rotation(robot_ID=robot_ID, robot_list=robot_list)
                
                #calculate the output of the brain which corresponds to the torque to apply to the robot
                output, val = NAIsf.compute_output(brains_list[i], list(main_body_position)+list(joint_pos_index))
                
                               
                #multiply the output
                output = [x*torque_multiplier for x in output]
                        
                pbsf.apply_torque_to_robot(torque=output, robot_ID=robot_ID, robot_list=robot_list)
                pass
            
            #
            #potential pause to match TPS
            if max_TPS != None:
                time.sleep(1/max_TPS)
            
            #step simulation
            pb.stepSimulation()
        
        #automatic disconnect
        pb.disconnect() 
            
            
    #get simulation results
    #1- get the robot info for every robot
    position_results = {}
    for robot_ID in robot_list:
        main_body_position, main_body_rotation, joint_pos_index = pbsf.get_robot_and_joints_position_rotation(robot_list[robot_ID])
        position_results.update({robot_ID: main_body_position})
        
    #2- get simulation data
    sim_time = clock_start - time.time()
    avg_tps = step_limit/sim_time
      
    return position_results, [sim_time, avg_tps]

#sim loop but with parallel computing
#[!]NOT WORKING!
def sim_loop_parallel(robot_list , brains_list,
             time_controlled=False, 
             limit_time = 5,
             step_limit = 1000, 
             max_TPS = None,
             debug = False,
             show_timer = False, 
             show_axis = False, 
             show_IDs = False,
             show_coords = False,
             cam_focus_ID = None):  
    
    #storage
    positions = {}
    sim_data = []
    
    #max number of threads
    max_threads = 4
    threads_list = []
    
    #get list of brains
    brain_max_index = len(brains_list)-1
    
    #catch case for less brains than threads
    if (brain_max_index + 1)  < max_threads:
        max_threads = brain_max_index
        
    #work with dict
    keys_list = list(robot_list.keys())
    
    #account for the fact that max_threads < brain_max_index
    cursor = 0
    while cursor <= brain_max_index:
        #assign thread task to thread ID
        if (brain_max_index - cursor) + 1  < max_threads:
            max_threads = (brain_max_index - cursor) + 1
        for thread_index in range(max_threads):
            
            #find keys to extract from dictionary
            keys_to_use = keys_list[ cursor : cursor + round(brain_max_index/max_threads) ]
            
            new_robot_list = {}
            #extract keys
            for key in keys_to_use:
                new_robot_list.update({key: robot_list[key]})
            
            #assign thread task
            new_thread = ThreadWithReturnValue(target=sim_loop, args = 
                                                        (new_robot_list, 
                                                        brains_list[ cursor : cursor + round(brain_max_index/max_threads)],
                                                        time_controlled, 
                                                        limit_time,
                                                        step_limit, 
                                                        max_TPS,
                                                        debug,
                                                        show_timer, 
                                                        show_axis, 
                                                        show_IDs,
                                                        show_coords,
                                                        cam_focus_ID))
            
            #append thread to threads list and update cursor
            threads_list.append(new_thread)
            cursor += round(brain_max_index/max_threads)
            new_thread.start()
            print("Thread started")
            
        #initialize and run threads
        #for thread_id in threads_list:
        #    thread_id.start()
            
        #clear threads list 
        #threads_list = []
    
    #wait for all threads to finish
    for thread_id in threads_list:
        positions.update(thread_id.join()[0])
        sim_data.append(thread_id.join()[1])
    
    return positions, sim_data


#creates a new robot in the simulation
#robot_ID needs to be supplied or else it will be set to a random value
#robot list is a dictionary with the Robots_ID as keys and the robot object as values
def create_robot(robot_ID=-1,robot_list={},robot_type = "biped_norotation.urdf"):
    
    #handle the ID of the robot
    if robot_ID == -1:
        robot_ID = "RND_" + str(rnd.uniform(0,1000))
        
    #get a starting position for the robot
    #for that we need to know how many robots are already in the simulation
    #z spacing of 1.1 matches roughly the height of the robot
    #2 [unit] is roughly enough spacing between 2 robots
    robot_count = len(robot_list)
    starting_pos = [len(robot_list),0,1.1]
    starting_orientation = pb.getQuaternionFromEuler([0,0,0])
    
    #create the robot
    robot = pb.loadURDF(robot_type, starting_pos, starting_orientation, useFixedBase=False)
    
    #relax the muscles/define standard friction
    #must not be 0
    jointFrictionForce = 10
    for joint in range(pb.getNumJoints(robot)):
        pb.setJointMotorControl2(robot, joint, pb.POSITION_CONTROL, force=jointFrictionForce)
        
    #reference joints should be set at 0
    #this makes it so they dont oppose movement as they are simply plane constraints
    pb.setJointMotorControl2(robot, 0,  pb.POSITION_CONTROL, force=0) #origin to z
    pb.setJointMotorControl2(robot, 1,  pb.POSITION_CONTROL, force=0) #z to x
    pb.setJointMotorControl2(robot, 2,  pb.POSITION_CONTROL, force=0) #x to y
        
    #append to dictionary
    robot_list.update({robot_ID: robot})
    
    return robot_list

