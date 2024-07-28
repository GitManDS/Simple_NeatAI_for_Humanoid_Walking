import pybullet as pb 
import numpy as np
import time

#this applies to most of the visual functions
#adjust as needed (increase for longer display time and less flickering)
debug_text_lifetime = 1

################### VISUAL FUNCTIONS ###################
#will focus the camera on a robot or on an robot ID
#if the robot ID is supplied, then the robot list must also be supplied
def focus_camera(robot = None, robot_list = None, robot_ID = None):
    
    if (robot_ID != None and robot_list != None):
        robot = robot_list[robot_ID]
        pass
    
    if robot != None:
        Pos=pb.getLinkState(robot,4)[0]
        pb.resetDebugVisualizerCamera(3, 
                                    -45, 
                                    -45, 
                                    Pos)
    else:
        print("No robot to focus on, quitting focusing")
        pass

    pass
  
#this will place a text above the robot with the robot ID for 1 step
#this will only work if the robot ID is supplied since its needed to identify the robot
def identify_robot(robot_ID, robot_list):
    #get head position
    robot = robot_list[robot_ID]
    head_pos = pb.getLinkState(robot,3)[0]
    
    #lifetime
    Ltime = debug_text_lifetime        #movie 1/fps
    
    #place debug text
    pb.addUserDebugText(robot_ID,[head_pos[0] - 0.25 , head_pos[1], head_pos[2] + 0.5 ],textColorRGB=[0,0,0], textSize=1, lifeTime=Ltime)
    
    pass

#when given a start date (time lib), this function will display a clock on the topright corner
#with the elapsed time, updating every function loop or step
def show_timer(clock_start, previous_timer_id = None):
    #get elapsed time
    elapsed_time = time.time() - clock_start
    
    #lifetime
    Ltime = debug_text_lifetime        #movie 1/fps
    
    #place debug text
    if previous_timer_id != None:
        pb.removeUserDebugItem(previous_timer_id)
        pass
    timer_ID = pb.addUserDebugText("Time: " + str(round(elapsed_time,2)),[0,0,0],textColorRGB=[0,0,0], textSize=1, lifeTime=Ltime)
    
    return timer_ID

#shows step count above timer
def show_step_count(step, previous_step_id = None):
    #lifetime
    Ltime = debug_text_lifetime        #movie 1/fps
    
    #place debug text
    if previous_step_id != None:
        pb.removeUserDebugItem(previous_step_id)
        pass
    timer_ID = pb.addUserDebugText("Step: " + str(step),[0,0,0.2],textColorRGB=[0,0,0], textSize=1, lifeTime=Ltime)
    
    return timer_ID

#this will show the axis of the robot in the simulation for 1 step
#if the robot ID is supplied, then the robot list must also be supplied
def show_axis(robot = None, robot_list = None, robot_ID = None):
    
    ### get robot ###
    if (robot_ID != None and robot_list != None):
        robot = robot_list[robot_ID]
        pass
    
    if robot == None:
        print("No robot to show axis on, quitting axis display")
        pass
    #################
    
    
    #colors
    orange = [1,0.5,0]
    blue = [0,0,1]
    black = [0,0,0]
    
    #line length
    leng = 0.6
    
    #get current axis position
    #z=1, x=2 , y=3
    pos_y = pb.getLinkState(robot,2)[0]
    pos_x = pb.getLinkState(robot,1)[0]
    pos_z = pb.getLinkState(robot,0)[0]
    
    pos_y2 = [pos_y[0],leng+pos_y[1],pos_y[2]]
    pos_x2 = [leng+pos_x[0],pos_x[1],pos_x[2]]
    pos_z2 = [pos_z[0],pos_z[1],leng+pos_z[2]]
    
    #lifetime
    Ltime = debug_text_lifetime        #movie 1/fps
    
    #axis
    pb.addUserDebugLine(pos_z, pos_z2 , lineColorRGB=orange, lineWidth=0.02, lifeTime=Ltime)
    pb.addUserDebugLine(pos_x,pos_x2, lineColorRGB=blue, lineWidth=0.02, lifeTime=Ltime)
    pb.addUserDebugLine(pos_y,pos_y2, lineColorRGB=black, lineWidth=0.02, lifeTime=Ltime)
    
    #axis text
    pb.addUserDebugText("Z",pos_z2,textColorRGB=black, textSize=1, lifeTime=Ltime)
    pb.addUserDebugText("X",pos_x2,textColorRGB=black, textSize=1, lifeTime=Ltime)
    pb.addUserDebugText("Y",pos_y2,textColorRGB=black, textSize=1, lifeTime=Ltime)
    
    pass

