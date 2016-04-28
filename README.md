# The Controller
Our project is implemented in Pyretic, which is a Python based language. We worked on a mininet setup with the given topology after installing Pyretic. We implemented four modules: routing, firewall, load balancer and monitoring.

#The Topology
Here is the topology on which our specific controller runs:

![Topology](http://imgur.com/JNqP7NL)

#Routing
The routing for the whole topology is done by a simple mac learning controller application which is included in the pyretic package itself. 

#Load Balancer
The load balancer policy being used is a simple round robin policy. Where each host is allocated to a server based on round robin fashion. In the topology we have two load balancers:

* s3 [10.0.100.1] - Responsible for h5 and h6.
* s4 [10.0.100.2] - Responsible for h7 and h8.

Each load balancer has a list of all the 4 clients(h1,h2,h3,h4). Now we will explain how the load balancer is working by an e.g of s3. Suppose h1 sends an HTTP request to s3 then h1 gets assigned to h5 and subsequent hosts get assigned to h6 and then h5 in a round robin manner.


#Firewall

The firewall has the following rules implemented:

* h1- This can only make HTTPS requests.
* h2- This can only make HTTP requests.
* h3- This can only make HTTPS requests.
* h4- This can only make HTTP requests.

The functioning of the firewall with all the other elements is explained below in the final network policy section.

#Monitoring
Monitoring is done at an interval of 10 seconds. It grabs the bytes transmitted by each distinct Source IP on a particular port in this case 80(HTTP) and 443(HTTPS). The monitor can optionally print the packet count as well.

#Final Network Policy
```python
LB_Monitor_Policy = (
			(ARPPkt >> mac_learner()) +
			( LB_1 >> mac_learner()) +
			( LB_2 >> mac_learner()) +
			Monitor(10)
		)
		
return if_(firewall_policy, drop, LB_Monitor_Policy)
```

Above is the code for the final network policy. Here is the description of the same:

* ARPPkt- Filters all ARP packets.
* LB_1- Policy of the load balancer running on s3.
* LB_2- Policy of the load balancer running on s4.
* Monitor(10)- The monitor capturing all packets at an interval of 10 seconds.

So the first three in the above list run in sequence with a mac learner. Mac learner helps deliver ARP packets and modified load balanced packets to the right destination. Monitor just reads required information and drops all packets. All these 4 run in parallel.

Now for the firewall policy to take effect, the above composed `LB_Monitor_Policy` needs to be given the filtered packets. Thus we drop all the packets that are not required in our access control specification(firewall policy) and the rest of the packets are sent through the load balancer policy.