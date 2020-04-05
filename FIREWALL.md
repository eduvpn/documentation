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

## Custom Firewall

If you need something more complicated than the included firewall scripts can
accomplish, you can still use the generated firewall as a base or start from
scratch, depending exactly on your use case.

**NOTE**: if you go down this path, make sure you remove 
`vpn-server-node-generate-firewall --install` from your copy of 
`apply_changes.sh`!

You can modify `/etc/sysconfig/iptables` and `/etc/sysconfig/ip6tables` 
manually and restart the firewall:

    $ sudo systemctl restart iptables
    $ sudo systemctl restart ip6tables

### Different Public IP for Different Profile

Assume you have two VPN profiles, one for `employees` and one for 
`admin` and they both use NAT. But now you want to use a different public IP 
address for traffic coming from each of these profiles. If you so far used the 
generated firewall, you'd have something like this in 
`/etc/sysconfig/iptables`:

    *nat
    :PREROUTING ACCEPT [0:0]
    :INPUT ACCEPT [0:0]
    :OUTPUT ACCEPT [0:0]
    :POSTROUTING ACCEPT [0:0]
    -A POSTROUTING --source 10.0.1.0/24 --jump MASQUERADE
    -A POSTROUTING --source 10.0.2.0/24 --jump MASQUERADE
    COMMIT

Here `10.0.1.0/24` is the `employees` profile, and `10.0.2.0/24` is the `admin` 
profile.

You can replace the two `POSTROUTING` rules by these:

    -A POSTROUTING -s 10.0.1.0/24 --jump SNAT --to-source 1.2.3.4
    -A POSTROUTING -s 10.0.2.0/24 --jump SNAT --to-source 1.2.3.5

Where `1.2.3.4` is the first public IPv4 address, and `1.2.3.5` is the second
one. Don't forget to restart the firewall as mentioned above.

### NAT to Multiple IP Addresses

If you have many clients, using NAT with a single IP address may not be 
sufficient. You can solve this like this:

    -A POSTROUTING -s 10.0.1.0/24 --jump SNAT --to-source 1.2.3.4-1.2.3.8

This will use the IP addresses `1.2.3.4` up to including `1.2.3.8` to share
the load over the IPs.

### Reject IPv6 Client Traffic

You cannot fully disable IPv6 in the VPN server, but you can drop all IPv6 
traffic coming from the clients wanting to go out to the Internet.

Modify `/etc/sysconfig/ip6tables` and remove the `*nat` line up to the
first `COMMIT` line before `*filter`. 

Remove all `-A FORWARD` lines in the `*filter` section, except:

    -A FORWARD --jump REJECT --reject-with icmp6-adm-prohibited

To apply:

    $ sudo ip6tables -F -t nat
    $ sudo systemctl restart ip6tables
