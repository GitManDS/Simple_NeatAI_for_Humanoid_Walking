import networkx as nx
import matplotlib.pyplot as plt
import matplotlib as mpl
import random as rnd
from matplotlib.widgets import Slider
from NeatAI import NeatAI_support_functions as NAIsf


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
def reorganize_hidden_layer_positions(fenotype, node_pos_list, layer_count = 0):
    #debug
    debug = False
    
    #define indexes
    index_last = fenotype.NodeCount - 1
    index_first = fenotype.NOO + fenotype.NOI
    
    #define variable to inform whether anything changed
    change = False
    
    #also extra variable to count layers
    #purelly debug, has no use for the visualizer
    if layer_count == 0:        #first time organizing
        layer_count = 3     #input, hidden, output
    
    if index_first >= index_last:                   #no hidden nodes or only 1 hidden node
        return node_pos_list, change, layer_count
    
    for i in range(index_first, index_last+1):              
        for j in range(index_first, index_last+1):
            cursor = NAIsf.search_con_index(fenotype.genepool, i, j)              #verify every connection between hidden nodes
            
            if cursor != -1 and fenotype.genepool[cursor].status == True:
                #there's an ACTIVE connection , check for conditions
                conn = fenotype.genepool[cursor]
                   
                #CASE1: nodes are in the same layer
                if node_pos_list[conn.out_index][1] == node_pos_list[conn.in_index][1]:
                    
                    #if the next layer is the output layer, then a new layer must be created
                    #fenotype.NOI index is the first output node
                    if node_pos_list[fenotype.NOI][1] == node_pos_list[conn.out_index][1] + 1:
                        for k in range(fenotype.NOI, fenotype.NOI + fenotype.NOO):          
                            node_pos_list[k][1] += 1            #move output layers by 1
                            layer_count += 1                    #update layer count
                    
                    #always move the one that is the output node
                    node_pos_list[conn.out_index][1] += 1                       #create additional hidden layer, move affected node up
                       
                    #update change 
                    change = True
                    
                    ##DEBUG
                    if debug:
                        print(f"[SAME LINE]moved gene {conn.out_index} up from layer {node_pos_list[conn.in_index][1]} to {node_pos_list[conn.out_index][1]} due to gene {conn.in_index}")
                    
                    
                #CASE2: the output node is under the input node
                elif node_pos_list[conn.out_index][1] < node_pos_list[conn.in_index][1]:
                    
                    #get the jump difference (+1 because we are moving the output node up)
                    diff = (node_pos_list[conn.in_index][1] - node_pos_list[conn.out_index][1])+1
                    
                    #if the next layer is the output layer, then a new layer must be created
                    #fenotype.NOI index is the first output node
                    #2 is used since we jump over the hidden layer
                    if node_pos_list[fenotype.NOI][1] == node_pos_list[conn.out_index][1] + diff:
                        for k in range(fenotype.NOI, fenotype.NOI + fenotype.NOO):          
                            node_pos_list[k][1] += 1            #move output layers by 1
                            layer_count += 1                    #update layer count
                        
                    #always move the one that is the output node
                    node_pos_list[conn.out_index][1] += diff                       #create additional hidden layer, move affected node up

                    #update change 
                    change = True
                    
                    ##DEBUG
                    if debug:
                        print(f"[UNDER INPUT] moved gene {conn.out_index} up from layer {node_pos_list[conn.in_index][1]-1} to {node_pos_list[conn.out_index][1]} due to gene {conn.in_index}")
                                
    return node_pos_list, change, layer_count

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

#plot the fenotype of a brain
#with hide direct connections, you can hide the direct connections between input and output nodes
def draw_genepool(fenotype, hide_direct_connections = False):
    
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
        #if the connection is between input and output nodes and the hide_direct_connections is set to True, set the alpha to 0      
        alpha = 1
        if hide_direct_connections and con.in_index < fenotype.NOI and con.out_index >= fenotype.NOI and con.out_index < (fenotype.NOI+fenotype.NOO):
            alpha = 0
        if con.status == True:
            genepool_active_conns.add_edge(con.in_index,con.out_index, color = con.weight, alpha = alpha)
            edges_enabled_colors.append(con.weight)
            #set the alpha
            
        else:
            genepool_disabled_conns.add_edge(con.in_index,con.out_index, alpha = alpha)
            #set the alpha
            
    
    cmap = plt.cm.RdYlGn
    
    #reorganize layers if hidden nodes are connected to eachother
    changed = True
    count_trash = 0
    while changed:
        node_pos_list, changed, count_trash = reorganize_hidden_layer_positions(fenotype, node_pos_list,count_trash)
    node_pos_list = reorganize_node_spacing(node_pos_list)

    #intermediate steps to order the colors
    edges_enabled = genepool_active_conns.edges()
    edges_disabled = genepool_disabled_conns.edges()
    edges_enabled_colors = [genepool_active_conns[u][v]['color'] for u,v in edges_enabled]
    alpha_list_enabled = [genepool_active_conns[u][v]['alpha'] for u,v in edges_enabled]
    alpha_list_disabled = [genepool_disabled_conns[u][v]['alpha'] for u,v in edges_disabled]
    
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
        alpha=alpha_list_enabled,
        width=2
    )

    edges_disabled = nx.draw_networkx_edges(
        genepool_disabled_conns,
        node_pos_list,
        style='dashed',
        edge_color='black',
        alpha=alpha_list_disabled,
        width=2
    )

    labels = nx.draw_networkx_labels(
        genepool_active_conns, 
        node_pos_list,
        font_weight='bold',
        font_size=10, 
        font_color="whitesmoke"
        )

    plt.colorbar(edges_enabled, label = "Weight")
    plt.axis('off')
            
    #plt.pause(0.2)
    #plt.clf()
    
    pass

