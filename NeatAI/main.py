import classes as ccls
import support_functions as sf
import matplotlib.pyplot as plt
import temporary_testing_funcs as ttf
import visualizer as vz
import time


#create brain
#ttf.record_clear()
#ttf.live_stress_test_NEAT_AI_class_and_visualizer(UPS=1000)

world = ccls.population(3,3,2)
world.print()

for i in range(20):
    world.mutate_all()

world.print()
    
world.species[0].brains[0].save_mental_connections("brain1.txt",overwrite=True)
world.species[0].brains[1].save_mental_connections("brain2.txt",overwrite=True)
brain3 = sf.combine_fenotypes(world.species[0].brains[0], world.species[0].brains[1])
print(sf.compare_fenotypes(world.species[0].brains[0],world.species[0].brains[1]))
vz.draw_fenotype_list([world.species[0].brains[0],world.species[0].brains[1],brain3])


brain3.observe_mental_map() 
print(sf.compute_output(brain3,[1,1,1]))

