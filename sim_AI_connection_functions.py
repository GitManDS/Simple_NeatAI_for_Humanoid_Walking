import pybullet as pb

#returns the position of the body in the world, aswell as 
#[!]can be expanded to give contact points and forces
def get_body_position_rotation(entity):

    #head joint / body position
    #dont need the position of all the links, just the position of the base and the position *index* of the joints
    main_body_position, main_body_rotation = pb.getLinkState(entity)[0:2]

    #object joints
    #Get the position index of each index from -a to a
    #firts 5 joints are the reference joints
    for i in range(5,pb.getNumJoints(entity)):
        joint_pos_index = pb.getJointState(entity,i)[0]
        pass


    return main_body_position, main_body_rotation, joint_pos_index

def apply_torque(entity):
    pass