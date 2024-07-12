import classes as ccls
import support_functions as sf



#create brain
brian_the_dog = ccls.brain_fenotype(2,3)
brian_the_dog.mutation_addconnection(3,4,1)
brian_the_dog.observe()
