import classes
import support_functions as sf
import random as rnd
import matplotlib.pyplot as plt
import visualizer as vz


#function to test the visualizer and the neat class
#will create a brain and apply random mutations to it until it breaks (if it breaks)
#modifies the brain according to UPS (updates per second)
def live_stress_test_NEAT_AI_class_and_visualizer(UPS):
    
    brian_the_dog = classes.brain_fenotype(rnd.randint(1,20),rnd.randint(1,20))
    plt.figure()
    brian_the_dog.observe()
    plt.pause(1/UPS)        
    plt.clf()
    while True:
        brian_the_dog=sf.random_mutation(brian_the_dog)
        
        brian_the_dog.print()
        brian_the_dog.observe()

        plt.pause(1/UPS)
        plt.clf()

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