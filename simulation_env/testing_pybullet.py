import pybullet as pb
import time
import pybullet_data
import assisting_functions as af

#Settings
TPS = 240            #updates per second
sim_time = 5        #seconds
sim_type = 1        #0 for real-time limited, 1 for step-by-step limited
assets_folder = "C:/Users/diogo serra/Desktop/trabalhos, documentose afixos de programas/TUDelft-MEaer/een/even semester/AI/Bipedal agent project/simulation_env/assets"

def sim_init():
    if sim_type == 0:
        pb.connect(pb.GUI)
    else:
        pb.connect(pb.GUI)
    pb.setGravity(0,0,-9.81)
    
    #advanced settings
    #pb.setAdditionalSearchPath(pybullet_data.getDataPath())
    pb.setAdditionalSearchPath(assets_folder)
    print(pybullet_data.getDataPath())
    
    pass

def sim_loop():  
    
    #run with GUI open and time limited (will run forever until GUI is closed)
    if sim_type == 0:
        pb.setRealTimeSimulation(1)
        elapsed_time = 0
        while True:
            #af.focus_camera(NeatROBOT)
            
            #af.biped_random_torque_twitches(NeatROBOT,elapsed_time)
            af.biped_testing_walk(NeatROBOT,elapsed_time)
            
            #af.show_axis(NeatROBOT)
            
            #af.identify_robot(NeatROBOT,"NeatROBOT")
            
            elapsed_time += 1/TPS
            pass
        
    #run without GUI and step-by-step limited (will run for simulation time and is limited by processing power)
    else:
        pb.stepSimulation()
        for step in range(int(sim_time*TPS)):  #loop for all updates
            
            print(f"STEP {step}" + "-"*20)
            af.biped_testing_walk(NeatROBOT,step)
            
            main_body_position, main_body_rotation = pb.getLinkState(NeatROBOT,5)[0:2]

            #object joints
            #Get the position index of each index from -a to a
            #firts 5 joints are the reference joints
            joint_pos_index = []
            for i in range(5,pb.getNumJoints(NeatROBOT)):
                joint_pos_index.append(round(pb.getJointState(NeatROBOT,i)[0],2))
                pass
                
            print(main_body_position, main_body_rotation)
            print(joint_pos_index)
            
            #end of loop
            time.sleep(1/TPS)              #seconds per tick
            pb.stepSimulation()
            if step % 10 == 0:
                print("stop")
            #end of loop
    
    pb.disconnect()
    pass

#MAIN

#initialize simulation
sim_init()

#create objects
planeId = pb.loadURDF("plane.urdf", useFixedBase=True) 

StartPos = [0,0,1.1] 
StartOrientation = pb.getQuaternionFromEuler([0,0,0]) 
NeatROBOT = pb.loadURDF("biped_norotation.urdf", StartPos, StartOrientation) 

#relax the muscles/define standard friction
jointFrictionForce = 10
for joint in range(pb.getNumJoints(NeatROBOT)):
  pb.setJointMotorControl2(NeatROBOT, joint, pb.POSITION_CONTROL, force=jointFrictionForce)

#reference joints should be set at 0
pb.setJointMotorControl2(NeatROBOT, 0,  pb.POSITION_CONTROL, force=0) #origin to z
pb.setJointMotorControl2(NeatROBOT, 1,  pb.POSITION_CONTROL, force=0) #z to x
pb.setJointMotorControl2(NeatROBOT, 2,  pb.POSITION_CONTROL, force=0) #x to y

#object joints
for i in range(pb.getNumJoints(NeatROBOT)):
    print(pb.getJointInfo(NeatROBOT,i)[0:4])
    pass

#object links
for i in range(pb.getNumJoints(NeatROBOT)):
    print(pb.getLinkState(NeatROBOT,i)[0:3])
    pass


#run simulation
sim_loop()







