from NeatAI import NeatAI_support_functions as NAIsf
from NeatAI import visualizer as vz
from NeatAI import temporary_testing_funcs as ttf
import random as rnd
import numpy as np
import matplotlib.pyplot as plt 
import os

class population:
    def __init__(self, NOI, NOO, Starting_brain_count=2, MaxSpecialDist=2.5, max_offspring = 3, max_pop_brains = 10, max_mutations_per_gen = 3) -> None:
        self.species = []                       #list of all the brains in the species
        self.add_new_species()                  #create first species and append to species list  
        for i in range(Starting_brain_count):
            self.species[0].add_brain(brain_fenotype(NOI,NOO))
        
        self.innovation = 1                          #innovation counter  
        self.inov_database = {}                      #database of all the innovations (hidden nodes and connections only)    
        self.species_count = 1                       #number of species
        self.brain_count = Starting_brain_count      #number of brains
        self.max_offspring = max_offspring           #max number of offspring per species
        self.min_offspring = 1                       #min number of offspring per species
        self.MaxSpecialDist = MaxSpecialDist         #max distance for compatibility between species
        self.MaxBrains = max_pop_brains              #max number of brains in the population at any given time 
        self.maxmutations = max_mutations_per_gen    #max number of mutations per generation
        
        pass
    
    #should be called after every individual mutation
    def update_innovation(self,new_inov):
        self.innovation = new_inov
        for specie in self.species:
            for brain in specie.brains:
                brain.inov_counter = new_inov
        pass
    
    #################### SPECIES-BRAINS MANAGEMENT ####################
    #add new species to population
    def add_new_species(self):
        self.species.append(species())
        pass
        
    #migrate a brain from one species to another
    def migrate(self, brain, destination_species, source_species=-1):
            #remove brain from source species
            if source_species != -1:
                source_species.remove_brain(brain=brain)
            
            #if its not specified, its likelly its a new brain and its just being placed into a species
            #-THIS IS BUGGY, DONT DO THIS-nevertheless, to make it more robust, check if the brain is in any species
            #only works if population is also supplied
            #elif source_species == -1:
            #    for specie in self.species:
            #        if brain in specie.brains:
            #            specie.remove_brain(brain=brain)
        
            #add brain to destination species
            destination_species.add_brain(brain)
            pass
    
    #updates results
    #if none of the indexes is specified, its assumed that there's results for all brains in their order
    #if only specie_index is specified, its assumed that there's results for all brains in that specie
    #if booth indexes are specified, its assumed that there's only one result for one brain  
    def update_results(self, results, specie_index = -1, brain_index = -1):
        if specie_index != -1:
            #specific species was identified
            specie = self.species[specie_index]
            specie.update_results(results, brain_index)
                
        elif brain_index == -1:     #supplying a brain index but not a specie index is not allowed
            #results for all species in all brains
            cursor = 0
            for specie in self.species:
                specie.update_results(results[cursor:cursor+len(specie.brains)], brain_index)
                cursor += len(specie.brains)
        pass
     
    #will reorganize the brains in the population into species
    #according to their distance from each other
    def organize_brains_in_species(self):
    
        #get list of brains
        brains_list = self.get_brains()
        
        #clear pop species and create the first specie
        #append first brain to it
        self.species = []
        self.add_new_species()
        self.species[0].add_brain(brains_list[0])
        #remove this brain from list of brains to be organized
        brains_list.pop(0)
        
        #organize the rest of the brains
        for brain in brains_list:
            #find a species that is compatible with the brain
            #assume its compatible, nests will try and prove it isn't
            for species in self.species:
                compat = True
                for brain_to_compare in species.brains:
                    #compare current brain with every brain in the population
                    SpecialDist, debug_info = NAIsf.compare_fenotypes(brain, brain_to_compare)
                    
                    if SpecialDist > self.MaxSpecialDist:
                        #if the brain is not compatible with the species, break the loop
                        #only one incompatible brain is needed to break the loop
                        compat = False
                        break
                
                if compat:
                    #its compatible with these species
                    species.add_brain(brain)
                    break
            
            #if the brain is not compatible with any species, create a new one
            if not compat:
                self.add_new_species()
                self.species[-1].add_brain(brain)
         
        pass 
    
    #################### MUTATIONS AND GENERATIONAL TRANSMISION ####################
    #mutate a brain and see if it fits in any of the existing species
    #to fit in a species, it must match with all the brains in that species
    def mutate_all(self):
        #start mutation for all brains  in population
        #go one by one and mutate them
        for specie in self.species:
            for brain in specie.brains:
                mutations = brain.mutation_random(max_mutations = self.maxmutations)                         #update each of the brains
            
                
                #this loop only checks for innovations (toggle and update are not checked as they are not innov)
                for mutation in mutations:
                    #check if the mutation already existed
                    exists = 0 
                    for key in self.inov_database:
                        if mutations[mutation][1:] == self.inov_database[key]:
                            #if it did, update the brain's genepool inovation counter
                            brain.genepool[mutations[mutation][0]].inov = key
                            #also go back 1 in the brain inovation counter
                            brain.inov_counter -= 1
                            
                            exists = 1
                            
                    if not exists:
                        #if it didn't, add it
                        self.inov_database.update({mutation:mutations[mutation][1:]}) 
                
                if brain.inov_counter != self.innovation:       #helps save time for mutations such as toggle and update weight
                    self.update_innovation(brain.inov_counter)  #update the innovation counter
        
        #reorganize the brains in the population into species
        #[!] THIS IS A VERY IMPORTANT STEP AS DISTANCES CHANGE RADICALLY AFTER MUTATION
        self.organize_brains_in_species()
        
        pass
    
    #creates a new generation of brains
    #includes checks for speciation, species viability and offspring number
    def create_new_generation(self, prioritize_smaller_brains = False):
        
        
        #first calculate and update the number of offspring for each species
        self.update_planned_offspring_count()
        
        #also check if all species have more than 1 brain
        self.populate_species()
        
        #order the pop by score
        self = NAIsf.order_by_score(self) 
        
        #for each species, first remove all the brains that will not crossover
        #this is done by sorting the species by their results and removing the last ones (index self.max_offspring onwards)
        for specie_index, specie in enumerate(self.species):
            if len(specie.brains) > 2:
                
                #get the list of results, reorder everything such that the results
                #are in the order of the brains with the least to most connection in the genepool
                #update results list
                #WARNING: NUMBER OF OFFSPRING IS STILL DICTATED BY THE ORIGINAL ORDER OF THE BRAINS (POINTS BASED)
                if prioritize_smaller_brains:              
                    #get the list of the genepool sizes
                    genepool_sizes=[]
                    for i in range(len(specie.brains)):
                        a=len(specie.brains[i].genepool)
                        while a in genepool_sizes:             #lazy way of avoiding a list with 2 entries of the same value
                            a+=1                            
                        genepool_sizes.append(a)
                    #order brains and results according to the genepool_sizes list
                    genepool_sizes, ordered_lists = NAIsf.sort_lists(genepool_sizes, [specie.brains,specie.adjus_results], reverse=False)
                    
                    specie.brains = ordered_lists[0]
                    specie.adjus_results = ordered_lists[1] 
                
                #remove the last brains
                #the remaining will crossover with the first (dominant) brain
                #while the number of brains is higher than the number of offspring + the dominant brain
                while len(specie.brains) > specie.max_offspring+1:
                    specie.remove_brain(brain_index=specie.max_offspring) #remove the first brain after the last max offspring brain parent
                    specie.adjus_results.pop(specie.max_offspring)              #same for results
        
                #crossover every recessive brain with the dominant brain in the species
                dominant_index = 0
                for brain_index in range(1,len(specie.brains)):
                    #combine the 2 brains
                    child_brain = NAIsf.combine_fenotypes(specie.brains[dominant_index],specie.brains[brain_index])

                    #place child in parent species 
                    self.migrate(child_brain, specie)
                    
            elif len(specie.brains)==2:                 #breaking up if statements to avoid errors with empty species
                #if there only 2 species, crossover the dominant brain of the first species with the dominant brain of the second species
                if specie.adjus_results[0] > self.species[1].adjus_results[0]:
                    dominant_index = 0
                    recessive_index = 1
                else:
                    dominant_index = 1
                    recessive_index = 0
                
                #only if they aren't the same  
                if specie.brains[0] != specie.brains[1]:
                    #combine the 2 brains
                    child_brain = NAIsf.combine_fenotypes(specie.brains[dominant_index],specie.brains[recessive_index])

                    #place child in parent species 
                    self.migrate(child_brain, specie)
                                
        #remove worst performing species
        #this is species with the worst performing brains (last species (its ordered by score))
        self.update_species_brain_count()
        while self.brain_count > self.MaxBrains:
            for specie in self.species:
                #remove the last brains
                self.species.pop()
                self.update_species_brain_count()
        
        
        pass
           
    #################### INFORMATION ####################   
    
    #prints the information about the existing species and brains
    def print(self , ordered_by_score = False, include_results = False):
        
        #optionally, we can print the species by score
        #for this, the species are ordered by score then for every species, the brains are ordered by score
        #only makes sense if scores exist in the first place
        if ordered_by_score and len(self.species[-1].adjus_results) > 0:
            self = NAIsf.order_by_score(self) 
        
        self.update_species_brain_count()
        print("------------ Population Print ------------")
        print(f"Number of species: {len(self.species)}, Number of brains: {self.brain_count}")
        for i,specie in enumerate(self.species):
            print(f"<SPECIE> = {i}:")
            for j,brain in enumerate(specie.brains):
                print(f"-->     <BRAIN> = {j}: (Conn Count = {len(brain.genepool)}, Node_Count = {brain.NodeCount})", end='')
                if include_results:
                    print(f"        score: {specie.adjus_results[j]}",end='')
                print("")
        print("------------ Population Print END------------")
        pass

    #save to file the entire population
    def save_population(self, filename, overwrite = False):
        #standard path
        path = "NeatAI/brain_saves/" + filename
        
        #check if file exists
        #if it does, change the path name
        i=1
        while os.path.isfile(path) and not overwrite:
            extension_index = path.find(".txt")
            path = path[:extension_index-2] + "_" + str(i) + ".txt"
            i+=1
        
        #open file
        file = open(path, "w")
        
        #write to file
        file.write(f"<Inov> = {self.innovation} :<MaxOff> = {self.max_offspring} : <MaxSpeDist> = {self.MaxSpecialDist}\n")  
        for specie in self.species:
            for brain in specie.brains:
                file.write(f"<SPECIE> = {self.species.index(specie)} : <BRAIN> = {specie.brains.index(brain)}\n")
                file.write(f"<NOI> = {brain.NOI}, <NOO> = {brain.NOO}, <NodeCount> = {brain.NodeCount}\n")  
                for i,con in enumerate(brain.genepool):
                    file.write(f"[{con.status}] <{i}> Connection: {con.in_index} -> {con.out_index}: Weight = {con.weight}: Inovation = {con.inov}\n")

        #close file
        file.close()      
        pass

    #load from file the entire population
    def load_population(self, filename):
        #standard path
        path = "NeatAI/brain_saves/" + filename
        
        #check if file exists
        if not os.path.isfile(path):
            exit(f"FAIL, could not load pop from file ({path})")
        
        #open file, read lines and close file
        file = open(path, "r")
        lines = file.readlines()
        file.close()
        
        #get info on the pop
        self.innovation = int(lines[0][9:lines[0].find(":",9)])
        self.max_offspring = int(lines[0][lines[0].find("<MaxOff>")+11:lines[0].find(":",lines[0].find("<MaxOff>")+11)])
        self.MaxSpecialDist = int(lines[0][lines[0].find("<MaxSpeDist>")+15:-1])
        
        #get rid of the first line
        lines.pop(0)
        
        #get species and brains
        #if the population didn't already have species, create them
        if len(self.species) == 0:
            self.add_new_species()                               #add first species
        elif len(self.species) > 1:
            self.species = [self.species[0]]                     #clear all other species
            
        if len(self.species[0].brains) == 0:
            self.species[0].add_brain(brain_fenotype(0,0))       #add a dummy brain to the first species
        elif len(self.species[0].brains) > 1:
            self.species[0].brains = [self.species[0].brains[0]] #clear all other brains
        
        self.species[0].brains[0].genepool = []      #clear all connections
        
        #keep cursor for species and brain index
        cursor_species_index = 0
        cursor_brain_index = 0
        cursor_conn_index = 0
        index = 0
        #using a while loop allows for the index to change in a custum way
        while index < len(lines):
            line = lines[index]
            #check if its reading new species
            if line.find("<SPECIE>") != -1:
                cursor_species_index = int(line[11: line.find(":",11)])
                cursor_brain_index = int(line[line.find("<BRAIN>")+10:-1])
                cursor_conn_index = 0               #reset
                
                #check if the species exists
                if cursor_species_index >= len(self.species):
                    self.add_new_species()
                #check if the brain exists inside the species
                if cursor_brain_index >= len(self.species[cursor_species_index].brains):
                    self.species[cursor_species_index].add_brain(brain_fenotype(0,0)) 
                    
                #iterate to the next line with info on the brain
                index += 1
                line = lines[index]
                #read info on brain
                #get info on the brain
                self.species[cursor_species_index].brains[cursor_brain_index].NOI = int(line[7:line.find(",",7)])
                self.species[cursor_species_index].brains[cursor_brain_index].NOO = int(line[line.find("<NOO>")+7:line.find(",",line.find("<NOO>")+7)])
                self.species[cursor_species_index].brains[cursor_brain_index].NodeCount = int(line[line.find("<NodeCount>")+13:-1])

                #iterate to the next line in order to read brain data
                index +=1
                line = lines[index]
            
            #normal routine: read brain connections
            
            #UNNECESSARY CHECKS, JUST MAKE SURE THERE'S NO CONNECTIONS IN THE FIRST PLACE
            #see if a new connection needs to be added
            #if cursor_conn_index > 0 or len(self.species[0].brains[0].genepool) == 0:
            #    self.species[cursor_species_index].brains[cursor_brain_index].add_random_connection()
            
            #add new connection
            self.species[cursor_species_index].brains[cursor_brain_index].add_random_connection()
            
            #parse the line
            #get status
            if line[1] == "T":
                self.species[cursor_species_index].brains[cursor_brain_index].genepool[cursor_conn_index].status = True
            else:
                self.species[cursor_species_index].brains[cursor_brain_index].genepool[cursor_conn_index].status = False
                
            #get in_index and out_index
            i_in_out_start = line.find("Connection")+11
            i_in_out_middle = line.find("->")
            i_out_final = line.find(":",i_in_out_middle)
            self.species[cursor_species_index].brains[cursor_brain_index].genepool[cursor_conn_index].in_index = int(line[i_in_out_start:i_in_out_middle-1])
            self.species[cursor_species_index].brains[cursor_brain_index].genepool[cursor_conn_index].out_index = int(line[i_in_out_middle+2:i_out_final])
            
            #get weight
            i_weight_start=line.find("Weight")+9
            i_weight_end = line.find(":",i_weight_start)
            self.species[cursor_species_index].brains[cursor_brain_index].genepool[cursor_conn_index].weight = float(line[i_weight_start:i_weight_end])
            
            #get inovation number
            i_inov_start = line.find("Inovation")+12
            i_inov_end = line.find("\n",i_inov_start)
            self.species[cursor_species_index].brains[cursor_brain_index].genepool[cursor_conn_index].inov = int(line[i_inov_start:i_inov_end])
            
            #update line search index and conn index
            index += 1
            cursor_conn_index +=1
        
        #Before leaving, update counts
        self.update_species_brain_count()
        
        pass
    
    #update count info
    def update_species_brain_count(self):
        self.species_count = len(self.species)
        self.brain_count = 0
        for specie in self.species:
            specie.update_brain_count()
            self.brain_count += specie.brain_count
        pass
    
    #update nodecount info
    #used after crossover as its easier
    def update_all_brains_nodecounts(self):
        for specie in self.species:
            for brain in specie.brains:
                brain.update_nodecount()    
        pass
    
    #same as update results but gets a list of the current results
    #index specification works the same way
    def get_results(self, specie_index = -1, brain_index = -1):
        results = []
        if specie_index != -1:
            if brain_index != -1:
                results= self.species[specie_index].adjus_results[brain_index] 
            else:
                results= self.species[specie_index].adjus_results 
                
        elif brain_index == -1:     #supplying a brain index but not a specie index is not allowed
            #results for all species in all brains
            cursor = 0
            for specie in self.species:
                results.append(specie.adjus_results)
                
        return results
    
    #goes species by species and gets the max difference between the results of the brains
    #appends the max difference of each species to a list
    def get_max_speciation_difference_per_species(self):
        max_diff = []
        
        for specie_index in range(len(self.species)):
            max_diff.append(0)
            for index_row in range(len(self.species[specie_index].brains)):
                #index_row+1 to avoid checking a pair of the same brain
                #doing it this way avoids checking the same brains more than once
                for index_col in range(index_row+1,len(self.species[specie_index].brains)):
                    diff = NAIsf.compare_fenotypes(self.species[specie_index].brains[index_row],self.species[specie_index].brains[index_col])
                    if diff[0] > max_diff[specie_index]:
                        max_diff[specie_index] = diff[0]
                               
        return max_diff
    #################### DEBUG AND MISCELANEOUS ####################
    
    #calculate the adjusted fitness of every brain in the population
    #assign a number of offspring to each species
    #WARNING: THIS IS ALREADY CALLED INSIDE CREATE NEW GENERATION
    def update_planned_offspring_count(self):
        #storage
        summed_adjusted_fitness = []
        
        #calculate the adjusted fitness of every brain in the population
        for specie in self.species:
            summed_adjusted_fitness.append(sum(specie.adjus_results)/len(specie.brains))
            
        #calculate the number of offspring for each species by linear interpolation
        if len(self.species) != 1:
            offspring_slope = (self.max_offspring - self.min_offspring)/(max(summed_adjusted_fitness)-min(summed_adjusted_fitness))
            
            for index, specie in enumerate(self.species):
                specie.max_offspring = round(self.min_offspring + offspring_slope*(summed_adjusted_fitness[index]-min(summed_adjusted_fitness)))
        #if there's only one species, set max crossover
        else:
            self.species[0].max_offspring = self.max_offspring
                    
        pass
    
    #check for all species if there are species with only one brain
    #populate them with a new brain    
    def populate_species(self):
        for specie in self.species:
            if len(specie.brains) == 1:
                specie.add_brain(specie.brains[0].copy())
        pass
    
    #used for checking and comparing all the brains
    #will not care about order
    #if specied, it can retrieve specific brains using the single index
    def get_brains(self,brain_index_list = []):
        all_brains = []
        cursor = 0
        for specie in self.species:
            for brain in specie.brains:
                if brain_index_list == []:
                    all_brains.append(brain)
                elif cursor in brain_index_list:
                    all_brains.append(brain)
                cursor += 1
                
        return all_brains
        
    #used for when the scores need to be bound to the brains, and not the species
    def store_scores_in_brains(self):
        for specie in self.species:
            for brain_index, brain in enumerate(specie.brains):
                brain.score = specie.adjus_results[brain_index]
            
    #used for the ooposite of store_scores_in_brains, retrieves the scores, stores them in the species
    #also returns a complete list of scores
    def retrieve_scores_from_brains(self):
        scores = []
        for specie in self.species:
            specie.specie_retrieve_scores_from_brains()
            scores.append(specie.adjus_results)
            
        return scores
        
        
    pass
           
