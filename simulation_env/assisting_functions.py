import pybullet as p 
import numpy as np


def focus_camera(entity):
    Pos,Rot=p.getBasePositionAndOrientation(entity)
    p.resetDebugVisualizerCamera(3, 
                                 -45, 
                                 -45, 
                                 Pos)

    pass
    
def biped_testing_walk(entity,step):
    
    #define position
    pos_pos = np.sin(step/10)
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

