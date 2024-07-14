import classes
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib as mpl
import random as rnd


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

#create a random mutation:
def random_mutation(fenotype):
    #0 - add connection
    #1 - add node
    #2 - toggle connection
    mutation = rnd.randint(0,2) 
    
    if mutation == 0:                       #ADD CONNECTION
        
        in_index = 0
        out_index = 0
        
        #stop it from adding a connection that already exists
        #second condition is to emulate a do-while loop
        checks = 0
        while search_con_index(fenotype.genepool, in_index, out_index) != -1 or in_index == out_index:
            #input node index
            if rnd.randint(0,1) < 0.5 or fenotype.NOO+fenotype.NOI == fenotype.NodeCount: #if there are no hidden nodes
                in_index = rnd.randint(0, fenotype.NOI-1)                                   #input nodes for input
            else:
                in_index = rnd.randint(fenotype.NOO+fenotype.NOI, fenotype.NodeCount-1)     #hidden nodes for input  
        
            out_index = in_index
            #output node index
            while out_index == in_index:
                out_index = rnd.randint(fenotype.NOI, fenotype.NodeCount-1)
            
            if checks > 30:
                print("No available nodes without a connection")
                return fenotype
            checks += 1
        
        #add connection
        fenotype.mutation_addconnection(in_index, out_index, rnd.uniform(0,1))
        
        #DEBUG
        print(f"Added connection: {in_index} -> {out_index}")
            
    
    if mutation == 1:                       #ADD NODE
        
        #input node index
        if rnd.randint(0,1) < 0.5 or fenotype.NOO+fenotype.NOI == fenotype.NodeCount: #if there are no hidden nodes
            in_index = rnd.randint(0, fenotype.NOI-1)                                   #input nodes for input
        else:
            in_index = rnd.randint(fenotype.NOO+fenotype.NOI, fenotype.NodeCount-1)     #hidden nodes for input  
        
        out_index = in_index
        #output node index
        while out_index == in_index:
            out_index = rnd.randint(fenotype.NOI, fenotype.NodeCount-1)
            
        #add node
        fenotype.mutation_addnode(in_index, out_index, rnd.uniform(0,1))
        
        #DEBUG
        print(f"Added node between {in_index} and {out_index}")
    
    if mutation == 2:                       #TOGGLE CONNECTION
        index = rnd.randint(0, len(fenotype.genepool)-1)
        previous_status = fenotype.genepool[index].status
        #toggle connection
        fenotype.mutation_toggleconnection(index)
        
        #DEBUG
        print(f"Connection {index} toggled from {previous_status} to {not previous_status}")
    
    return fenotype


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
