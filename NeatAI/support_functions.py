import classes
import networkx as nx
import matplotlib.pyplot as plt

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
        
        if con.in_index not in nodes:
            if con.in_index < fenotype.NOI:    #if input
                spacing_index = 0
            else:
                spacing_index = 1              #if hidden
        
            nodes.update({con.in_index : (nodes_count_per_layer[0],0)})
            nodes_count_per_layer[0] += 1
        if con.out_index not in nodes:
            if con.in_index < fenotype.NOO + fenotype.NOI:    #if output
                spacing_index = 2
            else:
                spacing_index = 1              #if hidden
            
            nodes.update({con.out_index : (nodes_count_per_layer[2],2)})
            nodes_count_per_layer[2] += 1
            
        #add the connection to the graph
        print(f"{con.in_index} -> {con.out_index}")
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

#search for connection with given in, out indexes
def search_con(genepool, in_index, out_index):
    for con in genepool:
        if con.in_index == in_index and con.out_index == out_index:
            return con
    return -1

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
