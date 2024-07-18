import support_functions as sf
import visualizer as vz
import random as rnd
import time
import matplotlib.pyplot as plt 
import temporary_testing_funcs as ttf
import os

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
            #if it doesn't exist, the same loop precaution as for add_connection must be taken
            if sf.detect_loops(self, critical_index=index_in, current_node_index=index_out, order=5):
                print("[LOOP] NOT ADDING NODE DUE TO LOOP")
                ttf.record_to_text_file("[LOOP] NOT ADDING NODE DUE TO LOOP")
            else:
            #if loop is not a problem
            #simply create 2 connections of the same weight
            #add connections to the new node    
                self.genepool.append(conn_gene(index_in,self.NodeCount,weight,self.inov_counter))
                self.genepool.append(conn_gene(self.NodeCount,index_out,weight,self.inov_counter))

        
        
        #update node count and innovation counter
        self.NodeCount += 1  
        self.inov_counter += 1 
    
    def mutation_random(self):
        #show debug messages
        debug = True
        
        #0 - add connection
        #1 - add node
        #2 - toggle connection
        #3 - update weight
        rnd.seed = time.time()
        mutation = rnd.randint(0,3) 
        
        if mutation == 0:                       #ADD CONNECTION
                  
            #stop it from adding a connection that already exists
            #second condition is to emulate a do-while loop
            checks = 0
            in_index = 0
            out_index = 0
            
            #connection must not exist from A to B or from B to A
            #this means that the connection between 2 nodes must be unidirectional
            #by splitting into 2 while loops, we avoid searching the genepool twice every time
            while (sf.search_con_index(self.genepool, out_index, in_index) != -1 or in_index == out_index) and checks < 31:
                #start out with invalid indexes
                in_index = 0
                out_index = 0
                while (sf.search_con_index(self.genepool, in_index, out_index) != -1 or in_index == out_index) and checks < 31:
                    #if its here, then the connection already exists
                    #get new combination of input/output nodes such that a new connection that doesn't exist is created
                    
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
                        if debug:
                            print("No available nodes without a connection")
                    checks += 1

                #before leaving this loop nest, loop again to check if the same connection exists in the opposite direction
            
            #CHECK FOR LOOPS
            if sf.detect_loops(self, critical_index=in_index, current_node_index=out_index, order=5):
                if debug:
                    print("[LOOP] NOT ADDING CONNECTION DUE TO LOOP")
                    ttf.record_to_text_file("[LOOP] NOT ADDING CONNECTION DUE TO LOOP")
            else:
                #add connection
                self.mutation_addconnection(in_index, out_index, rnd.uniform(0,1))
                
            #DEBUG
            if debug:
                print(f"Added connection: {in_index} -> {out_index}")
                ttf.record_to_text_file(f"Added connection: {in_index} -> {out_index}")
                
        
        if mutation == 1:                       #ADD NODE
            
            #input node index
            if rnd.randint(0,1) < 0.5 or self.NOO+self.NOI == self.NodeCount:   #if there are no hidden nodes
                in_index = rnd.randint(0, self.NOI-1)                           #input nodes for input
            else:
                in_index = rnd.randint(self.NOO+self.NOI, self.NodeCount-1)     #hidden nodes for input  
            
            out_index = in_index
            #output node index
            while out_index == in_index:
                out_index = rnd.randint(self.NOI, self.NodeCount-1)
                
            #add node
            self.mutation_addnode(in_index, out_index, rnd.uniform(0,1))
            
            #DEBUG
            if debug:
                print(f"Added node between {in_index} and {out_index}")
                ttf.record_to_text_file(f"Added node between {in_index} and {out_index}")
        
        if mutation == 2:                       #TOGGLE CONNECTION
            index = rnd.randint(0, len(self.genepool)-1)
            previous_status = self.genepool[index].status
            #toggle connection
            self.mutation_toggleconnection(index)
            
            #DEBUG
            if debug:
                print(f"Connection {index} toggled from {previous_status} to {not previous_status}")
                ttf.record_to_text_file(f"Connection {index} toggled from {previous_status} to {not previous_status}")
        
        if mutation == 3:                       #UPDATE WEIGHT
            index = rnd.randint(0, len(self.genepool)-1)
            old_weight = self.genepool[index].weight
            
            #update weight by +/- 20% max
            amplitude = rnd.uniform(-1,1) * 0.2 
            new_weight = old_weight + amplitude * old_weight
            
            #update weight
            self.update_weight(index, new_weight)
            
            #DEBUG
            if debug:               
                print(f"Connection {index} weight updated to {new_weight} ({amplitude*100}%)")
                ttf.record_to_text_file(f"Connection {index} weight updated to {new_weight} ({amplitude*100}%)")
    
    #################### INFORMATION ####################
    #creates a diagram of the brain
    def observe(self):
        #observe the brain's state
        vz.draw_genepool(self)
        plt.show()
        pass
    
    #saves a diagram of the brain to a path
    def save_mental_picture(self, path):
        #save the brain's state
        vz.draw_genepool(self)
        plt.savefig(path)
        plt.close()
        pass
    
    #prints to console all the connections in the brain
    #includes details
    #in_index, out_index and inov can be used to filter results
    def print(self, in_index = -1 , out_index = -1, inov = -1):
        #first print NOI, NOO and NodeCount
        print(f"<NOI> = {self.NOI}, <NOO> = {self.NOO}, <NodeCount> = {self.NodeCount}")
        
        #then all the connections
        for i,con in enumerate(self.genepool):
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
    def save_mental_connections(self,path):
        #check if file exists
        #if it does, change the path name
        i=1
        while os.path.isfile(path):
            extension_index = path.find(".txt")
            path = path[:extension_index-2] + "_" + str(i) + ".txt"
            i+=1
        
        #open file
        file = open(path, "w")
        
        #write to file
        file.write(f"<NOI> = {self.NOI}, <NOO> = {self.NOO}, <NodeCount> = {self.NodeCount}\n")  
        for con in self.genepool:
            file.write(f"[{con.status}] <> Connection: {con.in_index} -> {con.out_index}: Weight = {con.weight}: Inovation = {con.inov}\n")
        
        #close file
        file.close()      
        pass
      
    #loads connections from a file
    #wipes all previous connections, copies brain from file
    def load_mental_connections(self,path):
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

    #observe function but doesn't draw
    #usefull for custum drawing (i.e. real time drawing)
    def draw(self):
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