#will display atop the name of the robot the coordinates of the robot
#by default, it will display the coordinates of the body (torso)
def show_coords(robot = None, robot_list = None, robot_ID = None):
    ### get robot ###
    if (robot_ID != None and robot_list != None):
        robot = robot_list[robot_ID]
        pass
    
    if robot == None:
        print("No robot to show axis on, quitting axis display")
        pass
    #################
    
    #get the coordinates
    #torso rot is not used
    torso_pos, torso_rot = pb.getLinkState(robot,4)[0:2]
    
    #get head position to place the text
    head_pos = pb.getLinkState(robot,3)[0]
    
    #lifetime
    Ltime = debug_text_lifetime        #movie 1/fps
    
    #place debug text
    #-0.5 to help it be more centered
    #+1 to bring it up
    pb.addUserDebugText(f"x:{round(torso_pos[0],2)} y:{round(torso_pos[1],2)} z:{round(torso_pos[2],2)}" ,
                        [head_pos[0] - 0.5 , head_pos[1] , head_pos[2] + 1 ],
                        textColorRGB=[0,0,0], 
                        textSize=1, 
                        lifeTime=Ltime)
    
    pass

################### PHYSICS AND LOGISTICS FUNCTIONS ###################

#returns the position of the body in the world, aswell as 
#[!]can be expanded to give contact points and forces
def get_robot_and_joints_position_rotation(robot = None, robot_list = None, robot_ID = None):

    ### get robot ###
    if (robot_ID != None and robot_list != None):
        robot = robot_list[robot_ID]
        pass
    
    if robot == None:
        print("No robot to show axis on, quitting axis display")
        pass
    #################

    #head joint / body position
    #dont need the position of all the links, just the position of the base and the position *index* of the joints
    #4 is the index of the torso link
    main_body_position, main_body_rotation = pb.getLinkState(robot,4)[0:2]

    #object joints
    #Get the position index of each index from -a to a
    #firts 5 joints are the reference joints
    joint_pos_index = []
    for i in range(5,pb.getNumJoints(robot)):
        joint_pos_index.append(pb.getJointState(robot,i)[0])
        pass


    return main_body_position, main_body_rotation, joint_pos_index

#will apply a torque to the the joints of the robot
#accepts a list of torques to apply to the robot in the following order of joints
#order: r_rot-r_upperleg-r_lowerleg-r_ankle-l_rot-l_upperleg-l_lowerleg-l_ankle
def apply_torque_to_robot(torque, robot = None, robot_list = None, robot_ID = None):
    
    ### get robot ###
    if (robot_ID != None and robot_list != None):
        robot = robot_list[robot_ID]
        pass
    
    if robot == None:
        print("No robot to show axis on, quitting axis display")
        pass
    #################
    
    first_joint_index = 5
    last_joint_index = 12
    index = 0
    for joint_index in range(first_joint_index,last_joint_index+1):
        pb.setJointMotorControl2(robot, joint_index, pb.TORQUE_CONTROL, force=torque[index])
        index += 1
    
    pass

################### DEBUG FUNCTIONS ###################

#will show the joint information of the robot in the following format
#<joint index> [joint type] joint name: pos=position, vel=velocity
#additionally allows for type filetering 
def print_joint_info(robot = None, robot_list = None, robot_ID = None, type = None):
    
    ### get robot ###
    if (robot_ID != None and robot_list != None):
        robot = robot_list[robot_ID]
        pass
    
    if robot == None:
        print("No robot to show axis on, quitting axis display")
        pass
    #################
    
    types = {0:"REV",1:"PRIS",2:"SPHER",3:"PLAN",4:"FIXED"}
    for i in range(pb.getNumJoints(robot)):
        info = pb.getJointInfo(robot,i)
        if type == None:
            print(f"<{info[0]}> [{types[info[2]]}] {info[1]}]: pos={info[3]}, vel={info[4]}")
        elif types[info[2]] == type:
            print(f"<{info[0]}> [{types[info[2]]}] {info[1]}]: pos={info[3]}, vel={info[4]}")
    
    pass

#will show the link information of the robot in the following format
#<link index> pos=[x,y,z]
#additionally allows for type filetering 
def print_link_info(robot = None, robot_list = None, robot_ID = None, type = None):
    
    ### get robot ###
    if (robot_ID != None and robot_list != None):
        robot = robot_list[robot_ID]
        pass
    
    if robot == None:
        print("No robot to show axis on, quitting axis display")
        pass
    #################
    
    #get link count (joint count + 1)
    link_count = pb.getNumJoints(robot) + 1
    
    for i in range(link_count):
        info = pb.getLinkState(robot,i)
        print(f"<{i}> pos=[{round(info[0][0],2)},{round(info[0][1],2)},{round(info[0][2],2)}]")
    
    pass