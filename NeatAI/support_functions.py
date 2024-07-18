import classes
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib as mpl
import random as rnd
import numpy as np
import visualizer as vz
    

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
    
    pass

#compares 2 fenotypes for disjoint and excess genes
#also measure the average connection weight difference
#returns the compatibility distance
def compare_fenotypes(fenotype1,fenotype2):
    #Weights
    #delta = c1 *  excess/gene_larger_genome + c2 * disjoint/gene_bigger_genome + c3 * AWD
    c1 = 1.5
    c2 = 1
    c3 = 0.4
    
    #counters
    disjoint_counter = 0
    excess_counter = 0
    weight_difference = 0
     
    #see which one starts with the lower inovation number
    if fenotype1.genepool[0].inov < fenotype2.genepool[0].inov:
        older_fenotype = fenotype1
        newer_fenotype = fenotype2
    else:
        older_fenotype = fenotype2
        newer_fenotype = fenotype1
        
    #see which one is the smaller one
    if len(fenotype1.genepool) < len(fenotype2.genepool):   
        smaller_fenotype = fenotype1
        bigger_fenotype = fenotype2
    else:
        smaller_fenotype = fenotype2
        bigger_fenotype = fenotype1
    
    for inov_cursor in range(0,len(smaller_fenotype.genepool)):
        if older_fenotype.genepool[inov_cursor].inov != newer_fenotype.genepool[inov_cursor].inov:
            disjoint_counter += 1
        else:
            weight_difference += abs(older_fenotype.genepool[inov_cursor].weight - newer_fenotype.genepool[inov_cursor].weight)
    
    AWD = weight_difference/(inov_cursor+1)
    
    if inov_cursor != len(smaller_fenotype.genepool)-1:
        excess_counter = len(bigger_fenotype.genepool[inov_cursor:])
    
    #calculate delta (compatibility distance)
    d = c1 * excess_counter/len(bigger_fenotype.genepool) + c2 * disjoint_counter/len(bigger_fenotype.genepool) + c3 * AWD
    
    return d

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
        for i in range(fenotype.NOI + fenotype.NOO, fenotype.NodeCount):
            node_pos_list.append([i,1])         #hidden nodes
            
    if layer_count == 0:   #first time initializing
        layer_count = 3     #input, hidden, output

    #call existing function from visualizer
    node_pos_list, change, layer_count = vz.reorganize_hidden_layer_positions(fenotype, node_pos_list,layer_count)
    
    return node_pos_list, change, layer_count

#from a given fenotype, compute the output of the brain
#given the input
def compute_output(fenotype,input):
    #sort the genepool by layers
    node_pos_list, change, Number_of_layers = layer_sort(fenotype,[],0)
    while change:
        node_pos_list, change, Number_of_layers = layer_sort(fenotype,node_pos_list,Number_of_layers)
        
    #create a mupet fenotype that can be reduced over time
    mupet_fenotype = fenotype
     
    #create a list to store all gene values
    values = np.zeros(fenotype.NodeCount)
    values[0:fenotype.NOI] = input
      
    #for every node, from layer 2 to output layer from left to right, compute the value of the node
    for layer in range(1,Number_of_layers):
        #search for a node in said layer
        node_index = 0
        len_node_list = len(node_pos_list)
        while node_index < len_node_list:
            #found a node in the currently sought layer
            if node_pos_list[node_index][1] == layer:
                #compute the value of the node
                #search all connections that lead to the node
                con_index = 0
                len_con_list = len(mupet_fenotype.genepool)
                while con_index < len_con_list:
                    #found a connection that leads to the node
                    #adding up value
                    con = mupet_fenotype.genepool[con_index]    #this helps with readability
                    
                    if con.out_index == node_pos_list[node_index][0]:
                        if con.status == True:
                            values[con.out_index] = con.weight * values[con.in_index] 
                        
                        #REMOVE STUFF TO MAKE ITERATIONS FASTER AS IT GOES
                        #remove connection and update pool size
                        mupet_fenotype.genepool.pop(con_index)
                        len_con_list -= 1
                    else:
                        #search next connection
                        con_index += 1
                        
                #apply activation function
                values[con.out_index] = convert_according_to_AF(values[con.out_index])
                
                #remove node and update gene layer list size
                node_pos_list.pop(node_index)
                len_node_list -= 1
            else:
                #search next node
                node_index += 1
                      
    return values

#activation function
def convert_according_to_AF(input):
    #if method == "sigmoid":
    #    for i in range(0,len(input)):
    input = 1/(1+np.exp(input))

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
        

''' OLD FUNCTIONS, DEPRECATED
#create visualization of the genepool
def visualize_genepool(fenotype):
    #initialize the graph
    feno_view = nx.Graph()
    
    #get list of existing nodes
    nodes = {}
    nodes_count_per_layer = [0.5,0,0] #input, hidden, output
    
    #prepare color map
    color_map = []
    
    #go through every connection
    for con in fenotype.genepool:                   
        #if node (in or out) doesn't exist in the graph, add it
        #this isn't redundant since even though graph.add_edge does this automatically, it doesnt lign them up
        
        #Check the input node
        if con.in_index not in nodes:
            if con.in_index < fenotype.NOI:                   #if input
                spacing_index = 0
            else:
                spacing_index = 1                             #if hidden
        
            nodes.update({con.in_index : (nodes_count_per_layer[spacing_index],spacing_index)})
            nodes_count_per_layer[spacing_index] += 1
            
        #Check the output node
        if con.out_index not in nodes:
            if con.out_index < fenotype.NOO + fenotype.NOI:    #if output
                spacing_index = 2
            else:
                spacing_index = 1                             #if hidden
            
            nodes.update({con.out_index : (nodes_count_per_layer[spacing_index],spacing_index)})
            nodes_count_per_layer[spacing_index] += 1
            
        #add the connection to the graph
        print(f"{con.in_index} -> {con.out_index}")                             #debug
        feno_view.add_edge(con.in_index,con.out_index,weight=con.weight)        
        
        #define colors according to strength of the connection
        color_map.append(color_gradient(fenotype.genepool, con.weight))

    nx.draw(feno_view, nodes, 
            with_labels=True, 
            font_weight='bold',
            edge_color=color_map, 
            node_color = 'black',
            font_color = 'white')
    
    plt.show()
    pass

#returns the color of a connection based on the weight value for a given color scale
def color_gradient(genepool,weight):
    #2 extremes of the color scale
    #red-blue color scal
     
    #find max weight value
    max_weight = 0
    for con in genepool:
        if con.weight > max_weight:
            max_weight = con.weight
            
    #interpolate
    f = weight/max_weight
    
    return (1*f,0,1*(1-f)) #return the color

'''
