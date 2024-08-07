from NeatAI import classes
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib as mpl
import random as rnd
import numpy as np
from NeatAI import visualizer as vz
from NeatAI import temporary_testing_funcs as ttf
    

#search for connection with given in, out indexes
#for out_index = 0, it will return all the connections with the given in_index in a list
#otherwise it will return the index of the single connection
def search_con_index(genepool, in_index, out_index=0):
    counter=0
    if out_index != 0:          #find specific connection
        for con in genepool:
            if con.in_index == in_index and con.out_index == out_index:
                return counter
            counter += 1
    else:                      #find any connection with in_index
        indexes=[]
        for con in genepool:
            if con.in_index == in_index:
                indexes.append(counter)
            counter += 1
        return indexes
    return -1

#combine and merge 2 fenotypes according to innavtion numbers
#only invoke after confirming that speciation is the same!!!
#use compare_fenotypes to check distance before this
def combine_fenotypes(dominant_fenotype, recessive_fenotype):
    #debug
    debug = False
    
    #a copy of the dominant fenotype is created
    child_fenotype = dominant_fenotype.copy()
    
    #get all the inovation numbers that exist in the dominant fenotype
    existant_inov = []
    for con in dominant_fenotype.genepool:
        #note down all the inovation numbers that appear if they haven't been noted down already
        if con.inov not in existant_inov:   
            existant_inov.append(con.inov)
    
    #disjoint genes need to be added to the child from the recessive
    #excess genes do NOT need to be added to the child
    #do so by checking if there are genes in the recessive with a inovation number that doesn't exist in the dominant
    speed_cursor = 0   #disjoint and recessive genes will be inserted from left to right always, this helps speed it up
    for con in recessive_fenotype.genepool:
        #check if theres a connection that doesn't exist in child
        #AND it cannot be an excess connection from the recessive
        if con.inov not in existant_inov and con.inov < child_fenotype.genepool[-1].inov:  
            #this connection is disjoint or excess
            #need to check if it exists in the child already
            if search_con_index(child_fenotype.genepool,con.in_index,con.out_index) == -1:
                #it doesn't exist, still need to check if adding it would result in a loop
                #do this by checking if by connecting the in_index(critical) to the out_index, a loop is created
                if detect_loops(child_fenotype,con.in_index,con.out_index, order = 10) == False:
                    #loop not detected, add connection

                    #search for index to place the connection
                    #speed cursor is conserved in the for loop to speed up the process
                    while speed_cursor < len(child_fenotype.genepool):
                        if child_fenotype.genepool[speed_cursor].inov > con.inov:   #stops in the node after the one to be inserted
                            child_fenotype.genepool.insert(speed_cursor,con)
                            break
                        speed_cursor += 1
                else:
                    if debug:
                        print(f"[LOOP] Loop detected, connection with inov {con.inov} from {con.in_index} to {con.out_index} not added")
                        ttf.record_to_text_file(f"[LOOP] Loop detected, connection with inov {con.inov} from {con.in_index} to {con.out_index} not added")
            else:
                if debug:
                    print(f"[DUPLICATE] Connection with inov {con.inov} from {con.in_index} to {con.out_index} already exists")
                    ttf.record_to_text_file(f"[DUPLICATE] Connection with inov {con.inov} from {con.in_index} to {con.out_index} already exists")
    
    #update the nodecount
    child_fenotype.update_nodecount()
    #make sure score is reset to worst value possible
    child_fenotype.score = -1000
    
    return child_fenotype

