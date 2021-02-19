---
title: Traceable NAT
description: Make NAT users tracable using a static iptables configuration
category: advanced
author: Jørn Åne de Jong (Uninett)
---

# Traceable NAT

## Introduction

When using NAT, it is hard to identify the user behind an action, because every uses has the same outgoing IP address.
A solution to this could be Netflow, but that requires Netflow to be installed on every eduVPN host, which can be a hassle.

Instead, this document proposes a solution with rudimentary implementation, where every internal IPv4 address
is mapped to a limited range of port numbers for outgoing traffic.  With this, any user can be traced in two ways:

1. Incident reports will typically include the source port number used
2. If Netflow is used outside the eduVPN host, this will log the port number used by the eduVPN server


## How it works

The administrator must run a script that will generate iptables rules for the VPN node.  This can be done at the same time that `vpn-maint-apply-changes` is run.  Afterwards, the firewall must be reloaded, which would cause users' connections inside the tunnel to be reset, so the script only restarts the firewall when it's necessary.

Every time the script is run, it will check if the current iptables rules in /etc/iptables/rules.v4 are identical to the desired rules,
if they are, the script does nothing.  If they are not, it will update the rules in the file and restart the firewall.  When it does this, it will write the rules as a new file and keep the old file so that IP/port mappings can always be retrieved.  The old firewall files have a UNIX timestamp in their filename, so when you must investigate an incident, you can find how the firewall was configured at the time of that incident, and which port number was used by which internal IP address.


## Set up

This is only tested on Debian, and probably won't work on CentOS/Fedora.

Copy the `vpn-generate-natfw.php` file in this repository.

	install -m755 vpn-generate-natfw.php /usr/bin/vpn-generate-natfw

Now you must generate the iptables configuration and save it. If you want to test before you write, run

	vpn-generate-natfw -n

If you are happy with the result, you can write it by running without arguments

	vpn-generate-natfw

If you want to see what other options are available

	vpn-generate-natfw --help

That's all!  If you have any procedure where you run `vpn-server-node-server-config` or `vpn-maint-apply-changes` automatically,
you might consider running `vpn-generate-natfw` at the same time.  Never run `vpn-generate-natfw` with `-f` (force) from cron/systemd timers!


## Tracing an incident

In order to trace a user, you need three bits of information

* Date+time
* IP addresses involved
* Source port number

### 1. Find the firewall configuration that was active when the incident happened.

You need to have the date in UNIX timestamp format. Run

	date +%s -d '2020/12/26 13:37:42'

You will get a number, such as `1608986262`

### 2. Find the matching firewall configuration

Get a list of all firewall configurations

	ls -1 /etc/iptables/

You will see multiple files in the format `rules.v4.1608946501` with different numbers.
You must find the **highest** number that is still lower than the UNIX timestamp.

### 3. Find the internal IP address

Display the firewall rules

	less /etc/iptables/rules.v4.1608946501

You will see a lot of lines such as

	-A POSTROUTING -s 192.168.101.2 -p tcp -j SNAT --to-source 192.0.2.1:65280-65535
	-A POSTROUTING -s 192.168.101.2 -p udp -j SNAT --to-source 192.0.2.1:65280-65535
	-A POSTROUTING -s 192.168.101.3 -p tcp -j SNAT --to-source 192.0.2.1:65024-65279
	-A POSTROUTING -s 192.168.101.3 -p udp -j SNAT --to-source 192.0.2.1:65024-65279
	-A POSTROUTING -s 192.168.101.4 -p tcp -j SNAT --to-source 192.0.2.1:64768-65023
	-A POSTROUTING -s 192.168.101.4 -p udp -j SNAT --to-source 192.0.2.1:64768-65023
	-A POSTROUTING -s 192.168.101.5 -p tcp -j SNAT --to-source 192.0.2.1:64512-64767
	-A POSTROUTING -s 192.168.101.5 -p udp -j SNAT --to-source 192.0.2.1:64512-64767
	-A POSTROUTING -s 192.168.101.6 -p tcp -j SNAT --to-source 192.0.2.1:64256-64511
	-A POSTROUTING -s 192.168.101.6 -p udp -j SNAT --to-source 192.0.2.1:64256-64511

Port ranges are shown at the end of the line. Scroll with the arrow keys or PgUp/PgDown and find the line that matches your source port number.
You have now found the internal IPv4 address that was involved in the incident.  This internal IP address (on the left) can be matched to a user through the eduVPN portal (webinterface).
