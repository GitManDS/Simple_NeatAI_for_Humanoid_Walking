import pybullet as pb
import pybullet_data
import pybullet_utils.bullet_client as pbc   #this allows for the use of several clients of pybullet
import random as rnd
import threading as trd
from threading import Thread
import multiprocessing as mp
from simulation_env import pybullet_supporting_functions as pbsf
from NeatAI import NeatAI_support_functions as NAIsf
import time
import math
import numpy as np

#sim class client used to configure, manage and start a single simulation client
class sim_client:
    def __init__(self, GUI = False, gravity = -9.81, robot_type = "biped_freeman.urdf"):
        if GUI:
            self.Client = pbc.BulletClient(connection_mode=pb.GUI)
        else:
            self.Client = pbc.BulletClient(connection_mode=pb.DIRECT)
            
        #options and other parameters
        self.Client.setGravity(0,0,gravity)             #set gravity
        
        self.robot_list = {}                            #dictionary of robots used
        self.robot_type = robot_type                    #type of robot to be used
        self.joint_friction = 10                        #friction of the robot  
        self.joint_torque_multiplier = 100              #torque multiplier for the robot
        self.target_joint_velocity = 2                #target joint velocity for the robot
        
        self.clock_start = 0                            #start time of the simulation
        self.step   = 0                                 #current/last step of the simulation
        self.timer_id = None                            #timer id for the timer function (if called/used)
        self.step_id = None                             #step id for the step count function (if called/used)
        self.nametag_id = None                          #nametag id for the identify robot function (if called/used)
        
        self.robot_sim_results = {}                     #any sim results data that needs to be exported
        self.sim_data = []                              #simulation data
        self.robot_joint_count = 0                      #joint count of the robot (to be updated)
        self.relevant_joints = [5,6,8,9]                #joints to search info for and apply forces to
        
        #add assets folder
        assets_folder = "C:/Users/diogo serra/Desktop/trabalhos, documentose afixos de programas/TUDelft-MEaer/een/even semester/AI/Bipedal agent project/simulation_env/assets"
        self.Client.setAdditionalSearchPath(assets_folder)
        
        #create physical environment (plane)
        planeId = self.Client.loadURDF("plane.urdf", useFixedBase=True, basePosition=[0,0,0]) 
        
        pass
    
    #MAIN SIMULATION CONTROL LOOP, EDIT HERE WHAT TO DO
    #[!] time controlled simulations do not discount time spent on computations as opposed to time spent in stepping
    #this is because this is a debug feature anyways and won't be used in the final version
    #there are options for showing a timer, axis of the robot and the ID of the robot
    #-> these only apply to time controlled simulations, step controlled simulations will show all of these if debug
    #if a robot id is supplied to the cam_focus_ID arg then the camera will focus on that robot
    #-> [!] setting it to "leading" will focus on the furthest robot in the y axis
    #[!] debug must be set to True if any of the debug features are to be used (code efficiency)
    def sim_loop(self, brains_list,
             time_controlled=False, 
             time_limit = 5,
             step_limit = 1000, 
             max_TPS = None,
             debug = False,
             show_timer = False, 
             show_axis = False, 
             show_IDs = False,
             show_coords = False,
             cam_focus_ID = None):  
    
        #start clock
        self.clock_start = time.time()
        
        #SET CAMERA (centered)
        self.Client.resetDebugVisualizerCamera(cameraDistance=5, 
                                               cameraYaw=65, 
                                               cameraPitch=-25, 
                                               cameraTargetPosition=[0,0,0])
        
        #for the storage of any input and the position of the robots
        #need to initialize it here to avoid errors
        self.robot_sim_results = {}
        for robot_ID in self.robot_list:
            self.robot_sim_results.update({robot_ID: []})  
            
        #copy the robot list to avoid issues with the dictionary changing size during iteration
        robot_list_copy = self.robot_list.copy() 
        
        '''REMOVE THIS LATER'''
        #input_debug = []
        
        
        ######################## TIME CONTROLLED ########################
        
        #run time controlled/limited (will run forever until GUI is closed)
        #uses limit time (in seconds) to stop simulation
        if time_controlled:
            
            #sets simulation to use real time
            self.Client.setRealTimeSimulation(1)
            
            elapsed_time = 0
            while True:
                ############################# OPTIONAL/debug #############################  
                if debug:
                    if show_timer:
                        self.show_timer()
                    if show_axis:
                        self.show_axis()
                    if show_IDs:
                        self.identify_robots()
                    if show_coords:
                        self.show_coords()
                    if cam_focus_ID != None:
                        self.focus_camera(robot_ID=cam_focus_ID)
                        
                #WRITE FUNCTIONS TO RUN IN CODE HERE!!!
                #
                
                #
                #check if time limit has been reached
                elapsed_time = time.time() - self.clock_start
                if elapsed_time > time_limit:
                    break
                pass
            
        
        ######################## STEP CONTROLLED ########################
            
        #run without GUI and step-by-step limited (will run for simulation time and is limited by processing power)
        #needs a step limit, else it will assume one
        #if max_TPS is specified, then a pause will be added to match the TPS
        elif not time_controlled:
            #step once to begin simulation, but define first step as step 0
            self.Client.stepSimulation()
            
            #get initial robot positions
            main_body_position_old = []
            for robot_ID in self.robot_list:
                main_body_position, main_body_rotation, joint_pos, joint_vel = self.get_robot_and_joints_position_rotation(self.robot_list[robot_ID])
                main_body_position_old.append(main_body_position)
            
            for self.step in range(step_limit):
                
                #catch case of no robots left to sim
                if len(robot_list_copy) == 0:
                    break
                
                ############################# OPTIONAL/debug ############################# 
                if debug:
                    if show_timer:
                        self.show_timer()
                    if show_axis:
                        self.show_axis()
                    if show_IDs:
                        self.identify_robots()
                    if show_coords:
                        self.show_coords()
                if cam_focus_ID != None:
                    if cam_focus_ID == "BEST":
                        #find the robot with the highest y position
                        y_pos = 0
                        for robot_ID in robot_list_copy:
                            main_body_position, main_body_rotation, joint_pos, joint_vel = self.get_robot_and_joints_position_rotation(robot_ID=robot_ID, joint_list=self.relevant_joints)
                            if main_body_position[1] > y_pos:
                                y_pos = main_body_position[1]
                                cam_focus_ID = robot_ID   
                                
                    self.focus_camera(robot_ID=cam_focus_ID) 
                        
                #WRITE FUNCTIONS TO RUN IN CODE HERE!!!
                #
    
            
                #for i, robot_ID in enumerate(self.robot_list):
                i=0
                robot_ID_list = list(robot_list_copy.keys())
                while i < len(robot_list_copy):
                    robot_ID = robot_ID_list[i]
                    #get robot info
                    #[5-L upper leg, 6- L lower leg, 8-R upper leg, 9-R lower leg]
                    main_body_position, main_body_rotation, joint_pos, joint_vel = self.get_robot_and_joints_position_rotation(robot_ID=robot_ID, joint_list=self.relevant_joints)
                               
                    #convert rotation to euler angles
                    main_body_rotation = list(self.Client.getEulerFromQuaternion(main_body_rotation))  
                    main_body_rotation = [i/math.pi for i in main_body_rotation]     
                    
                    #get velocity from the last step (units/step) and update old pos
                    velocity = [main_body_position[j] - main_body_position_old[i][j] for j in range(3)]
                    main_body_position_old[i] = main_body_position
                    
                    #normalize the joint and pos inputs
                    #rotation goes from -1 to 1
                    velocity = [i*100 for i in velocity]
                    joint_pos = joint_pos
                    joint_vel = [i/10 for i in joint_vel]
                    
                    
                    #create input
                    input = [velocity[1]] + [velocity[2]] + [main_body_rotation[0]] + joint_pos + joint_vel   
                    
                    '''REMOVE THIS LATER'''
                    #input_debug.append(input)
                            
                    #save the results for this robot
                    #include step count as a way to measure time
                    self.robot_sim_results[robot_ID].append(joint_pos +  joint_vel+ list(main_body_position)+ 
                                                            main_body_rotation+ velocity+ [self.step])
                    
                    #if the robot fell, delete it
                    if main_body_position[2] < 0.25:
                        self.Client.removeBody(robot_list_copy[robot_ID])
                        robot_list_copy.pop(robot_ID)
                        robot_ID_list.pop(i)
                        
                        #dont iterate to next robot since this one was deleted from the list
                    
                    else:
                        #continue with the simulation for this robot
                        
                        #calculate the output of the brain which corresponds to the torque to apply to the robot
                        output, val = brains_list[i].compute_output(input)
                        
                        #self.apply_torque_to_robot(torque=output, robot_ID=robot_ID, joint_list=[5,6,8,9])
                        output=pbsf.convert_input_to_joint_ranges(output)
                        self.apply_position_input_to_robot(position=output, robot_ID=robot_ID, joint_list=self.relevant_joints)
                        
                        #next robot
                        i += 1
                
                #
                #potential pause to match TPS
                if max_TPS != None:
                    time.sleep(1/max_TPS)
                
                #step simulation
                self.Client.stepSimulation()
                            
                      
        #1- get simulation data
        sim_time = self.clock_start - time.time()
        avg_tps = step_limit/sim_time
        self.sim_data = [sim_time, avg_tps]
        
        #automatic disconnect/close the sim
        self.Client.disconnect() 
        
        '''REMOVE THIS LATER'''
        '''USEFULL FOR TUNING NORMALIZATION
        input_debug_max = input_debug[0]
        max_index = [0]*len(input_debug_max)
        for data_index in range(len(input_debug[0])):
            for entry_index,entry in enumerate(input_debug):
                if abs(input_debug_max[data_index]) < abs(entry[data_index]):
                    #found new max, store it
                    input_debug_max[data_index] = abs(entry[data_index])
                    max_index[data_index] = entry_index
                    
        print(input_debug_max)
        print(max_index)
        '''    
        
        #return for immediate post processing
        return self.robot_sim_results, self.sim_data

    #################### ROBOT CONTROL ####################

    #creates a new robot in the simulation
    #for every brain the the population
    def match_brains_to_robots(self, brains_list, brain_keys=None):
        for brain_index, brain in enumerate(brains_list):
            self.add_robot(robot_ID = brain_keys[brain_index])
          
        #manage collisions
        for robot_ID in self.robot_list:
            last_link_index = 13
            for link_id in range(0,last_link_index+1):
                #disable the robot collisions between each other
                self.Client.setCollisionFilterGroupMask(self.robot_list[robot_ID], link_id, 0, 0)
                #enable the robot collisions with the plane
                #0- plane link id, #1 - enablecollisions
                plane_ID = 0
                self.Client.setCollisionFilterPair(self.robot_list[robot_ID], plane_ID, link_id, 0, 1)
            pass         
          

        pass

    #returns the position of the body in the world, aswell as 
    #[!]can be expanded to give contact points and forces
    #the outputs are not stored in variables since they are already stored inside the simulation client
    def get_robot_and_joints_position_rotation(self, robot = None, robot_ID = None, joint_list = None):

        ### get robot ###
        if (robot_ID != None and self.robot_list != None):
            robot = self.robot_list[robot_ID]
            pass
        
        elif robot == None:
            print("No robot to show axis on, quitting axis display")
            pass
        #################

        #head joint / body position
        #dont need the position of all the links, just the position of the base and the position *index* of the joints
        #4 is the index of the torso link
        main_body_position, main_body_rotation = self.Client.getLinkState(robot,4)[0:2]

        #object joints
        #Get the position index of each index from -a to a
        #firts 5 joints are the reference joints
        if joint_list == None:
            joint_list = range(5,self.robot_joint_count)
    
        joint_pos = []
        joint_vel = []
        for i in joint_list:
            joint_pos.append(self.Client.getJointState(robot,i)[0])
            joint_vel.append(self.Client.getJointState(robot,i)[1])
            pass


        return main_body_position, main_body_rotation, joint_pos, joint_vel

    #will apply a torque to the the joints of the robot
    #accepts a list of torques to apply to the robot in the following order of joints
    def apply_torque_to_robot(self, torque, robot = None, robot_ID = None, joint_list = None):
        
        ### get robot ###
        if (robot_ID != None and self.robot_list != None):
            robot = self.robot_list[robot_ID]
            pass
        
        elif robot == None:
            print("No robot to show axis on, quitting axis display")
            pass
        #################
        
        #multiply the torque
        torque = [x*self.joint_torque_multiplier for x in torque]
        
        #first 5 joints are reference joints
        index = 0
        if joint_list == None:
            joint_list = range(5,self.robot_joint_count)
            
        for joint_index in joint_list:
            self.Client.setJointMotorControl2(robot, joint_index, self.Client.TORQUE_CONTROL, force=torque[index])
            index += 1
        
        pass

    #will set the objective end position of each joint of the robot
    #uses torque multiplier as a limit torque 
    def apply_position_input_to_robot(self, position, robot = None, robot_ID = None, joint_list = None):
        
        ### get robot ###
        if (robot_ID != None and self.robot_list != None):
            robot = self.robot_list[robot_ID]
            pass
        
        elif robot == None:
            print("No robot to show axis on, quitting axis display")
            pass
        #################
        
        #first 5 joints are reference joints
        if joint_list == None:
            joint_list = range(5,self.robot_joint_count)
            
        index = 0
        for joint_index in joint_list:
            self.Client.setJointMotorControl2(robot, joint_index, 
                                              self.Client.POSITION_CONTROL, 
                                              targetPosition = position[index], 
                                              targetVelocity = self.target_joint_velocity,
                                              force=self.joint_torque_multiplier)
            index += 1
        
        pass

    ################### VISUAL FUNCTIONS ###################
    #will focus the camera on a robot or on an robot ID
    #if the robot ID is supplied, it will focus on that robot
    def focus_camera(self, robot = None, robot_ID = None):
        
        if (robot_ID != None and self.robot_list != None):
            robot = self.robot_list[robot_ID]
            pass
        
        if robot != None:
            Pos=self.Client.getLinkState(robot,4)[0]
            self.Client.resetDebugVisualizerCamera(3, 
                                        -45, 
                                        -45, 
                                        Pos)
        else:
            print("No robot to focus on, quitting focusing")
            pass

        pass
    
    #this will place a text above the robot with the robot ID for 1 step
    #if the robot ID is supplied, it will indentify that robot
    #else it will identify all robots
    def identify_robots(self,robot_ID=None):
        
        #get head position
        if robot_ID == None:
            robots_to_use = self.robot_list
        else:
            robots_to_use = {robot_ID: self.robot_list[robot_ID]}
            
        for robot in robots_to_use:
            #get head position to place the text
            head_pos = self.Client.getLinkState(self.robot_list[robot],3)[0]
            
            #eliminate the last nametags
            if self.nametag_id != None:
                for nametag_id in self.nametag_id:
                    self.Client.removeUserDebugItem(nametag_id)
                pass
            self.nametag_id=[]
            
            #place debug text
            self.nametag_id.append(self.Client.addUserDebugText(robot,[head_pos[0] - 0.25 , head_pos[1], head_pos[2] + 0.5 ],textColorRGB=[0,0,0], textSize=1))
        
        pass

    #when given a start date (time lib), this function will display a clock on the topright corner
    #with the elapsed time, updating every function loop or step
    def show_timer(self):
        #get elapsed time
        elapsed_time = time.time() - self.clock_start
        
        #remove last timer
        if self.timer_id != None:
            self.Client.removeUserDebugItem(self.timer_id)
            pass
    
        #place debug text
        self.timer_ID = self.Client.addUserDebugText("Time: " + str(round(elapsed_time,2)),[0,0,0],textColorRGB=[0,0,0], textSize=1)
        
        pass

    #shows step count above timer
    def show_step_count(self):
             
        #eliminate debug text
        if self.step_id != None:
            self.Client.removeUserDebugItem(self.step_id)
            pass
        #place debug text
        self.step_id = self.Client.addUserDebugText("Step: " + str(self.step),[0,0,0.2],textColorRGB=[0,0,0], textSize=1)
        
        pass

    #this will show the axis of the robot in the simulation for 1 step
    #if the robot ID is supplied, it will show the axis of that robot
    #else, all robots will have their axis shown
    def show_axis(self, robot_ID = None):
        
        #colors
        orange = [1,0.5,0]
        blue = [0,0,1]
        black = [0,0,0]
        
        #line length
        leng = 0.6
        
        if robot_ID == None:
            robots_to_use = self.robot_list
        else:
            robots_to_use = {robot_ID: self.robot_list[robot_ID]}
            
        #go through all robots
        for robot in robots_to_use:
            #get current axis position
            #z=1, x=2 , y=3
            pos_y = self.Client.getLinkState(robots_to_use[robot],2)[0]
            pos_x = self.Client.getLinkState(robots_to_use[robot],1)[0]
            pos_z = self.Client.getLinkState(robots_to_use[robot],0)[0]
            
            pos_y2 = [pos_y[0],leng+pos_y[1],pos_y[2]]
            pos_x2 = [leng+pos_x[0],pos_x[1],pos_x[2]]
            pos_z2 = [pos_z[0],pos_z[1],leng+pos_z[2]]
            
            #lifetime
            Ltime = 1        #movie 1/fps
            
            #axis
            self.Client.addUserDebugLine(pos_z, pos_z2 , lineColorRGB=orange, lineWidth=0.02, lifeTime=Ltime)
            self.Client.addUserDebugLine(pos_x,pos_x2, lineColorRGB=blue, lineWidth=0.02, lifeTime=Ltime)
            self.Client.addUserDebugLine(pos_y,pos_y2, lineColorRGB=black, lineWidth=0.02, lifeTime=Ltime)
            
            #axis text
            self.Client.addUserDebugText("Z",pos_z2,textColorRGB=black, textSize=1, lifeTime=Ltime)
            self.Client.addUserDebugText("X",pos_x2,textColorRGB=black, textSize=1, lifeTime=Ltime)
            self.Client.addUserDebugText("Y",pos_y2,textColorRGB=black, textSize=1, lifeTime=Ltime)
                
        pass

    #will display atop the name of the robot the coordinates of the robot
    #by default, it will display the coordinates of the body (torso)
    def show_coords(self, robot_ID = None):
        
        if robot_ID == None:
            robots_to_use = self.robot_list
        else:
            robots_to_use = {robot_ID: self.robot_list[robot_ID]}
            
        for robot in robots_to_use:
            #get the coordinates
            #torso rot is not used
            torso_pos, torso_rot = self.Client.getLinkState(robots_to_use[robot],4)[0:2]
            
            #get head position to place the text
            head_pos = self.Client.getLinkState(robots_to_use[robot],3)[0]
            
            #lifetime
            Ltime = 1        #movie 1/fps
            
            #place debug text
            #-0.5 to help it be more centered
            #+1 to bring it up
            self.Client.addUserDebugText(f"x:{round(torso_pos[0],2)} y:{round(torso_pos[1],2)} z:{round(torso_pos[2],2)}" ,
                                torso_pos,
                                textColorRGB=[0,0,0], 
                                textSize=1, 
                                lifeTime=Ltime)
  
        pass

    #################### INFORMATION ####################

    #will show the joint information of the robot in the following format
    #<joint index> [joint type] joint name: pos=position, vel=velocity
    #additionally allows for type filetering 
    def print_joint_info(self, robot_ID = None, type = None):
        
        ### get robot ###
        if (robot_ID != None and self.robot_list != None):
            robot = self.robot_list[robot_ID]
            pass
        
        if robot == None:
            print("No robot to show axis on, quitting axis display")
            pass
        #################
        
        types = {0:"REV",1:"PRIS",2:"SPHER",3:"PLAN",4:"FIXED"}
        for i in range(self.robot_joint_count):
            info = self.Client.getJointInfo(robot,i)
            if type == None:
                print(f"<{info[0]}> [{types[info[2]]}] {info[1]}]: pos={info[3]}, vel={info[4]}")
            elif types[info[2]] == type:
                print(f"<{info[0]}> [{types[info[2]]}] {info[1]}]: pos={info[3]}, vel={info[4]}")
        
        pass

    #will show the link information of the robot in the following format
    #<link index> pos=[x,y,z]
    #additionally allows for type filetering 
    def print_link_info(self, robot_ID = None):
        
        ### get robot ###
        if (robot_ID != None and self.robot_list != None):
            robot = self.robot_list[robot_ID]
            pass
        
        if robot == None:
            print("No robot to show axis on, quitting axis display")
            pass
        #################
        
        #get link count (joint count + 1)
        link_count = self.robot_joint_count + 1
        
        for i in range(link_count):
            info = self.Client.getLinkState(robot,i)
            print(f"<{i}> pos=[{round(info[0][0],2)},{round(info[0][1],2)},{round(info[0][2],2)}]")
        
        pass  

    #################### DEBUG AND MISCELANEOUS ####################

    #creates a new robot in the simulation
    #robot_ID needs to be supplied or else it will be set to a random value
    #robot list is a dictionary with the Robots_ID as keys and the robot object as values
    def add_robot(self, robot_ID=None):
        
        #handle the ID of the robot
        if robot_ID == None:
            robot_ID = "RND_" + str(rnd.uniform(0,1000))
            
        #get a starting position for the robot
        #z spacing of 1.1 matches roughly the height of the robot
        starting_pos = [0,0,1.1]
        starting_orientation = self.Client.getQuaternionFromEuler([0,0,0])
        
        #create the robot
        robot = self.Client.loadURDF(self.robot_type, starting_pos, starting_orientation, useFixedBase=False)
        
        #update joint count of robot if needed
        if self.robot_joint_count == 0:
            self.robot_joint_count = self.Client.getNumJoints(robot)
        
        #relax the muscles/define standard friction
        #must not be 0
        jointFrictionForce = self.joint_friction
        for joint in range(self.robot_joint_count):
            self.Client.setJointMotorControl2(robot, joint, self.Client.POSITION_CONTROL, force=jointFrictionForce)
            
        #reference joints should be set at 0
        #this makes it so they dont oppose movement as they are simply plane constraints
        self.Client.setJointMotorControl2(robot, 0,  self.Client.POSITION_CONTROL, force=0) #origin to z
        self.Client.setJointMotorControl2(robot, 1,  self.Client.POSITION_CONTROL, force=0) #z to x
        self.Client.setJointMotorControl2(robot, 2,  self.Client.POSITION_CONTROL, force=0) #x to y
            
        #append to dictionary
        self.robot_list.update({robot_ID: robot})
        
        pass

    pass

