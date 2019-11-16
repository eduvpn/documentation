---
title: Configuring the Firewall
description: Configure the VPN Firewall
category: documentation
---

A simple firewall is included that only allows connections to the VPN, SSH, 
HTTP and HTTPS ports. It also prevents external
systems from contacting your VPN clients.

The firewall is configured through `/etc/vpn-server-node/firewall.php`.

## Host Firewall

SSH access is not strictly needed, but it is useful to be able to manage your 
VPN server :-) 

It is smart however to limit the connections to SSH to a list of trusted hosts,
and not have it open for the entire Internet *OR* your VPN users.

If your network already filters incoming SSH traffic, a VPN user MAY still be 
able to connect to SSH!

If you want to avoid this, you need to make some modifications:

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

### Open a Port 

To simply open a port, in this case `12345` for both TCP and UDP, add this:

	[
		'proto' => ['tcp', 'udp'],
		'dst_port' => [12345]
	]

To open a port only for certain IP ranges:

    [
        'proto' => ['tcp', 'udp'],
        'src_net' => ['10.0.0.0/8', 'fd00::/8'],
        'dst_port' => [53],
    ],	

### NAT

You can enable/disable NAT for certain profiles:

    // NAT
    'natRules' => [
        // profile "internet"
        'internet' => [
            'enableNat' => ['IPv4', 'IPv6']
        ],
    ],
	
This enables NAT for the `internet` profile for both IPv4 and IPv6. You can 
modify this if you switch to [Public Addresses](PUBLIC_ADDR.md).

## VPN Client Firewall

The VPN client firewall simply prevents any connection *initiation* from the 
Internet preventing clients that have open services to have them exposed to 
the Internet. Of course, when NAT is used (the default) there is already *some* 
protection against it. But when switching to [Public Addresses](PUBLIC_ADDR.md) 
this is a different story.

## Apply Firewall

To apply the changes you make to the firewall, run the `apply_changes.sh` 
script from this repository on your VPN server.