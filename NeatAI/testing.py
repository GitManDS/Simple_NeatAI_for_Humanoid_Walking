import classes as ccls
import support_functions as sf
import matplotlib.pyplot as plt
import temporary_testing_funcs as ttf
import visualizer as vz
import time


#create brain
#ttf.record_clear()
#ttf.live_stress_test_NEAT_AI_class_and_visualizer(UPS=1000)

#ttf.live_stress_test_NEAT_AI_population(UPS=1000)

world = ccls.population(3,3,Starting_brain_count=5, MaxSpecialDist=30, max_offspring=10)
world.print()

for i in range(20):
    world.mutate_all()

world.save_population("pop1.txt",overwrite=True)
world2 = ccls.population(3,3,10)
world2.load_population("pop1.txt")
world2.save_population("pop2.txt",overwrite=True)
world.print()
    
#world.species[0].brains[0].save_mental_connections("brain1.txt",overwrite=True)
#world.species[0].brains[1].save_mental_connections("brain2.txt",overwrite=True)
brain3 = sf.combine_fenotypes(world.species[0].brains[0], world.species[1].brains[0])
print(sf.compare_fenotypes(world.species[0].brains[0],world.species[1].brains[0]))
vz.draw_fenotype_list([world.species[0].brains[0],world.species[1].brains[0],brain3])

world.species[0].brains[0].observe_mental_map()
world.species[1].brains[0].observe_mental_map()
brain3.observe_mental_map() 
print(sf.compute_output(brain3,[1,1,1]))

