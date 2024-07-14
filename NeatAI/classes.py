import support_functions as sf
import visualizer as vz

class brain_fenotype:
    def __init__(self,NOI,NOO):
        #initiliaze the brain with the minimum number of connections/nodes
        self.NOI = NOI                #number of input nodes
        self.NOO = NOO                #number of output nodes
        self.NodeCount = NOI + NOO    #total number of nodes
        
        self.genepool = []            #list of all the connections in the brain
        self.inov_counter = 1
        for i in range(NOO):
            for j in range(NOI): #for each output node, connect it to each input node
                self.genepool.append(conn_gene(j,i+NOI,1,self.inov_counter)) #add the connection to the genepool    
                self.inov_counter += 1 #increment the innovation number
        pass
    
    def update_weight(self, index_con, new_weight, index_in=0, index_out=0):
        
        #search for a connection by the node indexes
        if index_con == -1:
            index_con = sf.search_con(self.genepool, index_in, index_out)
            if index_con == -1:
                exit("Connection not found")
        
        self.genepool[index_con].weight = new_weight                 
        pass
    
    #################### MUTATIONS ####################
    
    def mutation_addconnection(self, in_index, out_index, weight):       
        #add a connection to the brain
        self.genepool.append(conn_gene(in_index,out_index,weight, self.inov_counter))
        
        #update counter
        self.inov_counter += 1
        pass
    
    def mutation_toggleconnection(self, index):
        #toggle the status of a connection
        self.genepool[index].Toggle()
        
        #update counter
        self.inov_counter += 1
        pass
    
    def mutation_addnode(self,index_in,index_out,weight):
        #search for the connection
        index_con = sf.search_con_index(self.genepool, index_in, index_out)
        
        #add a new node
        #if the connection exists, it must be disabled
        if self.genepool[index_con].status == True and index_con != -1:
            self.genepool[index_con].Toggle()
            
            #also the connection must be split into two and one of them must inherit the old weight value
            #add connections to the new node
            self.genepool.append(conn_gene(index_in,self.NodeCount,weight,self.inov_counter))
            self.genepool.append(conn_gene(self.NodeCount,index_out,self.genepool[index_con].weight, self.inov_counter))
        else: 
            #if it doesn't exist, simply create 2 connections of the same weight
            #add connections to the new node
            self.genepool.append(conn_gene(index_in,self.NodeCount,weight,self.inov_counter))
            self.genepool.append(conn_gene(self.NodeCount,index_out,weight,self.inov_counter))

        
        
        #update node count and innovation counter
        self.NodeCount += 1  
        self.inov_counter += 1 
    
    
    #################### INFORMATION ####################
    def observe(self):
        #observe the brain's state
        vz.draw_genepool(self)
        pass
    
    def print(self):
        #print the brain's state
        sf.print_genepool(self)
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