#will draw all the connections in a sequenced manner
#if more than one fenotype is given, it will draw them all aligned by inovation number
def draw_fenotype_list(fenotype_list, save=False):
    #scalings and other parameters
    scale_x = 1.1       #corrects for scaling
    scale_y = 1.2 
    
    # Setting Plot and Axis variables as subplots()
    # function returns tuple(fig, ax)
    Plot, Axis = plt.subplots(figsize=(10, 6))
    
    # Adjust the bottom size according to the
    # requirement of the user
    plt.subplots_adjust(bottom=0.25)
    
    #first determine if there are any inov numbers that none of the fenotype have
    #if there are, remove the space that would normally be reserved for that inov number
    #as none of the fenotypes will have a connection to fit there
    existant_inov = []
    non_existant_inov = []
    for brain in fenotype_list:
        for con in brain.genepool:
            #note down all the inovation numbers that appear if they haven't been noted down already
            if con.inov not in existant_inov:    
                existant_inov.append(con.inov)
    
    #go through all the inov numbers and check if there's one that doesn't exist
    for i in range(max(existant_inov)+1):
        if i+1 not in existant_inov:
            non_existant_inov.append(i+1)
    
    #before going fenotype by fenotype, create some necessary storage var
    inov_max = max(existant_inov)
    gene_pos_assis = {}       #assistant nodes
    label_assis = {}          #assistant nodes
    Conns_assis = nx.Graph()  #assistant nodes
    
    for j, fenotype in enumerate(fenotype_list):
        #init connections, gene positions and atributes
        #also resets these quantities
        #these have to be specified here since they are reset for each fenotype
        Conns = nx.Graph()
        gene_pos = {} 
        colors = []
        labels = {}

        
        #go through all the connections
        for i, con in enumerate(fenotype.genepool):
            
            #no need for connections whent the nodes represent connections
            #if i+1 < len(fenotype.genepool)-1:  #if next node exists in the genepool
            #    Conns.add_edge(i,i+1)           #create a connection anticipating next node
            Conns.add_node(i)
            
            #check how much spacing needs to be corrected for non_existant_inov_spaces
            non_existant_inov_space_correction = 0
            for k in non_existant_inov:
                if con.inov > k:
                    non_existant_inov_space_correction += 1
                

            gene_pos.update({i : (con.inov*scale_x - non_existant_inov_space_correction,-j*scale_y)})
            
            if con.status == True:
                colors.append("green")
            else:
                colors.append("gray")
            
            labels.update({i : f"<{i}>\n{con.in_index}->{con.out_index}\nW={round(con.weight,4)}\nInov={con.inov}"})
            
            
                
        #draw graph
        nodes = nx.draw_networkx_nodes(
            Conns, 
            gene_pos, 
            node_color=colors,
            node_shape = "s",
            node_size = 5000
        )    
        
        labels = nx.draw_networkx_labels(
            Conns, 
            gene_pos,
            labels=labels
        )
        
        Conns_assis.add_node(j)
        gene_pos_assis.update({j : (-0.5,-j*scale_y)})    
        label_assis.update({j : f"Brain {j}"})
    
    #draw assisting nodes
    nodes_assis = nx.draw_networkx_nodes(
        Conns_assis,
        gene_pos_assis,
        node_color = "orange",
        node_shape = "s",
        node_size = 5000
    )
    labels_assis = nx.draw_networkx_labels(
        Conns_assis, 
        gene_pos_assis,
        labels=label_assis
    )
    
        
    plt.axis('off')
        
    # Choose the Slider color
    slider_color = 'White'
    
    # Set the axis and slider position in the plot
    axis_position = plt.axes([0.2, 0.1, 0.65, 0.03],
                            facecolor = slider_color)
    slider_position_x = Slider(axis_position,
                            'Posx', 0.1, scale_x*inov_max)
    
    ax_y = Plot.add_axes([0.1, 0.25, 0.0225, 0.63])
    
    slider_position_y = Slider(ax_y,
                            'Posy', -scale_y*len(fenotype_list) ,1,orientation="vertical")
    
    ax_zoom = Plot.add_axes([0.2, 0.05, 0.65, 0.03])
    slider_position_zoom = Slider(ax_zoom,
                            'zoom', 0 ,10, valinit=1)
 
    
    # update() function to change the graph when the
    # slider is in use
    def update(val):
        pos_x = slider_position_x.val
        pos_y = slider_position_y.val
        zoom = slider_position_zoom.val
        Axis.axis([(pos_x-1.5)*zoom, (pos_x+1.5)*zoom, (pos_y -1.5)*zoom , (pos_y + 1.5)*zoom])
        Plot.canvas.draw_idle()
    
    # update function called using on_changed() function
    slider_position_x.on_changed(update)
    slider_position_y.on_changed(update)
    slider_position_zoom.on_changed(update)
    
    # Display the plot
    Axis.axis([-1.5, 1.5, -1-j, 1])
    Axis.set_aspect(aspect='equal', adjustable='datalim')
    if save:
        plt.savefig("NeatAI/brain_saves/fenotype.png")
    
    plt.show()
    
    pass

    