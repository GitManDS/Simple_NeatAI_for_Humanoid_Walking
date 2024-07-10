import pybullet as p 
import time
import pybullet_data
import assisting_functions as af

#Settings
TPS = 240            #updates per second
sim_time = 0.1        #seconds
sim_type = 0        #0 for real-time limited, 1 for step-by-step limited
assets_folder = "C:/Users/diogo serra/Desktop/trabalhos, documentose afixos de programas/TUDelft-MEaer/een/even semester/AI/Bipedal agent project/simulation_env/assets"

def sim_init():
    if sim_type == 0:
        p.connect(p.GUI)
    else:
        p.connect(p.DIRECT)
    p.setGravity(0,0,-9.81)
    
    #advanced settings
    #p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.setAdditionalSearchPath(assets_folder)
    print(pybullet_data.getDataPath())
    
    pass

def sim_loop():  
    
    #run with GUI open and time limited (will run forever until GUI is closed)
    if sim_type == 0:
        p.setRealTimeSimulation(1)
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
        p.stepSimulation()
        for i in range(int(sim_time*TPS)):  #loop for all updates
                
            
            #end of loop
            time.sleep(1/TPS)              #seconds per tick
            p.stepSimulation()
            #end of loop
    
    p.disconnect()
    pass

#MAIN

#initialize simulation
sim_init()

#create objects
planeId = p.loadURDF("plane.urdf", useFixedBase=True) 

StartPos = [0,0,1.1] 
StartOrientation = p.getQuaternionFromEuler([0,0,0]) 
NeatROBOT = p.loadURDF("biped_norotation.urdf", StartPos, StartOrientation) 

#relax the muscles/define standard friction
jointFrictionForce = 10
for joint in range(p.getNumJoints(NeatROBOT)):
  p.setJointMotorControl2(NeatROBOT, joint, p.POSITION_CONTROL, force=jointFrictionForce)

#reference joints should be set at 0
p.setJointMotorControl2(NeatROBOT, 0,  p.POSITION_CONTROL, force=0) #origin to z
p.setJointMotorControl2(NeatROBOT, 1,  p.POSITION_CONTROL, force=0) #z to x
p.setJointMotorControl2(NeatROBOT, 2,  p.POSITION_CONTROL, force=0) #x to y

#object joints
for i in range(p.getNumJoints(NeatROBOT)):
    print(p.getJointInfo(NeatROBOT,i)[0:4])
    pass

#object links
for i in range(p.getNumJoints(NeatROBOT)):
    print(p.getLinkState(NeatROBOT,i)[0:3])
    pass


#run simulation
sim_loop()







