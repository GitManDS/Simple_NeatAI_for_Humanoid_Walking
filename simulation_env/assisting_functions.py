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
    
    #torso to R leg
    p.setJointMotorControl2(entity, 3, p.POSITION_CONTROL, targetPosition= pos_pos, force=force_val)
    #torso to L leg
    p.setJointMotorControl2(entity, 6, p.POSITION_CONTROL, targetPosition= -pos_pos, force=force_val)
    
    #right knee
    p.setJointMotorControl2(entity, 4, p.POSITION_CONTROL, targetPosition= pos_pos, force=force_val)
    #Left Knee
    p.setJointMotorControl2(entity, 7, p.POSITION_CONTROL, targetPosition= -pos_pos, force=force_val)
    
    #right ankle
    p.setJointMotorControl2(entity, 5, p.POSITION_CONTROL, targetPosition= pos_pos, force=force_val)   
    #Left ankle
    p.setJointMotorControl2(entity, 8, p.POSITION_CONTROL, targetPosition= -pos_pos, force=force_val)
    
    pass