#Will run the simulation single process or multi process
#decides so based on the max_processes variable
def simulate(pop,
            robot_type = "biped_freeman.urdf",
            joint_friction = 10,
            torque_multiplier = 100,
            GUI = False,
            max_single_process_brains = 7,
            max_processes = 4,
            time_controlled=False, 
            time_limit = 5,
            step_limit = 1000, 
            max_TPS = None,
            debug = False,
            show_timer = False, 
            show_axis = False, 
            show_IDs = False,
            show_coords = False,
            cam_focus_ID = None):
    
    positions = {}
    sim_data = []
    
    brains_list = pop.get_brains()  
    
    #if the number of brains is less than the max_processes, then run a single process
    if len(brains_list) < max_single_process_brains:
        #create the necessary keys for the robot list
        keys_list = pbsf.create_robot_list_keys(pop)
        
        #run sim and get results
        sim_results, sim_data = single_process_simulation(brains_list,keys_list,
             robot_type=robot_type,
             joint_friction=joint_friction,
             torque_multiplier=torque_multiplier,
             GUI = GUI,
             time_controlled=time_controlled, 
             time_limit = time_limit,
             step_limit = step_limit, 
             max_TPS = max_TPS,
             debug = debug,
             show_timer = show_timer, 
             show_axis = show_axis, 
             show_IDs = show_IDs,
             show_coords = show_coords,
             cam_focus_ID = cam_focus_ID)
    
    #if the number of brains is more than the max_processes, then run a multi process
    else: 
        sim_results, sim_data = multiprocess_simulations(pop,
                                robot_type=robot_type,
                                joint_friction=joint_friction,
                                torque_multiplier=torque_multiplier,
                                GUI = GUI,
                                time_controlled=time_controlled, 
                                time_limit = time_limit,
                                step_limit = step_limit, 
                                max_processes = max_processes,
                                max_TPS = max_TPS,
                                debug = debug,
                                show_timer = show_timer, 
                                show_axis = show_axis, 
                                show_IDs = show_IDs,
                                show_coords = show_coords,
                                cam_focus_ID = cam_focus_ID)
        
        
        
    return sim_results, sim_data

