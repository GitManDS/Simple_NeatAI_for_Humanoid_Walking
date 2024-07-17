import support_functions as sf
import visualizer as vz
import random as rnd
import time
import matplotlib.pyplot as plt 

class population:
    def __init__(self) -> None:
        self.species = []                              #list of all the brains in the species
        self.species.append(species())     #create first species and append to species list     
        
        self.innovation = 1                          #innovation counter     
        pass
    
    def iterate_innovation(self):
        self.innovation += 1
        for specie in self.species:
            for brain in specie.brains:
                brain.inov_counter = self.innovation
        pass

class species:
    def __init__(self) -> None:
        self.brains = [] #list of all the brains in the species              
        pass

    def add_brain(self,brain):
        self.brains.append(brain)
        pass 

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
    
    def mutation_random(self):
        #0 - add connection
        #1 - add node
        #2 - toggle connection
        #3 - update weight
        rnd.seed = time.time()
        mutation = rnd.randint(0,3) 
        
        if mutation == 0:                       #ADD CONNECTION
            
            in_index = 0
            out_index = 0
            
            #stop it from adding a connection that already exists
            #second condition is to emulate a do-while loop
            checks = 0
            while (sf.search_con_index(self.genepool, in_index, out_index) != -1 or in_index == out_index) and checks < 31:
                #input node index
                if rnd.randint(0,1) < 0.5 or self.NOO+self.NOI == self.NodeCount: #if there are no hidden nodes
                    in_index = rnd.randint(0, self.NOI-1)                                   #input nodes for input
                else:
                    in_index = rnd.randint(self.NOO+self.NOI, self.NodeCount-1)     #hidden nodes for input  
            
                out_index = in_index
                #output node index
                while out_index == in_index:
                    out_index = rnd.randint(self.NOI, self.NodeCount-1)
                
                if checks > 30:
                    print("No available nodes without a connection")
                checks += 1
            
            #add connection
            self.mutation_addconnection(in_index, out_index, rnd.uniform(0,1))
            
            #DEBUG
            print(f"Added connection: {in_index} -> {out_index}")
                
        
        if mutation == 1:                       #ADD NODE
            
            #input node index
            if rnd.randint(0,1) < 0.5 or self.NOO+self.NOI == self.NodeCount: #if there are no hidden nodes
                in_index = rnd.randint(0, self.NOI-1)                                   #input nodes for input
            else:
                in_index = rnd.randint(self.NOO+self.NOI, self.NodeCount-1)     #hidden nodes for input  
            
            out_index = in_index
            #output node index
            while out_index == in_index:
                out_index = rnd.randint(self.NOI, self.NodeCount-1)
                
            #add node
            self.mutation_addnode(in_index, out_index, rnd.uniform(0,1))
            
            #DEBUG
            print(f"Added node between {in_index} and {out_index}")
        
        if mutation == 2:                       #TOGGLE CONNECTION
            index = rnd.randint(0, len(self.genepool)-1)
            previous_status = self.genepool[index].status
            #toggle connection
            self.mutation_toggleconnection(index)
            
            #DEBUG
            print(f"Connection {index} toggled from {previous_status} to {not previous_status}")
        
        if mutation == 3:                       #UPDATE WEIGHT
            index = rnd.randint(0, len(self.genepool)-1)
            old_weight = self.genepool[index].weight
            
            #update weight by +/- 20% max
            amplitude = rnd.uniform(-1,1) * 0.2 
            new_weight = old_weight + amplitude * old_weight
            
            #update weight
            self.update_weight(index, new_weight)
            
            #DEBUG
            print(f"Connection {index} weight updated to {new_weight} ({amplitude*100}%)")
    
    #################### INFORMATION ####################
    def observe(self):
        #observe the brain's state
        vz.draw_genepool(self)
        pass
    
    def save_mental_picture(self, path):
        #save the brain's state
        vz.draw_genepool(self)
        plt.savefig(path)
        plt.close()
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