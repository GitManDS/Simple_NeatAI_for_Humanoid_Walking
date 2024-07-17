import classes as ccls
import support_functions as sf
import matplotlib.pyplot as plt
import temporary_testing_funcs as ttf
import time



#create brain
#ttf.live_stress_test_NEAT_AI_class_and_visualizer(UPS=5)

world = ccls.population()
brian1 = ccls.brain_fenotype(3,3)
brain2 = ccls.brain_fenotype(3,3)
world.species[0].add_brain(brian1)
world.species[0].add_brain(brain2)

for i in range(20):
    brian1.mutation_random()
    #brain2.mutation_random()    
    
brian1.save_mental_picture("NeatAI/brain1.png")
start = time.time()
print(sf.compute_output(brian1,[1,1,1]))
end = time.time()
print(end-start)
    