#will create a simulation client and run it with the specified parameters
#MAIN FUNCTION TO RUN THE SIMULATION
#[!] the multiprocess data and id variables are relevant when using multiprocessing only
def single_process_simulation(brains_list,keys_list,
             multiprocess_data = None,
             multiprocess_id = None,
             robot_type = "biped_freeman.urdf",
             joint_friction = 10,
             torque_multiplier = 100,
             GUI = False,
             time_controlled=False, 
             time_limit = 5,
             step_limit = 1000, 
             max_TPS = None,
             debug = False,
             show_timer = False, 
             show_axis = False, 
             show_IDs = False,
             show_coords = False,
             cam_focus_ID = None):
    
    #create sim client
    #includes creation of environment and gravity setting
    sim = sim_client(GUI=GUI, robot_type=robot_type)
    
    #update joint friction and torque multiplier
    sim.joint_friction = joint_friction
    sim.joint_torque_multiplier = torque_multiplier
    
    #setup sim client
    #includes creation of robots matching the given brain and keys list
    sim.match_brains_to_robots(brains_list, keys_list)
    
    #run the simulation to get results
    sim.sim_loop(brains_list,
                time_controlled, 
                time_limit,
                step_limit, 
                max_TPS,
                debug,
                show_timer, 
                show_axis, 
                show_IDs,
                show_coords,
                cam_focus_ID)
    
    #update if multithread
    if multiprocess_id != None:
        multiprocess_data[multiprocess_id] = [sim.robot_sim_results,sim.sim_data]
    
    #return sim data
    return sim.robot_sim_results , sim.sim_data

