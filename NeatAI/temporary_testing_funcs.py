import classes
import support_functions as sf
import random as rnd
import matplotlib.pyplot as plt
import visualizer as vz
import time


#function to test the visualizer and the neat class
#will create a brain and apply random mutations to it until it breaks (if it breaks)
#modifies the brain according to UPS (updates per second)
def live_stress_test_NEAT_AI_class_and_visualizer(UPS):
    
    brian_the_dog = classes.brain_fenotype(rnd.randint(3,20),rnd.randint(3,20))
    plt.figure()
    brian_the_dog.draw()
    plt.pause(1/UPS)        
    plt.clf()
    while True:
        brian_the_dog.mutation_random()
        
        #brian_the_dog.print()
        brian_the_dog.draw()

        plt.pause(1/UPS)
        plt.clf()

def live_stress_test_NEAT_AI_population(UPS):    
    while True:
        #reset every 300 generations
        #create world with random characteristics
        world = classes.population(rnd.randint(3,10),rnd.randint(3,10),rnd.randint(3,10))
        gen=0
        while gen<300:
            clock_in = time.time()
            #view current world
            world.print()
            
            #mutate
            world.mutate_all()
            
            ##Random results
            world.update_species_brain_count()
            results = [rnd.uniform(0,1000) for i in range(world.brain_count)]
            world.update_results(results)
            
            #crossover
            world.create_new_generation()
            #clock in
            
            clock_out = clock_in
            clock_in = time.time()
            print(f"gen: {gen} time elapsed per gen: {clock_in-clock_out}s")
            gen+=1

            #wait 1/ups to observe change
            time.sleep(1/UPS)
        
        #delete everything to avoid memory leaks
        for species in world.species:
            for brain in species.brains:
                del brain
            del species
        del world
            
        
def create_random_brain():
    rnd.seed = 2002
    
    brian_the_dog = classes.brain_fenotype(rnd.randrange(1,20),rnd.randrange(1,20))
    
    #create random connections
    for i in range(rnd.randrange(1,20)):
        brian_the_dog.mutation_addconnection(rnd.randrange(0,brian_the_dog.NodeCount),rnd.randrange(0,brian_the_dog.NodeCount),rnd.uniform(0,1))
        
    #modify random connections
    for i in range(rnd.randrange(1,20)):
        brian_the_dog.update_weight(rnd.randrange(0,len(brian_the_dog.genepool)),rnd.uniform(0,1))
    
    #toggle random connections
    for i in range(rnd.randrange(1,20)):
        brian_the_dog.mutation_toggleconnection(rnd.randrange(0,len(brian_the_dog.genepool)))
    
    return brian_the_dog

def record_to_text_file(message):
    #standard path
    path = "NeatAI/record.txt"
    
    #append to file
    with open(path, "a") as file:
        file.write(message)
        file.write("\n")
    pass
    
def record_clear():
    #standard path
    path = "NeatAI/record.txt"
    
    #clear file
    with open(path, "w") as file:
        pass