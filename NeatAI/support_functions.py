import classes
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib as mpl
import random as rnd
import numpy as np


#search for connection with given in, out indexes
def search_con_index(genepool, in_index, out_index):
    counter=0
    for con in genepool:
        if con.in_index == in_index and con.out_index == out_index:
            return counter
        counter += 1
    return -1

#print the fenotype of a brain, connection by connection
def print_genepool(fenotype):
    for con in fenotype.genepool:
        print(f"[{con.status}] <> Connection: {con.in_index} -> {con.out_index}: Weight = {con.weight}: Inovation = {con.inov}")
    pass

def combine_fenotypes(dominant_fenotype, recessive_fenotype):
    
    pass

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

def layer_sort(fenotype,node_pos_list=[]):
    
    #extra parameters
    layer_count = 3

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

    #define indexes
    index_last = fenotype.NodeCount - 1
    index_first = fenotype.NOO + fenotype.NOI
    
    #define variable to inform whether anything changed
    change = False
    
    if index_first == index_last:
        return node_pos_list, change
    
    for i in range(index_first, index_last+1):              
        for j in range(index_first, index_last+1):
            cursor = search_con_index(fenotype.genepool, i, j)              #verify every connection between hidden nodes
            
            if cursor != -1 :
                #there's a connection, check for conditions
                conn = fenotype.genepool[cursor]
                   
                #CASE1: nodes are in the same layer
                if node_pos_list[conn.out_index][1] == node_pos_list[conn.in_index][1]:
                    
                    #if the next layer is the output layer, then a new layer must be created
                    #fenotype.NOI index is the first output node
                    if node_pos_list[fenotype.NOI][1] == node_pos_list[conn.out_index][1] + 1:
                        for k in range(fenotype.NOI, fenotype.NOI + fenotype.NOO):          
                            node_pos_list[k][1] += 1            #move output layers by 1
                    
                    #always move the one that is the output node
                    node_pos_list[conn.out_index][1] += 1                       #create additional hidden layer, move affected node up
                    layer_count += 1
                    change = True
                    
                #CASE2: the output node is under the input node
                elif node_pos_list[conn.out_index][1] == node_pos_list[conn.in_index][1]:
                    
                    #if the next layer is the output layer, then a new layer must be created
                    #fenotype.NOI index is the first output node
                    #2 is used since we jump over the hidden layer
                    if node_pos_list[fenotype.NOI][1] == node_pos_list[conn.out_index][1] + 2:
                        for k in range(fenotype.NOI, fenotype.NOI + fenotype.NOO):          
                            node_pos_list[k][1] += 1            #move output layers by 1
                        
                    #always move the one that is the output node
                    node_pos_list[conn.out_index][1] += 2                       #create additional hidden layer, move affected node up
                    layer_count += 1
                    change = True
    
    return node_pos_list, change, layer_count

def compute_output(fenotype,input):
    #sort the genepool by layers
    node_pos_list, change, Number_of_layers = layer_sort(fenotype,[])
    while change:
        node_pos_list, change, Number_of_layers = layer_sort(fenotype,node_pos_list)
        
    #create a mupet fenotype that can be reduced over time
    mupet_fenotype = fenotype
     
    #create a list to store all gene values
    values = np.zeros(fenotype.NodeCount)
    values[0:fenotype.NOI] = input
      
    #for every node, from layer 2 to output layer from left to right, compute the value of the node
    for layer in range(1,Number_of_layers):
        #search for a node in said layer
        for node_index, node in enumerate(node_pos_list):
            if node[1] == layer:
                #compute the value of the node
                #search all connections that lead to the node
                for con_index, con in enumerate(mupet_fenotype.genepool):
                    if con.out_index == node[0]:
                        if con.status == True:
                            values[con.out_index] = con.weight * values[con.in_index] 
                        
                        #REMOVE STUFF TO MAKE ITERATIONS FASTER AS IT GOES
                        #remove connection
                        mupet_fenotype.genepool.pop(con_index)
                        
                #apply activation function
                values[con.out_index] = convert_according_to_AF(values[con.out_index])
                
            #remove node
            node_pos_list.pop(node_index)
                      
    return values

def convert_according_to_AF(input):
    #if method == "sigmoid":
    #    for i in range(0,len(input)):
    input = 1/(1+np.exp(input))

    #elif method == "rectified_liner":
    #    for i in input:
    #output = max(0,input)
    
    return input
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
