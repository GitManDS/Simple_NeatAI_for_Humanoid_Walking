import networkx as nx
import matplotlib.pyplot as plt
import matplotlib as mpl
import random as rnd
import support_functions as sf



#plot the fenotype of a brain
def draw_genepool(fenotype):
    
    genepool_active_conns = nx.Graph()
    genepool_disabled_conns = nx.Graph()
    
    #initialize position counter and other storage variables
    nodes_count_per_layer = [0.5,0,0]   #input, hidden, output
    edges_enabled_colors = []
    node_pos_list = {}
    
    #go through every connection
    for con in fenotype.genepool:
        
        #check if input node exists in diagramn, create and position it otherwise
        if con.in_index not in node_pos_list:
            new_node, nodes_count_per_layer = create_node(con.in_index, fenotype, nodes_count_per_layer)
            node_pos_list.update(new_node)
        
        #check if output node exists in diagramn, create and position it otherwise
        if con.out_index not in node_pos_list:
            new_node, nodes_count_per_layer = create_node(con.out_index, fenotype, nodes_count_per_layer)
            node_pos_list.update(new_node)
        
        #add the connection to the graph and manage colors/labels
        if con.status == True:
            genepool_active_conns.add_edge(con.in_index,con.out_index, color = con.weight)
            edges_enabled_colors.append(con.weight)
        else:
            genepool_disabled_conns.add_edge(con.in_index,con.out_index)
    
    cmap = plt.cm.viridis
    
    #reorganize layers if hidden nodes are connected to eachother
    changed = True
    while changed:
        node_pos_list, changed = reorganize_hidden_layer_positions(fenotype, node_pos_list)
    node_pos_list = reorganize_node_spacing(node_pos_list)

    #intermediate steps to order the colors
    edges = genepool_active_conns.edges()
    edges_enabled_colors = [genepool_active_conns[u][v]['color'] for u,v in edges]
    
    #draw graphs
    
    nodes_enabled = nx.draw_networkx_nodes(
        genepool_active_conns, 
        node_pos_list, 
        node_color="black")
    
    edges_enabled = nx.draw_networkx_edges(
        genepool_active_conns,
        node_pos_list,
        edge_color=edges_enabled_colors,
        edge_cmap=cmap,
        width=2
    )
    
    edges_disabled = nx.draw_networkx_edges(
        genepool_disabled_conns,
        node_pos_list,
        style='dashed',
        edge_color='black',
        width=2
    )
    
    labels = nx.draw_networkx_labels(
        genepool_active_conns, 
        node_pos_list,
        font_weight='bold',
        font_size=10, 
        font_color="whitesmoke"
        )

    plt.colorbar(edges_enabled)
    plt.axis('off')
    
    pass

#support function for visualizing the genepool
#creates and positions the nodes in the graph
def create_node(index, fenotype ,nodes_count_per_layer):
                 
    #if node doesn't exist in the graph, add it
    #this isn't redundant since even though graph.add_edge does this automatically, it doesnt align them up
    
    if index < fenotype.NOO + fenotype.NOI:    
        if index < fenotype.NOI:
            layer_index = 0                   #if input node
        else:
            layer_index = 2                       #if output node
    else:
            layer_index = 1                       #if hidden node
    
    node = {index : [nodes_count_per_layer[layer_index],layer_index]}
    nodes_count_per_layer[layer_index] += 1
            
    return node, nodes_count_per_layer


#checks if there are hidden nodes with connections to eachother
def reorganize_hidden_layer_positions(fenotype, node_pos_list):
    
    #define indexes
    index_last = fenotype.NodeCount - 1
    index_first = fenotype.NOO + fenotype.NOI
    
    #define variable to inform whether anything changed
    change = False
    
    if index_first == index_last:
        return node_pos_list, change
    
    for i in range(index_first, index_last+1):              
        for j in range(index_first, index_last+1):
            cursor = sf.search_con_index(fenotype.genepool, i, j)              #verify every connection between hidden nodes
            
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

                    change = True
    
    return node_pos_list, change

#counts how many nodes are in each layer   
#reorganizes each layer 
def reorganize_node_spacing(node_pos_list): 
    layers = {} #will keep a record of the current number of nodes in each layer    
    
    for node in node_pos_list:
        if node_pos_list[node][1] not in layers:
            node_pos_list[node][0] = 0                      #position node
            layers.update({node_pos_list[node][1]:1})       #update layer count with a new layer
        else:
            node_pos_list[node][0] = layers[node_pos_list[node][1]]     #position node
            layers[node_pos_list[node][1]] += 1                         #update layer count
    
    #center everything
    for node in node_pos_list:
        node_pos_list[node][0] -= (layers[node_pos_list[node][1]]-1)/2
    
    return node_pos_list  

