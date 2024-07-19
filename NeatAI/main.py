import classes as ccls
import support_functions as sf
import matplotlib.pyplot as plt
import temporary_testing_funcs as ttf
import visualizer as vz
import time


#create brain
#ttf.record_clear()
#ttf.live_stress_test_NEAT_AI_class_and_visualizer(UPS=1000)

world = ccls.population()
brain1 = ccls.brain_fenotype(3,3)
brain2 = ccls.brain_fenotype(3,3)
world.species[0].add_brain(brain1)
world.species[0].add_brain(brain2)

for i in range(20):
    brain1.mutation_random()
    world.update_innovation(brain1.inov_counter)
    brain2.mutation_random()   
    world.update_innovation(brain2.inov_counter) 

brain1.save_mental_connections("brain1.txt",overwrite=True)
brain2.save_mental_connections("brain2.txt",overwrite=True)
vz.draw_fenotype_list([brain1,brain2])
#plt.show()


brain1.save_mental_connections("brain1.txt")
brain1.save_mental_picture("brain1.png")
brain2.load_mental_connections("brain1.txt")
brain2.print()
brain2.observe() 
print(sf.compute_output(brain2,[1,1,1]))

