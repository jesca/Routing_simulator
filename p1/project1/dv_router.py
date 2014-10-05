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
 
        pass

    	
    def handle_rx (self, packet, port):
        # Called by framework when the Entity self receives a packet
        #Override Entity's handle_rx

        if isinstance(packet,DiscoveryPacket):
        	self.handleDiscovery(packet, port)
        elif isinstance(packet, RoutingUpdate):
        	self.handleRoutingUpdate(packet)
        else:
        	#is a data packet
        	self.handleData(packet, port)


    def handleDiscovery(self, packet, port):
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
    	if packet.src not in self.dests_dic:
    		self.dests_dic[packet.src] = port
    		print "adding", packet.src, "to", self
			#add to costs dictionary
        	self.costs_dic[packet.src] = packet.latency

        if isinstance(packet.src, DVRouter):
			#send routingupdate dst, src
			routing_update = RoutingUpdate()
			routing_update.src = self
			routing_update.dst = packet.src
			for neighbor in self.costs_dic:
				routing_update.add_destination(neighbor,self.costs_dic[neighbor])
				for key in routing_update.all_dests():
					print routing_update.get_distance(key)
			self.send(routing_update, port)
    	
    	#change packet source every time a destinationPacket exits a switch (source no longer host)
    	packet.src=self
    	self.send(packet, port, flood=True)
    	
    	#link down?


    def handleRoutingUpdate(self, packet):
    	# store the data and update it somehow

    def handleData(self, packet, port):
    	print "packet trace", packet.trace
    	print "latency", packet.latency

    	pass


        	
 