class species:
    def __init__(self) -> None:
        self.brains = [] #list of all the brains in the species
        self.adjus_results = [] #list of all the adjus_results of the species, ordered in the same way as the brains              
        
        self.max_offspring = 1 #max number of offspring per species
        self.brain_count=0     
        pass

    
    #################### BRAINS MANAGEMENT ####################
    
    def add_brain(self,brain):
        self.brains.append(brain)
        self.brain_count += 1
        pass
    
    #removes brain from species either by index or by object itself
    def remove_brain(self,brain=-1,brain_index=-1):
        if brain_index != -1:
            self.brains.pop(brain_index)
            self.brain_count -= 1
        elif brain != -1 and brain in self.brains:
            self.brains.remove(brain)
            self.brain_count -= 1
        pass
    
    def update_results(self,results, index = -1):
        if index == -1:                             #all brain results
            self.adjus_results = results
        else:                                       #individual brian results
            self.adjus_results[index] = results
            
        #EXPLICIT FITNESS SHARING
        #to adjust the results, divide it by the number of brains of specie
        #this way, the results are normalized
        self.adjus_results = [i/len(self.brains) for i in self.adjus_results]
        pass
    
    #################### INFORMATION ####################
    def update_brain_count(self):
        self.brain_count = len(self.brains)
        pass
    
    #################### DEBUG AND MISCELANEOUS ####################
    
    #retrive scores per brain in species
    def specie_retrieve_scores_from_brains(self):
        for brain_index, brain in enumerate(self.brains):
            self.adjus_results[brain_index] = brain.score
        pass
      
