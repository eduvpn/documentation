---
title: BGP
description: Use BGP announcements
category: howto
---

# BGP

## Warning

This guide is provided as is.  The eduVPN project provides no support for BGP.


## Introduction

If your network allows it, the IP ranges used by your vpn-server-node can be obtained through BGP.  For this to work, you must know the following:

  * `neighbor` IP-address of your routers (this may differ from the default gateway)
  * `local-address` Your own IP-address
  * `router-id` Your router ID, often this is your IPv4 address - also for IPv6 announces  
  * `local-as` AS number for your VPN setup (obtained from your institutions netops)
  * `peer-as` AS number of your network

The netops must know the IP-address your vpn-server-node is using, and the subnets it will be requesting.
Please note that many BGP implementations will refuse to issue subnets smaller than configured, unless explicitly allowed.
If you need to be able to split your subnet, discuss this with your network operator.

**DO NOT SET THIS UP BEFORE TALKING TO YOUR NETWORK ADMINISTRATOR FIRST**


## Install exaBGP

On CentOS 7, you can do as follows:

	yum install pip3
	pip3 install exabgp

Make a systemd unit file

### /etc/exabgp/exabgp.service

	[Unit]
	Description=exabgp

	[Service]
	Type=simple
	ExecStart=/usr/local/bin/exabgp -e /etc/exabgp/exabgp.env /etc/exabgp/exabgp.conf
	User=nobody
	PermissionsStartOnly=true
	ExecStartPre=/bin/mkdir -p /run/exabgp
	ExecStartPre=-/usr/bin/mkfifo /run/exabgp/exabgp.in /run/exabgp/exabgp.out
	ExecStartPre=/bin/chmod 600 /run/exabgp/exabgp.in /run/exabgp/exabgp.out
	ExecStartPre=/bin/chown nobody:nobody /run/exabgp /run/exabgp/exabgp.in /run/exabgp/exabgp.out

	[Install]
	WantedBy=multi-user.target


## Configuration

Write a configuration file for exabgp; this file documents the routers and the AS numbers used.

Update `router-id`, `peer-as`, `local-as`, `local-address` and `neighbor` statements with your own.

### /etc/exabgp/exabgp.conf

	template {
		neighbor v4 {
			router-id 192.0.2.100;
			peer-as 112;
			local-as 65355;
			group-updates;
			local-address 192.0.2.100;
			family {
				ipv4 unicast;
			}
		}
		neighbor v6 {
			router-id 192.0.2.100;
			peer-as 112;
			local-as 65355;
			group-updates;
			local-address 2001:db8::64;
			family {
				ipv6 unicast;
			}
		}
	}
	neighbor 192.0.2.2 {
		inherit v4;
	}
	neighbor 192.0.2.3 {
		inherit v4;
	}
	neighbor 2001:db8::2 {
		inherit v6;
	}
	neighbor 2001:db8::3 {
		inherit v6;
	}
	process recursor {
		run /usr/bin/python3 -m exabgp healthcheck --config /etc/exabgp/eduvpn.conf;
		encoder text;
	}

### /etc/exabgp/eduvpn.conf

	name = eduvpn
	interval = 5
	fast-interval = 1
	ip = 192.0.2.128/25
	ip = 2001:db8:80::/64
	no-ip-setup
	withdraw-on-down
	command = true
	pid = /var/run/exabgp/eduvpn.pid
	silent

Then start exabgp

	ln -s /etc/exabgp/exabgp.service /etc/systemd/system/exabgp.service
	systemctl enable exabgp.service --now
	
