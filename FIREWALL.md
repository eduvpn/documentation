---
title: Configuring the Firewall
description: Configure the VPN Firewall
category: documentation
---

By default a very simple firewall is included that allows connections to the
VPN server over the VPN ports, SSH, HTTP and HTTPS.

SSH is not strictly needed, but it is useful to be able to manage your VPN 
server. 

It is smart however to limit the connections to SSH to a list of trusted hosts,
and not have it open for the entire Internet *OR* VPN users.

If you network already filters incoming SSH traffic, a VPN user MAY still be 
able to connect to SSH!

If you want to avoid this, you need to modify the firewall! In order to do this
modify `/etc/vpn-server-node/firewall.php`:

	// Only allow SSH access from 10.0.0.0/8 & fd00::/8
	// Make sure to remove 22 from "dst_port" in above rule
	[
	    'proto' => ['tcp'],
	    'src_net' => [
	        '10.0.0.0/8',
	        'fd00::/8',
	    ],
	    'dst_port' => [
	        22,     // SSH
	    ],
	],

Modify the listed IP addresses here to a range of trusted IP addresses. Don't 
forget to [APPLY](PROFILE_CONFIG.md#apply-changes) the changes!