#compares 2 fenotypes for disjoint and excess genes
#also measure the average connection weight difference
#returns the compatibility distance
def compare_fenotypes(fenotype1,fenotype2):
    #Weights
    #delta = c1 *  excess/gene_larger_genome + c2 * disjoint/gene_bigger_genome + c3 * AWD
    #excess and disjoint genes are more critical than weight differences
    c1 = 1               
    c2 = 1
    c3 = 0.4
    
    #get data for the final calculation
    bigger_fenotype_conn_count = max(len(fenotype1.genepool),len(fenotype2.genepool))
    smaller_fenotype_conn_count = min(len(fenotype1.genepool),len(fenotype2.genepool))
    
    #counters
    disjoint_counter = 0
    excess_counter = 0
    weight_difference = []
     
    #get the dictionary of the existing inovation numbers and respective connection indexes
    #do this for fenotype 1
    existant_inov_feno1 = {}
    for index, con in enumerate(fenotype1.genepool):
        #note down all the inovation numbers that appear if they haven't been noted down already
        #if con.inov not in existant_inov_feno1:   
        existant_inov_feno1.update({con.inov:index})
        
    #repeat for fenotype 2
    existant_inov_feno2 = {}
    for index, con in enumerate(fenotype2.genepool):
        #note down all the inovation numbers that appear if they haven't been noted down already
        #if con.inov not in existant_inov_feno2:   
        existant_inov_feno2.update({con.inov:index})
            
    #first, go over all the inovations and check matching inovation numbers
    #if both lists have one inovation number, get the difference and store it
    #creating a phony existant inov dictionary to allow for removal of inovations that have been matched
    #whilst using a for loop
    phony_existant_inov_feno1 = existant_inov_feno1.copy()
    for inov in phony_existant_inov_feno1:
        if inov in existant_inov_feno2.keys():
            #found 2 connections with matching inov numbers
            conn_index1 = existant_inov_feno1[inov]
            conn_index2 = existant_inov_feno2[inov]
            
            #both fenotypes have the same inovation number
            #get the difference in weight
            weight_difference.append(abs(fenotype1.genepool[conn_index1].weight - fenotype2.genepool[conn_index2].weight))

            #remove from dictionary to allow for search of excess genes and disjoint genes
            existant_inov_feno1.pop(inov)
            existant_inov_feno2.pop(inov)
            
    #calculate average weight difference
    AWD = sum(weight_difference)/len(weight_difference)
    
    #get the number of disjoint and excess genes
    #only if they exist
    if len(existant_inov_feno1) == 0 or len(existant_inov_feno2) == 0:
        disjoint_counter = 0
        excess_counter = len(existant_inov_feno1) + len(existant_inov_feno2)    #one of these might not be 0, and correspond to excess genes
    
    else:
        #there are disjoint genes
        #first get the smaller last inov number for the genepool
        smaller_last_inov = fenotype1.genepool[-1].inov if fenotype1.genepool[-1].inov < fenotype2.genepool[-1].inov else fenotype2.genepool[-1].inov
        #also get the list with the biggest last inov (likelly an excess one)
        bigger_inov_list = existant_inov_feno1 if list(existant_inov_feno1)[-1] > list(existant_inov_feno2)[-1] else existant_inov_feno2
        
        #then get the number of excess genes
        for inov in bigger_inov_list:
            if inov > smaller_last_inov:
                excess_counter += 1
        
        #disjoing then becomes easy as its simply the sum of the remaining inovations minus the excess
        disjoint_counter = len(existant_inov_feno1) + len(existant_inov_feno2) - excess_counter
    
    #calculate delta (compatibility distance)
    d = c1 * excess_counter/bigger_fenotype_conn_count + c2 * disjoint_counter/smaller_fenotype_conn_count + c3 * AWD
    
    info_differences = [disjoint_counter,excess_counter,AWD]
    
    return d, info_differences

#sorts the nodes per layer according to the connections
def layer_sort(fenotype,node_pos_list=[], layer_count = 0):

    if node_pos_list == []:
        #initialize the node position list
        node_pos_list = []
        #inputs
        for i in range(0, fenotype.NOI):
            node_pos_list.append([i,0])         #input nodes
        for i in range(fenotype.NOI, fenotype.NOI + fenotype.NOO):
            node_pos_list.append([i,2])         #output nodes
        for i in range(fenotype.NOI + fenotype.NOO, (fenotype.LastNodeIndex+1)):
            node_pos_list.append([i,1])         #hidden nodes
            
    if layer_count == 0:   #first time initializing
        layer_count = 3     #input, hidden, output

    #call existing function from visualizer
    node_pos_list, change, layer_count = vz.reorganize_hidden_layer_positions(fenotype, node_pos_list,layer_count)
    
    return node_pos_list, change, layer_count

#activation function
def convert_according_to_AF(input, method = "sigmoid"):
    if method == "sigmoid":
        input = 1/(1+np.exp(input))
    if method == "tanh":
        input = np.tanh(input)*2

    #elif method == "rectified_liner":
    #    for i in input:
    #output = max(0,input)
    
    return input

#this function will detect if there is a loop in the hidden layer
#if there is, it will return true
#INSTRUCTIONS: at the first call of the function:
#   -- critical index: in_index of the new connection to be added
#   -- current_node_index: out_index of the new connection to be added
def detect_loops(fenotype, critical_index, current_node_index, order = 2):
    #this function detects for any series of connections that start at in_index
    #and end up in the in_index of the new connectionn
    #critical_index = new_conn.in_index
    #^^^^this is defined outside the recursive function to avoid unnecessary redefinition
    
    #get list of outgoing connections from the out index
    indexes = search_con_index(fenotype.genepool, current_node_index)
    nodes = [fenotype.genepool[i].out_index for i in indexes]
    
    #look for the critical index in the outgoing connections
    if critical_index in nodes:
        return True
    #if the critical index is not found, but the order is not 0, then the function is going to be called again
    #for every outgoing node, the same is going to be checked in a recursive manner
    #order is going to drop by 1
    elif order > 0:
        for index in nodes:
            if detect_loops(fenotype,critical_index, index, order=order-1) == True:
                return True
    
    #if it wasn't found and order is 0, then there is no loop
    return False

