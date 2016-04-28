#!/usr/bin/python


# Pyretic libraries
from pyretic.lib.std import *
from pyretic.lib.query import *
from pyretic.lib.corelib import *
################################################
# Translate from
# client -> public address : client -> server
# server -> client : public address -> client
################################################
def Translate(c, s, p):
	cp = match(srcip=c, dstip=p)
	sc = match(srcip=s, dstip=c)
	return ((cp >> modify(dstip=s)) + (sc >> modify(srcip=p)) + (~cp & ~sc))


##################################################################
# Simple round-robin load balancing policy #
##################################################################
class LoadBalancer(DynamicPolicy):
	def __init__(self, Device, Clients, Servers, PublicIP):
		super(LoadBalancer, self).__init__()
		#print("[Load Balancer]: Device ID: %s" %(Device))
		#print("[Load Balancer]: Server addresses: %s %s" %(Servers[0], Servers[1]))
		self.Device = Device
		self.Clients = Clients
		self.Servers = Servers
		self.PublicIP = PublicIP
		self.Index = 0
		# Start a packet query
		self.Query = packets(1, ['srcip'])
		# Handle events using callback function
		self.Query.register_callback(self.LoadBalancingPolicy)
		# Capture packets that arrive at LB and go to Internet
		self.Public_to_Controller = (match(dstip=self.PublicIP, switch=self.Device)>> self.Query)
		self.LB_Policy = None
		self.policy = self.Public_to_Controller

	def UpdatePolicy(self):
		self.policy = self.LB_Policy + self.Public_to_Controller

	def LoadBalancingPolicy(self, pkt):
		Client = pkt['srcip']
		# Be careful not to redirect servers on themselves
		if Client in self.Servers: return
		# Round-robin, per-flow load balancing
		Server = self.NextServer()
		p = Translate(Client, Server, self.PublicIP)
		print("[Load Balancer]: Mapping c:%s to s:%s" % (Client, Server))
		# Apply the modifications
		if self.LB_Policy:
			self.LB_Policy = self.LB_Policy >> p
		else:
			self.LB_Policy = p
		# Update LB policy object
		self.UpdatePolicy()

	# Round-robin
	def NextServer(self):
		Server = self.Servers[self.Index % len(self.Servers)]
		self.Index += 1
		return Server
################################################################################
### Test the LB functionality
################################################################################
def main():
	from pyretic.modules.mac_learner import mac_learner
	from pyretic.examples.Monitor import Monitor
	from pyretic.examples.firewall import firewall_policy
	ARPPkt = match(ethtype=ARP_TYPE)
	Clients = 1
	Servers = 2
	Device_1 = 4
	Device_2 = 3
	PublicIP_1 = IP("10.0.100.1")
	PublicIP_2 = IP("10.0.100.2")
	ClientIPs = [IP("10.0.0.1"), IP("10.0.0.2"), IP("10.0.0.3"), IP("10.0.0.4")]
	ServerIPs_1 = [IP("10.0.0.5"), IP("10.0.0.6")]
	ServerIPs_2 = [IP("10.0.0.7"), IP("10.0.0.8")]
	LB_1 = LoadBalancer(Device_1, ClientIPs, ServerIPs_1, PublicIP_1)
	LB_2 = LoadBalancer(Device_2, ClientIPs, ServerIPs_2, PublicIP_2)
	LB_Monitor_Policy = (
			(ARPPkt >> mac_learner()) +
			( LB_1 >> mac_learner()) +
			( LB_2 >> mac_learner()) +
			Monitor(10)
		)

	return if_(firewall_policy, drop, LB_Monitor_Policy)