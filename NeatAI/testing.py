import matplotlib.pyplot as plt
import random as rnd
from NeatAI import NeatAI_support_functions as NAIsf
from NeatAI import classes as ccls
from NeatAI import temporary_testing_funcs as ttf
from NeatAI import visualizer as vz


#create brain
#ttf.record_clear()
#ttf.live_stress_test_NEAT_AI_class_and_visualizer(UPS=1000)

#ttf.live_stress_test_NEAT_AI_population(UPS=1000)

world = ccls.population(3,3,Starting_brain_count=5)
world.print()

for i in range(500):
    #mutate
    world.mutate_all()

    ##Random results
    world.update_species_brain_count()
    rnd.seed = rnd.uniform(0,1000)
    results = [rnd.uniform(0,1000) for i in range(world.brain_count)] 
    world.update_results(results)
    print("-"*100)
    world.print(ordered_by_score=True)
    
    if i % 100 == 0 and i!=0:
        brains = world.get_all_brains()
        for i in range(3):
            brains[i].observe_mental_map()
    
    world.update_planned_offspring_count()
    print([specie.max_offspring for specie in world.species])
    print(world.get_max_speciation_difference_per_species())
    #crossover
    world.create_new_generation(prioritize_smaller_brains=True)
    world.print()

world.print()