#orders brains (and also possibly species) by score
#order is in reverse (from highest to lowest)
#by default, it only orders brains
#by giving a population, it sorts everything
#FUNCTION NOT IN CLASSES ALLOWS FOR THE USE OF EITHER A POPULATION OR A SPECIE
def order_by_score(element, reverse = True):
    
    #define order direction
    rev_mult = 1
    if reverse:
        rev_mult = -1
    
    if type(element) == classes.population:     #no species supplied, order all species and all brains
        
        #order brains for each species
        for specie in element.species:
            sorted = False
            while not sorted:
                sorted = True
                for brain_i in range(1,len(specie.brains)):
                    #check if current element is smaller than the previous
                    if (specie.brains[brain_i].score - specie.brains[brain_i-1].score)*rev_mult < 0:
                        #still not sorted
                        sorted = False
                        
                        #correct main list
                        temp_holder = specie.brains[brain_i]                   #store current
                        specie.brains[brain_i] = specie.brains[brain_i-1]     #replace current with previous
                        specie.brains[brain_i-1] = temp_holder                 #replace previous with current (temp)
        
        #order species
        sorted = False
        while not sorted:   
            sorted = True
            for specie_i in range(1,len(element.species)):
                #check if current element is smaller than the previous
                if (element.species[specie_i].brains[0].score - element.species[specie_i-1].brains[0].score)*rev_mult < 0:
                    #still not sorted
                    sorted = False
                    
                    #correct main list
                    temp_holder = element.species[specie_i]                     #store current
                    element.species[specie_i] = element.species[specie_i-1]     #replace current with previous
                    element.species[specie_i-1] = temp_holder                 #replace previous with current (temp)
    
    elif type(element) == classes.species:    #specie was defined, order brains of that species
        
        sorted = False
        while not sorted:
            sorted = True
            for brain_i in range(1,len(element.brains)):
                #check if current element is smaller than the previous
                if (element.brains[brain_i] - element.brains[brain_i-1])*rev_mult < 0:
                    #still not sorted
                    sorted = False
                    
                    #correct main list
                    temp_holder = element.brains[brain_i]                   #store current
                    element.brains[brain_i] = element.brains[brain_i-1]     #replace current with previous
                    element.brains[brain_i-1] = temp_holder                 #replace previous with current (temp)
        

    else:
        exit("ERROR: element passed to order_by_score is not of type population or species")
    
    return element

#for when a single index exists, this will get the species and the brain index corresponding
#to the given index, this assumes that the brains are ordered by index in their species
#and the species are ordered by index in the population
#will return None, None if the index is out of bounds
def get_species_brain_index_from_single_index(pop, index):
    cursor=0
    species_index = 0
    brain_index = 0
    
    for specie in pop.species:
        for brain in specie.brains:
            if cursor == index:
                return species_index, brain_index
            cursor += 1
            brain_index += 1
        species_index += 1
        brain_index = 0

    return None, None
    
    
'''
#helpfull function to sort lists according to the main list
#will sort all lists and return them
def sort_lists(main_list, lists=[], reverse = False):
    
    #trick to implement reverse without making function twice as big
    rev_mult = 1
    if reverse:
        rev_mult = -1
    
    sorted = False
    temp_holder = []
    
    while not sorted:
        sorted = True
        for main_list_i in range(1,len(main_list)):
            #check if current element is smaller than the previous
            if (main_list[main_list_i] - main_list[main_list_i-1])*rev_mult < 0:
                
                #correct main list
                temp_holder = main_list[main_list_i]                   #store current
                main_list[main_list_i] = main_list[main_list_i-1]     #replace current with previous
                main_list[main_list_i-1] = temp_holder                 #replace previous with current (temp)
                
                #correct lists
                for list_i in range(len(lists)):
                    #for every list
                    temp_holder = lists[list_i][main_list_i]                   #store current
                    lists[list_i][main_list_i] = lists[list_i][main_list_i-1] #replace current with previous
                    lists[list_i][main_list_i-1] = temp_holder                 #replace previous with current (temp)

                sorted = False
                
    return main_list, lists
    
'''