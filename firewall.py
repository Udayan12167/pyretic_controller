firewall_policy = (match(srcip='10.0.0.1', dstport=80)|
				   match(srcip='10.0.0.2', dstport=443)|
				   match(srcip='10.0.0.3', dstport=80)|
				   match(srcip='10.0.0.4', dstport=443))