class brain_fenotype:
    def __init__(self,NOI,NOO):
        #initiliaze the brain with the minimum number of connections/nodes
        self.NOI = NOI                #number of input nodes
        self.NOO = NOO                #number of output nodes
        self.NodeCount = NOI + NOO    #total number of nodes
        self.LastNodeIndex = NOI + NOO - 1 #index of the last node (might be different to node count due to mutations) 
        self.score = 0                #lastest score of the brain
        
        self.genepool = []            #list of all the connections in the brain
        self.inov_counter = 1
        for i in range(NOO):
            for j in range(NOI): #for each output node, connect it to each input node
                self.genepool.append(conn_gene(j,i+NOI,rnd.uniform(-1,1),self.inov_counter)) #add the connection to the genepool    
                self.inov_counter += 1 #increment the innovation number
        pass
    
    #creates copy of the brain and returns it
    def copy(self):
        new_brain = brain_fenotype(self.NOI,self.NOO)
        new_brain.genepool = self.genepool.copy()
        new_brain.inov_counter = self.inov_counter
        new_brain.NodeCount = self.NodeCount
        new_brain.LastNodeIndex = self.LastNodeIndex
        new_brain.score = self.score
        return new_brain
    
    #from a given fenotype, compute the output of the brain
    #given the input
    def compute_output(self,input):
        
        #sort the genepool by layers
        node_pos_list, change, Number_of_layers = NAIsf.layer_sort(self,[],0)
        while change:
            node_pos_list, change, Number_of_layers = NAIsf.layer_sort(self,node_pos_list,Number_of_layers)
            
        #create a mupet fenotype that can be reduced over time
        #[WARNING] USE COPY TO AVOID TRANSFERING POINTER
        mupet_fenotype = self.copy()
        
        #create a list to store all gene values
        #needs to use last node index+1 to avoid out of bounds
        values = np.zeros(self.LastNodeIndex+1)
        values[0:self.NOI] = input
        
        #for every node, from layer 2 to output layer from left to right, compute the value of the node
        for layer in range(1,Number_of_layers):
            #search for a node in said layer
            node_index = 0
            len_node_list = len(node_pos_list)
            while node_index < len_node_list:
                if node_pos_list[node_index][1] == layer:
                    #found a node in the currently sought layer
                    #compute the value of the node
                    #search all connections in the entire genepool that lead to the node
                    con_index = 0
                    len_con_list = len(mupet_fenotype.genepool)
                    while con_index < len_con_list:
                        con = mupet_fenotype.genepool[con_index]    #this helps with readability
                        current_node_index = node_pos_list[node_index][0]   #so does this
                        
                        
                        if con.out_index == current_node_index:
                            #found a connection that leads to the node
                            #adding up value
                            if con.status == True:
                                values[current_node_index] += con.weight * values[con.in_index] 
                            
                            #REMOVE STUFF TO MAKE ITERATIONS FASTER AS IT GOES
                            #remove connection and update pool size
                            mupet_fenotype.genepool.pop(con_index)
                            len_con_list -= 1
                        else:
                            #this connection does not lead to current node
                            #search next connection
                            con_index += 1
                            
                    #apply activation function
                    #only do so once all the values have been added onto the current node
                    values[current_node_index] = NAIsf.convert_according_to_AF(values[current_node_index])
                    
                    #remove node and update gene layer list size
                    #by removing this list item, iterating is not necessary
                    node_pos_list.pop(node_index)
                    len_node_list -= 1
                else:
                    #search next node
                    node_index += 1
            
        #output can be taken from values
        output = values[self.NOI:self.NOI + self.NOO]           
        return output,values
    
    #################### MUTATIONS ####################
    #necesssary because they need to update the innovation counter and other information
    
    def mutation_update_weight(self, index_con, new_weight, index_in=0, index_out=0):
        exit_code = 0
        
        #search for a connection by the node indexes
        if index_con == -1:
            index_con = NAIsf.search_con(self.genepool, index_in, index_out)
            if index_con == -1:
                exit_code = 1
                exit("Connection not found")
        
        self.genepool[index_con].weight = new_weight   
        
        #update weight isn't a topological innovation
        #self.inov_counter += 1             
        return exit_code 
    
    def mutation_addconnection(self, in_index, out_index, weight):       
        #add a connection to the brain
        self.genepool.append(conn_gene(in_index,out_index,weight, self.inov_counter))
        
        #update counter
        self.inov_counter += 1
        
        return 0
    
    def mutation_toggleconnection(self, index):
        #toggle the status of a connection
        self.genepool[index].Toggle()
        
        #toggle connection isn't a topological innovation
        #self.inov_counter += 1
        return 0
    
    def mutation_addnode(self,index_in,index_out,weight):
        exit_code = 0
        
        #search for the connection
        index_con = NAIsf.search_con_index(self.genepool, index_in, index_out)
        
        #add a new node
        #if the connection exists, it must be disabled
        if self.genepool[index_con].status == True and index_con != -1:
            self.genepool[index_con].Toggle()
            
            #also the connection must be split into two and one of them must inherit the old weight value
            #add connections to the new node
            self.genepool.append(conn_gene(index_in,self.LastNodeIndex+1,weight,self.inov_counter))
            self.inov_counter += 1 
            self.genepool.append(conn_gene(self.LastNodeIndex+1,index_out,self.genepool[index_con].weight, self.inov_counter))
            self.inov_counter += 1 
            
        else: 
            #if it doesn't exist, the same loop precaution as for add_connection must be taken
            if NAIsf.detect_loops(self, critical_index=index_in, current_node_index=index_out, order=5):
                #print("[LOOP] NOT ADDING NODE DUE TO LOOP")
                #ttf.record_to_text_file("[LOOP] NOT ADDING NODE DUE TO LOOP")
                return 1
            else:
            #if loop is not a problem
            #simply create 2 connections of the same weight
            #add connections to the new node    
                self.genepool.append(conn_gene(index_in,self.LastNodeIndex+1,weight,self.inov_counter))
                self.inov_counter += 1
                self.genepool.append(conn_gene(self.LastNodeIndex+1,index_out,weight,self.inov_counter))
                self.inov_counter += 1 

        
        
        #update node count and innovation counter
        self.NodeCount += 1  
        self.LastNodeIndex += 1
        
        return exit_code
    
    def mutation_removenode(self, index):
        exit_code = 0
        
        #removing a node means removing all the connections in and out of it
        #search for the connections
        #can't use for loop, we are activelly removing items from the list
        i=0
        while i < len(self.genepool):
            if self.genepool[i].in_index == index or self.genepool[i].out_index == index:
                    self.genepool.pop(i)
                    self.NodeCount -= 1
            else:
                i += 1
                
            #update the lastnodeindex
            self.update_nodecount()
            if self.LastNodeIndex == index:
                self.LastNodeIndex -= 1
        
        return exit_code
    
    def mutation_random(self, max_mutations = 3):
        #show debug messages
        debug = False
        
        #create a return info with the mutations made
        # innovation : [conn_index, in_index, out_index]
        # con index is used to alter the inov_number in case it already existed
        mutations = {}
        
        #0 - add connection
        #1 - add node
        #2 - remove node
        #3 - toggle connection
        #4 - update weight
        rnd.seed = rnd.uniform(0,1000)
        mutation_count = rnd.randint(1,max_mutations) #Up to 3 simultaneous mutations
        
        for current_mutation_count in range(mutation_count):
            mutation = rnd.randint(0,4) 
            
            if mutation == 0:                       #ADD CONNECTION
                    
                #stop it from adding a connection that already exists
                #second condition is to emulate a do-while loop
                checks = 0
                in_index = 0
                out_index = 0
                
                #connection must not exist from A to B or from B to A
                #this means that the connection between 2 nodes must be unidirectional
                #by splitting into 2 while loops, we avoid searching the genepool twice every time
                while (NAIsf.search_con_index(self.genepool, out_index, in_index) != -1 or in_index == out_index) and checks < 31:
                    #start out with invalid indexes
                    in_index = 0
                    out_index = 0
                    while (NAIsf.search_con_index(self.genepool, in_index, out_index) != -1 or in_index == out_index) and checks < 31:
                        #if its here, then the connection already exists
                        #get new combination of input/output nodes such that a new connection that doesn't exist is created
                        
                        #input node index
                        if rnd.randint(0,1) < 0.5 or self.NOO+self.NOI == (self.LastNodeIndex + 1): #if there are no hidden nodes
                            in_index = rnd.randint(0, self.NOI-1)                         #input nodes for input
                        else:
                            in_index = rnd.randint(self.NOO+self.NOI, self.LastNodeIndex)     #hidden nodes for input  
                    
                        out_index = in_index
                        #output node index
                        while out_index == in_index:
                            out_index = rnd.randint(self.NOI, self.LastNodeIndex)
                        
                        if checks > 30:
                            if debug:
                                print("No available nodes without a connection")
                        checks += 1

                    #before leaving this loop nest, loop again to check if the same connection exists in the opposite direction
                
                #CHECK FOR LOOPS
                if NAIsf.detect_loops(self, critical_index=in_index, current_node_index=out_index, order=10):
                    if debug:
                        print("[LOOP] NOT ADDING CONNECTION DUE TO LOOP")
                        ttf.record_to_text_file("[LOOP] NOT ADDING CONNECTION DUE TO LOOP")
                else:
                    #add connection
                    mutations.update({self.inov_counter : [len(self.genepool), in_index, out_index]})
                    self.mutation_addconnection(in_index, out_index, rnd.uniform(0,1))
                    
                #DEBUG
                if debug:
                    print(f"Added connection: {in_index} -> {out_index}")
                    ttf.record_to_text_file(f"Added connection: {in_index} -> {out_index}")
                           
            if mutation == 1:                       #ADD NODE
                
                #input node index
                if rnd.randint(0,1) < 0.5 or self.NOO+self.NOI == (self.LastNodeIndex + 1):   #if there are no hidden nodes
                    in_index = rnd.randint(0, self.NOI-1)                           #input nodes for input
                else:
                    in_index = rnd.randint(self.NOO+self.NOI, self.LastNodeIndex)     #hidden nodes for input  
                
                out_index = in_index
                #output node index
                while out_index == in_index:
                    out_index = rnd.randint(self.NOI, self.LastNodeIndex)
                    
                #add node
                #check if it was successful (its possible it didnt add a node due to loops)
                if self.mutation_addnode(in_index, out_index, rnd.uniform(0,1)) == 0:
                    mutations.update({self.inov_counter-2: [len(self.genepool)-2,in_index,self.genepool[-1].in_index]})
                    mutations.update({self.inov_counter-1: [len(self.genepool)-1,self.genepool[-1].in_index,out_index]})
                
                #DEBUG
                if debug:
                    print(f"Added node between {in_index} and {out_index}")
                    ttf.record_to_text_file(f"Added node between {in_index} and {out_index}")
            
            if mutation == 2:                       #REMOVE NODE
                #choose random node to remove (hidden only)
                #only works if there are actually hidden nodes
                if self.NodeCount-1 > self.NOI+self.NOO:
                    index_range = [self.NOI+self.NOO, self.LastNodeIndex]
                    index = rnd.randint(index_range[0], index_range[1])
                
                    #remove node
                    self.mutation_removenode(index)
                    
                    #update mutations to not include removed nodes
                    keys = list(mutations.keys())
                    for key in keys:
                        if NAIsf.search_con_index(genepool=self.genepool,in_index=mutations[key][1],out_index=mutations[key][2]) == -1:
                            #this connection doesn't exist anymore, remove it
                            poped_mutation = mutations.pop(key)
                            
                    #update all others such that they point to the correct connection index
                    #unfortunatelly since they are not order, the only way to do this is to check all of them
                    for mutation_key in mutations.keys():
                        mutations[mutation_key][0] = NAIsf.search_con_index(genepool=self.genepool,
                                                                                in_index=mutations[mutation_key][1],
                                                                                out_index=mutations[mutation_key][2])
         
                    #DEBUG
                    if debug:
                        print(f"Added node between {in_index} and {out_index}")
                        ttf.record_to_text_file(f"Added node between {in_index} and {out_index}")
                               
            if mutation == 3:                       #TOGGLE CONNECTION
                index = rnd.randint(0, len(self.genepool)-1)
                previous_status = self.genepool[index].status
                #toggle connection
                self.mutation_toggleconnection(index)
                
                #DEBUG
                if debug:
                    print(f"Connection {index} toggled from {previous_status} to {not previous_status}")
                    ttf.record_to_text_file(f"Connection {index} toggled from {previous_status} to {not previous_status}")
            
            if mutation == 4:                       #UPDATE WEIGHT
                index = rnd.randint(0, len(self.genepool)-1)
                old_weight = self.genepool[index].weight
                
                #update weight by +/- 20% max
                amplitude = rnd.uniform(-1,1) * 0.2 
                new_weight = old_weight + amplitude * old_weight
                
                #update weight
                self.mutation_update_weight(index, new_weight)
                
                #DEBUG
                if debug:               
                    print(f"Connection {index} weight updated to {new_weight} ({amplitude*100}%)")
                    ttf.record_to_text_file(f"Connection {index} weight updated to {new_weight} ({amplitude*100}%)")
        
        #return info with the mutations made
        
        return mutations
    
    #################### INFORMATION ####################
    #creates a diagram of the brain
    def observe_mental_map(self):
        #observe the brain's state
        vz.draw_genepool(self)
        plt.show()
        pass
    
    #saves a diagram of the brain to a path
    def save_mental_picture(self, filename, overwrite = False):
        #standard path
        path = "NeatAI/brain_saves/" + filename
        
        #save the brain's state
        vz.draw_genepool(self)
        plt.savefig(path)
        plt.close()
        pass
    
    #prints to console all the connections in the brain
    #includes details
    #in_index, out_index and inov can be used to filter results
    def print(self, in_index = -1 , out_index = -1, inov = -1, active_only = False):
        #first print NOI, NOO and NodeCount
        print(f"<NOI> = {self.NOI}, <NOO> = {self.NOO}, <NodeCount> = {self.NodeCount}")
        
        #then all the connections
        for i,con in enumerate(self.genepool):
            if active_only and not con.status:                    #active_only filter
                continue
            if in_index != -1 and con.in_index != in_index:     #in_index filter
                continue
            if out_index != -1 and con.out_index != out_index:  #out_index filter
                continue
            if inov != -1 and con.inov != inov:                 #inov filter
                continue
            
            #if its here, it satisfies all the filters
            #print to console
            print(f"[{con.status}] <{i}> Connection: {con.in_index} -> {con.out_index}: Weight = {con.weight}: Inovation = {con.inov}")
        pass
    
    #prints to file all the connections in the brain
    #includes details
    def save_mental_connections(self,filename, overwrite = False):
        #standard path
        path = "NeatAI/brain_saves/" + filename
        
        #check if file exists
        #if it does, change the path name
        i=1
        while os.path.isfile(path) and not overwrite:
            extension_index = path.find(".txt")
            path = path[:extension_index-2] + "_" + str(i) + ".txt"
            i+=1
        
        #open file
        file = open(path, "w")
        
        #write to file
        file.write(f"<NOI> = {self.NOI}, <NOO> = {self.NOO}, <NodeCount> = {self.NodeCount}\n")  
        for i,con in enumerate(self.genepool):
            file.write(f"[{con.status}] <{i}> Connection: {con.in_index} -> {con.out_index}: Weight = {con.weight}: Inovation = {con.inov}\n")
        
        #close file
        file.close()      
        pass
      
    #loads connections from a file
    #wipes all previous connections, copies brain from file
    def load_mental_connections(self,filename):
        #standard path
        path = "NeatAI/brain_saves/" + filename
        
        #check if file exists
        if not os.path.isfile(path):
            exit(f"FAIL, could not load brain from file ({path})")
        
        #open file, read lines and close file
        file = open(path, "r")
        lines = file.readlines()
        file.close()
        
        #get info on the brain
        self.NOI = int(lines[0][7:lines[0].find(",",7)])
        self.NOO = int(lines[0][lines[0].find("<NOO>")+7:lines[0].find(",",lines[0].find("<NOO>")+7)])
        self.NodeCount = int(lines[0][lines[0].find("<NodeCount>")+13:-1])
        
        #remove that information line
        lines.pop(0)
        
        #read connection from lines
        old_genepool_len = len(self.genepool)
        for index,line in enumerate(lines):
            #see if a new connection needs to be added
            if index > old_genepool_len-1:
                self.add_random_connection()
            
            #parse the line
            #get status
            if line[1] == "T":
                self.genepool[index].status = True
            else:
                self.genepool[index].status = False
                
            #get in_index and out_index
            i_in_out_start = line.find("Connection")+11
            i_in_out_middle = line.find("->")
            i_out_final = line.find(":",i_in_out_middle)
            self.genepool[index].in_index = int(line[i_in_out_start:i_in_out_middle-1])
            self.genepool[index].out_index = int(line[i_in_out_middle+2:i_out_final])
            
            #get weight
            i_weight_start=line.find("Weight")+9
            i_weight_end = line.find(":",i_weight_start)
            self.genepool[index].weight = float(line[i_weight_start:i_weight_end])
            
            #get inovation number
            i_inov_start = line.find("Inovation")+12
            i_inov_end = line.find("\n",i_inov_start)
            self.genepool[index].inov = int(line[i_inov_start:i_inov_end])
            
            #update other stuff
            self.update_nodecount()
        pass
        
    #################### DEBUG ####################
    
    #adds a new connection from 0 to 0
    #gives it weight, inov numbers of 0
    #status is disabled
    #DOES NOT INCREMENT INOV COUNTER
    #DOES NOT UPDATE NODE COUNT
    #SHOULD NOT BE USED IN NORMAL CIRCUMSTANCES
    def add_random_connection(self):        
        self.genepool.append(conn_gene(0,0,0,0))
        self.genepool[-1].status = False
        pass

    #updates the weight without changing inov counter
    def update_weight_without_changing_inov(self, index_con, new_weight, index_in=0, index_out=0):
        #search for a connection by the node indexes
        if index_con == -1:
            index_con = NAIsf.search_con(self.genepool, index_in, index_out)
            if index_con == -1:
                exit("Connection not found")
        
        self.genepool[index_con].weight = new_weight                 
        pass
        
    #used for when the node count is updated
    def update_nodecount(self):
        self.NodeCount = 0
        for con in self.genepool:
            if con.in_index + 1 > self.NodeCount:
                self.NodeCount = con.in_index + 1
                self.LastNodeIndex = con.in_index
            if con.out_index + 1 > self.NodeCount:
                self.NodeCount = con.out_index + 1
                self.LastNodeIndex = con.out_index
        pass
                
    #observe function but doesn't draw
    #usefull for custum drawing (i.e. real time drawing)
    def draw_mental_map(self):
        #observe the brain's state
        vz.draw_genepool(self)
        pass
    
class conn_gene:
    def __init__(self, in_index, out_index, weight, inov):
        self.in_index = in_index     # Index of the input and output nodes
        self.out_index = out_index   # Index of the input and output nodes
        self.weight = weight         # Weight of the connection
        self.inov = inov             # Innovation number of the gene
        self.status = True           # True if enabled, False if disabled        
        pass
        
    def Toggle(self):               # Toggles the status of the connection
        self.status = not self.status
        pass