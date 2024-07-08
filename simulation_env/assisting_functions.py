import pybullet as p 


def focus_camera(entity):
    Pos,Rot=p.getBasePositionAndOrientation(entity)
    p.resetDebugVisualizerCamera(3, 
                                 -45, 
                                 -45, 
                                 Pos)

    pass
    