#creates the simulations and runs them in parallel
def multiprocess_simulations(pop,
                            robot_type = "biped_freeman.urdf",
                            joint_friction = 10,
                            torque_multiplier = 100,
                            GUI = False,
                            time_controlled=False, 
                            time_limit = 5,
                            step_limit = 1000, 
                            max_processes = 4,
                            max_TPS = None,
                            debug = False,
                            show_timer = False, 
                            show_axis = False, 
                            show_IDs = False,
                            show_coords = False,
                            cam_focus_ID = None):  
    
    #storage
    sim_results = {}
    sim_data = []
    
    #max number of processs
    processs_list = []
    
    #get list of brains
    brains_list = pop.get_brains()
    brain_max_index = len(brains_list)-1
    
    #keys list to work with dictionary
    keys_list = pbsf.create_robot_list_keys(pop)
    
    #catch case for less brains than processs
    if (brain_max_index + 1)  < max_processes:
        max_processes = brain_max_index
    
    cursor = 0
    client_index = 0
    
    #depending on the brain count, the last process might have to simulate more brains than the others
    brains_per_process = len(brains_list)//max_processes
    extra_brains_last_process = len(brains_list)%max_processes

    #GO THROUGH ALL processS
    manager = mp.Manager()
    multiprocess_data = manager.dict()
    
    for process_index in range(max_processes):
        
        #SETUP SIMULATION TASK FOR EACH process 
        
        #in order to simulate all the brains and because of rounding the steps, the last process will simulate
        #the last few brains until the end of the list
        #process 1 , 2 , 3 ,....
        if process_index != max_processes - 1:
            #find keys to extract from dictionary
            keys_to_use = keys_list[ cursor : cursor + brains_per_process ]
            #assign robot list to sim client
            brains_to_use = brains_list[ cursor : cursor + brains_per_process ]
        
        #process -1 (last process)
        else:       
            #if the last process only has one element, these 2 will be empty and that needs to be corrected
            #IM not happy with this fix but it works
            if len(keys_list[cursor : cursor + brains_per_process+extra_brains_last_process])==0:
                #get last brain
                #find keys to extract from dictionary
                keys_to_use = [keys_list[ cursor ]]
                #assign robot list to sim client
                brains_to_use = [brains_list[ cursor ]]
            else:
                #get every brain from the cursor to the end
                #find keys to extract from dictionary
                keys_to_use = keys_list[ cursor : cursor + brains_per_process+extra_brains_last_process ]
                #assign robot list to sim client
                brains_to_use = brains_list[ cursor : cursor + brains_per_process+extra_brains_last_process ]

        #assign process task
        new_process_task = mp.Process(target = single_process_simulation, args = (brains_to_use, keys_to_use,
                                                                multiprocess_data,process_index,
                                                                robot_type,
                                                                joint_friction,
                                                                torque_multiplier,
                                                                GUI,
                                                                time_controlled, 
                                                                time_limit,
                                                                step_limit, 
                                                                max_TPS,
                                                                debug,
                                                                show_timer, 
                                                                show_axis, 
                                                                show_IDs,
                                                                show_coords,
                                                                cam_focus_ID))
        
        #small trick, if GUI is used, only the first process will have GUI (only one process can have GUI)
        GUI = False
        
        #append process to processs list and update cursor
        processs_list.append(new_process_task)                 #append process to list to then wait for the results
        cursor += brains_per_process                           #update cursor with the last brain index
        client_index += 1                                      #update client index 
            
    #start all processs tasks
    for process in processs_list:
        process.start()               

    #wait for all processs to finish
    #And get results appended to the positions and sim_data lists
    for process_id in processs_list:
        process_id.join()

    #get data
    sim_results_dict_list = multiprocess_data.values()
    for i in range(len(sim_results_dict_list)):
        sim_results.update(sim_results_dict_list[i][0])
    
    return sim_results, sim_data
