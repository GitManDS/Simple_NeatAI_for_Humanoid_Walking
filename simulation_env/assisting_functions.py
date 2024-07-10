import pybullet as p 
import numpy as np


def focus_camera(entity):
    Pos=p.getLinkState(entity,2)[0]
    p.resetDebugVisualizerCamera(3, 
                                 -45, 
                                 -45, 
                                 Pos)

    pass
  
def biped_random_torque_twitches(entity,step):  
     
    #define position
    pos_pos = np.sin(step/10)*0.5
    force_val = 250
    
    #debug index offset
    i=-1
    
    #torso to R leg
    p.setJointMotorControl2(entity, 4+i, p.TORQUE_CONTROL, targetPosition= pos_pos, force=force_val)
    #torso to L leg
    p.setJointMotorControl2(entity, 7+i, p.TORQUE_CONTROL, targetPosition= -pos_pos, force=force_val)
    
    #right knee
    p.setJointMotorControl2(entity, 5+i, p.TORQUE_CONTROL, targetPosition= pos_pos, force=force_val)
    #Left Knee
    p.setJointMotorControl2(entity, 8+i, p.TORQUE_CONTROL, targetPosition= -pos_pos, force=force_val)
    
    #right ankle
    #p.setJointMotorControl2(entity, 6+i, p.TORQUE_CONTROL, targetPosition= pos_pos, force=force_val)   
    #Left ankle
    #p.setJointMotorControl2(entity, 9+i, p.TORQUE_CONTROL, targetPosition= -pos_pos, force=force_val)
      
def biped_testing_walk(entity,step):
    
    #define position
    pos_pos = np.sin(step/10)*0.5
    force_val = 1000
    
    #debug index offset
    i=-1
    
    #torso to R leg
    p.setJointMotorControl2(entity, 4+i, p.POSITION_CONTROL, targetPosition= pos_pos, force=force_val)
    #torso to L leg
    p.setJointMotorControl2(entity, 7+i, p.POSITION_CONTROL, targetPosition= -pos_pos, force=force_val)
    
    #right knee
    p.setJointMotorControl2(entity, 5+i, p.POSITION_CONTROL, targetPosition= pos_pos, force=force_val)
    #Left Knee
    p.setJointMotorControl2(entity, 8+i, p.POSITION_CONTROL, targetPosition= -pos_pos, force=force_val)
    
    #right ankle
    p.setJointMotorControl2(entity, 6+i, p.POSITION_CONTROL, targetPosition= pos_pos, force=force_val)   
    #Left ankle
    p.setJointMotorControl2(entity, 9+i, p.POSITION_CONTROL, targetPosition= -pos_pos, force=force_val)
    
    pass

def identify_robot(entity,entity_name):
    #get head position
    #head index = 4
    head_pos = p.getLinkState(entity,3)[0]
    
    #lifetime
    Ltime = 1/24        #movie 1/fps
    
    #place debug text
    p.addUserDebugText(entity_name,[head_pos[0] , head_pos[1] , head_pos[2]+ 0.1],textColorRGB=[0,0,0], textSize=1, lifeTime=Ltime)
    
    pass

def show_axis(entity):
    #colors
    orange = [1,0.5,0]
    blue = [0,0,1]
    black = [0,0,0]
    
    #line length
    leng = 0.6
    
    #get current axis position
    #z=1, x=2 , y=3
    pos_y = p.getLinkState(entity,2)[0]
    pos_x = p.getLinkState(entity,1)[0]
    pos_z = p.getLinkState(entity,0)[0]
    
    pos_y2 = [pos_y[0],leng+pos_y[1],pos_y[2]]
    pos_x2 = [leng+pos_x[0],pos_x[1],pos_x[2]]
    pos_z2 = [pos_z[0],pos_z[1],leng+pos_z[2]]
    
    #lifetime
    Ltime = 1/24        #movie 1/fps
    
    #axis
    p.addUserDebugLine(pos_z, pos_z2 , lineColorRGB=orange, lineWidth=0.02, lifeTime=Ltime)
    p.addUserDebugLine(pos_x,pos_x2, lineColorRGB=blue, lineWidth=0.02, lifeTime=Ltime)
    p.addUserDebugLine(pos_y,pos_y2, lineColorRGB=black, lineWidth=0.02, lifeTime=Ltime)
    
    #axis text
    p.addUserDebugText("Z",pos_z2,textColorRGB=black, textSize=1, lifeTime=Ltime)
    p.addUserDebugText("X",pos_x2,textColorRGB=black, textSize=1, lifeTime=Ltime)
    p.addUserDebugText("Y",pos_y2,textColorRGB=black, textSize=1, lifeTime=Ltime)
    
    pass