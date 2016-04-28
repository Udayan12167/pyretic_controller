#!/usr/bin/python

import os

from pyretic.lib.std import *
from pyretic.lib.query import *
from pyretic.lib.corelib import *

class Monitor(DynamicPolicy):
	# Monitor Constructor
	def __init__(self, mInterval):
		super(Monitor, self).__init__()
		self.mInterval = mInterval
		self.ByteQuery = self.ByteCounts()
		#self.PktQuery = self.PacketCounts()
		self.policy = self.ByteQuery

	# Prints counted packets
	def PacketCountPrinter(self, PktCounts):
		print("------------------------------ Packet Counts ------------------------------")
		for k, v in sorted(PktCounts.items()):
			print u'{0}: {1} pkts'.format(k, v)
		print("---------------------------------------------------------------------------")
	
	# Counts packets every second
	def PacketCounts(self):
		q = count_packets(self.mInterval, ['srcip', 'switch', 'protocol'])
		q.register_callback(self.PacketCountPrinter)
		return q

	# Prints counted bytes
	def ByteCountPrinter(self, ByteCounts):
		print("------------------------------- Packet Bytes ------------------------------")
		for k, v in sorted(ByteCounts.items()):
			print u'{0}: {1} bytes'.format(k, v)
		print("---------------------------------------------------------------------------")

	# Counts bytes every second
	def ByteCounts(self):
		q = count_bytes(self.mInterval, ['srcip', 'dstport'])
		q.register_callback(self.ByteCountPrinter)
		return q