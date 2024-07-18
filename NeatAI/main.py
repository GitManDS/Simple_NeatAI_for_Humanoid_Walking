import classes as ccls
import support_functions as sf
import matplotlib.pyplot as plt
import temporary_testing_funcs as ttf
import time


#testing
#fuckedbrain = ccls.brain_fenotype(2,2)
#fuckedbrain.load_mental_connections("NeatAI/brain_saves/fuckedup2.txt")
#print(sf.detect_loops(fuckedbrain,11,10,order=3))
#print("hello")

#create brain
ttf.record_clear()
ttf.live_stress_test_NEAT_AI_class_and_visualizer(UPS=1000)

world = ccls.population()
brain1 = ccls.brain_fenotype(3,3)
brain2 = ccls.brain_fenotype(3,3)
world.species[0].add_brain(brain1)
world.species[0].add_brain(brain2)

for i in range(20):
    brain1.mutation_random()
    #brain2.mutation_random()    

brain1.save_mental_connections("NeatAI/brain_saves/brain1.txt")
brain1.save_mental_picture("NeatAI/brain_saves/brain1.png")
brain2.load_mental_connections("NeatAI/brain_saves/brain1.txt")
brain2.print()
brain2.observe() 
print(sf.compute_output(brain2,[1,1,1]))
    
#brian1.save_mental_picture("NeatAI/brain1.png")
#start = time.time()
#print(sf.compute_output(brian1,[1,1,1]))
#end = time.time()
#print(f"time elapsed = {end-start}")
    
