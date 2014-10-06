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
            self.handleData(packet, port)


    def handleDiscovery(self, dpacket, port):
        """
        print "packet", packet
        print "switch port", port
        print "packet source", packet.src
        print "packet destination", packet.dst
        print "packet trace", packet.trace
        print "latency", packet.latency
        print "switch port count", self.get_port_count()
        """
        """update dictionaries"""
        #add to destination dictionary
        if dpacket.src not in self.dests_dic:
            self.dests_dic[dpacket.src] = port
            #add to costs dictionary
            self.costs_dic[dpacket.src] = (dpacket.latency, self)

        #get updates from all ports before sending routing update
        if isinstance(dpacket.src, DVRouter):
            #send routingupdate dst, src
            routing_update = RoutingUpdate()
            routing_update.src = self
            routing_update.dst = dpacket.src
            for destination in self.costs_dic:
                routing_update.add_destination(destination,self.costs_dic[destination])
            """print "routing update for", dpacket.src, "from", self
            for key in routing_update.all_dests():
                print"key: ", key, "dist:", routing_update.get_distance(key)"""
            self.send(routing_update, port)
        
        #change packet source every time a destinationPacket exits a switch (source no longer host)
        dpacket.src=self
        self.send(dpacket, port, flood=True)
        
        #link down?

    
    def handleRoutingUpdate(self, rpacket):
        send_update = False

        for destination in rpacket.all_dests():
            new_cost = rpacket.get_distance(destination)[0] + self.dests_dic[rpacket.src]
            if destination in self.costs_dic:
                if destination is self:
                    self.costs_dic[self] = (0, self)
                #update cost for destionation if
                if new_cost < (self.costs_dic[destination])[0]:
                    send_update = True
                    # A    ->2    B    ->8     C
                    # for A: costs[C] = ( 8 + 2 )
                    # Keep: A dictionary { (C: (10, B)) } ; destination = C, distance = (10, B)
                    self.costs_dic[destination] = (new_cost, rpacket.src)
            else:
                #first time seeing destination; have no shortest path.
                self.costs_dic[destination] = (new_cost, rpacket.src)
        
        print "routing update for", self
        for key in self.costs_dic:
            print "to get to", key, "use route:", self.costs_dic[key]
    
    def handleData(self, data_packet, port):
        pass
