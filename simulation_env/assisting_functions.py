import pybullet as pb 
import numpy as np

#will focus the camera on a entity or on an entity ID
#if the entity ID is supplied, then the entity list must also be supplied
def focus_camera(entity = None, entity_list = None, entity_ID = None):
    
    if (entity_ID != None and entity_list != None):
        entity = entity_list[entity_ID]
        pass
    
    if entity != None:
        Pos=pb.getLinkState(entity,4)[0]
        pb.resetDebugVisualizerCamera(3, 
                                    -45, 
                                    -45, 
                                    Pos)
    else:
        print("No entity to focus on, quitting focusing")
        pass

    pass
  
def biped_random_torque_twitches(entity,step):  
     
    #define position
    pos_pos = np.sin(step/10)*0.5
    force_val = 250
    
    #debug index offset
    i=-1
    
    #torso to R leg
    pb.setJointMotorControl2(entity, 4+i, pb.TORQUE_CONTROL, targetPosition= pos_pos, force=force_val)
    #torso to L leg
    pb.setJointMotorControl2(entity, 7+i, pb.TORQUE_CONTROL, targetPosition= -pos_pos, force=force_val)
    
    #right knee
    pb.setJointMotorControl2(entity, 5+i, pb.TORQUE_CONTROL, targetPosition= pos_pos, force=force_val)
    #Left Knee
    pb.setJointMotorControl2(entity, 8+i, pb.TORQUE_CONTROL, targetPosition= -pos_pos, force=force_val)
    
    #right ankle
    #pb.setJointMotorControl2(entity, 6+i, pb.TORQUE_CONTROL, targetPosition= pos_pos, force=force_val)   
    #Left ankle
    #pb.setJointMotorControl2(entity, 9+i, pb.TORQUE_CONTROL, targetPosition= -pos_pos, force=force_val)
      
def biped_testing_walk(entity,step):
    
    #define position
    pos_pos = np.sin(step/10)*0.5
    force_val = 100
    
    #debug index offset
    i=0
    
    #torso to R leg
    pb.setJointMotorControl2(entity, 6, pb.POSITION_CONTROL, targetPosition= pos_pos, force=force_val)
    #torso to L leg
    pb.setJointMotorControl2(entity, 10, pb.POSITION_CONTROL, targetPosition= -pos_pos, force=force_val)
    
    #right knee
    pb.setJointMotorControl2(entity, 7, pb.POSITION_CONTROL, targetPosition= pos_pos, force=force_val)
    #Left Knee
    pb.setJointMotorControl2(entity, 11, pb.POSITION_CONTROL, targetPosition= -pos_pos, force=force_val)
    
    #right ankle
    pb.setJointMotorControl2(entity, 8, pb.POSITION_CONTROL, targetPosition= pos_pos, force=force_val)   
    #Left ankle
    pb.setJointMotorControl2(entity, 12, pb.POSITION_CONTROL, targetPosition= -pos_pos, force=force_val)
    
    pass

def identify_robot(entity,entity_name):
    #get head position
    head_pos = pb.getLinkState(entity,3)[0]
    
    #lifetime
    Ltime = 1/24        #movie 1/fps
    
    #place debug text
    pb.addUserDebugText(entity_name,[head_pos[0] - 0.25 , head_pos[1], head_pos[2] + 0.5 ],textColorRGB=[0,0,0], textSize=1, lifeTime=Ltime)
    
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
    pos_y = pb.getLinkState(entity,2)[0]
    pos_x = pb.getLinkState(entity,1)[0]
    pos_z = pb.getLinkState(entity,0)[0]
    
    pos_y2 = [pos_y[0],leng+pos_y[1],pos_y[2]]
    pos_x2 = [leng+pos_x[0],pos_x[1],pos_x[2]]
    pos_z2 = [pos_z[0],pos_z[1],leng+pos_z[2]]
    
    #lifetime
    Ltime = 1/24        #movie 1/fps
    
    #axis
    pb.addUserDebugLine(pos_z, pos_z2 , lineColorRGB=orange, lineWidth=0.02, lifeTime=Ltime)
    pb.addUserDebugLine(pos_x,pos_x2, lineColorRGB=blue, lineWidth=0.02, lifeTime=Ltime)
    pb.addUserDebugLine(pos_y,pos_y2, lineColorRGB=black, lineWidth=0.02, lifeTime=Ltime)
    
    #axis text
    pb.addUserDebugText("Z",pos_z2,textColorRGB=black, textSize=1, lifeTime=Ltime)
    pb.addUserDebugText("X",pos_x2,textColorRGB=black, textSize=1, lifeTime=Ltime)
    pb.addUserDebugText("Y",pos_y2,textColorRGB=black, textSize=1, lifeTime=Ltime)
    
    pass