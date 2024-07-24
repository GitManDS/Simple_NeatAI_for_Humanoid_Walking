import classes as ccls
import support_functions as sf
import matplotlib.pyplot as plt
import temporary_testing_funcs as ttf
import visualizer as vz
import random as rnd


#create brain
#ttf.record_clear()
#ttf.live_stress_test_NEAT_AI_class_and_visualizer(UPS=1000)

#ttf.live_stress_test_NEAT_AI_population(UPS=1000)

world = ccls.population(3,3,Starting_brain_count=5)
world.print()

for i in range(50):
    #mutate
    world.mutate_all()
    
    print("AHHHHHHHHHHHHHHHHHHH")
    world.print()
    ##Random results
    world.update_species_brain_count()
    rnd.seed = rnd.uniform(0,1000)
    results = [rnd.uniform(0,1000) for i in range(world.brain_count)]
    results[0]+=results[0]*5
    world.update_results(results)
    
    world.update_planned_offspring_count()
    print([specie.max_offspring for specie in world.species])
    print(world.get_max_speciation_difference_per_species())
    #crossover
    world.create_new_generation()
    world.print()

world.print()

