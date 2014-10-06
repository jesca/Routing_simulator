from sim.api import *
from sim.basics import *

'''
Create your distance vector router in this file.
'''

""" Instructions: 
Write a DVRouter class which inherits from the Entity class. The function that you will need to override
is handle_rx dealing with the following three types of packets (feel free to add more member functions to
DVRouter). """

class DVRouter (Entity):
    def __init__(self):
         # destionations dictionary 
         # {C: port from which packet is sent out to get to C, A: port from which packet is sent out to get to A, ...} 
        self.dests_dic = {}
        # costs dictionary 
        # costs dictionary = least cost paths (yellow highlights)
        self.costs_dic = {}
    
        
    def handle_rx (self, packet, port):
        # Called by framework when the Entity self receives a packet
        #Override Entity's handle_rx

        if isinstance(packet,DiscoveryPacket):
            self.handleDiscovery(packet, port)
        elif isinstance(packet, RoutingUpdate):
            self.handleRoutingUpdate(packet)
        else:
            self.handleData(packet)


    def handleDiscovery(self, dpacket, port):
        #sent from a host
        if dpacket.is_link_up:
            if dpacket.src not in self.dests_dic:
                self.dests_dic[dpacket.src] = port
                #add to costs dictionary
                self.costs_dic[dpacket.src] = (dpacket.latency, self)
        
        for neighbor in self.dests_dic:
                        if not isinstance(neighbor, HostEntity):
                            self.sendRoutingUpdate(self, neighbor, self.dests_dic[neighbor])   
        #link down?

    
    def handleRoutingUpdate(self, rpacket):
        print "update routes for", self
        for destination in rpacket.all_dests():

            new_cost = rpacket.get_distance(destination) + self.costs_dic[rpacket.src][0]
            
            if destination in self.costs_dic:
                if destination is self:
                    self.costs_dic[self] = (0, self)

                if new_cost < (self.costs_dic[destination])[0]:
                    # A    ->2    B    ->8     C
                    # for A: costs[C] = ( 8 + 2 )
                    # Keep: A dictionary { (C: (10, B)) } ; destination = C, distance = (10, B)
                    self.costs_dic[destination] = (new_cost, rpacket.src)
                    #since this is modified, send routing updates to neighboring switches
                    print "changed cost for", self
                    for neighbor in self.dests_dic:
                        if not isinstance(neighbor, HostEntity):
                            self.sendRoutingUpdate(self,neighbor,self.dests_dic[neighbor])
                            print "routing update from", self, "to", neighbor
            else:
                #first time seeing destination; have no shortest path.
                self.costs_dic[destination] = (new_cost, rpacket.src)
                for neighbor in self.dests_dic:
                    if not isinstance(neighbor, HostEntity):
                        self.sendRoutingUpdate(self,neighbor,self.dests_dic[neighbor])
        print ": ", self.costs_dic

    """
    Dests_dic: { neighbor, port}
    Costs_dic: { dest: (cost, neighbor)}
    """
    def handleData(self, data_packet):
        #find the lowest cost route to the src of the data packet using costs dictionary
        #get next neighbor
        lowest_cost_route = (self.costs_dic[data_packet.dst])[1]
        #port to get to least cost route exit()
        if lowest_cost_route == self:
            port = self.dests_dic[data_packet.dst]
        else:
            port = self.dests_dic[lowest_cost_route] 
        self.send(data_packet, port)


    """Helper methods"""
    def sendRoutingUpdate(self, src, dst, port):
        routing_update = RoutingUpdate()
        routing_update.src = src
        routing_update.dst = dst
        for destination in self.costs_dic:
                routing_update.add_destination(destination,self.costs_dic[destination][0])

        self.send(routing_update, port)
