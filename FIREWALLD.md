---
title: Configuring firewalld
description: Using firewalld for simple IPv4/IPv6 NAT VPN provider
---

If all you need is a simple VPN server that uses NAT to provide Internet access
to the clients, it is easy to use [firewalld](https://firewalld.org/).

## Installation

Install firewalld, if not already installed:

    $ sudo yum -y install firewalld
    $ sudo systemctl enable --now firewalld

## Configuration

### Zone

Put your external interface, e.g. `eth0` in the `external` zone, which enables
NAT. If you are using 
[NetworkManager](https://wiki.gnome.org/Projects/NetworkManager/) on your 
server and the interface is managed by NetworkManager:

    $ sudo firewall-cmd --zone=external --add-interface=eth0 --permanent

If you are NOT using NetworkManager, simple add `ZONE=external` to 
`/etc/sysconfig/network-scripts/ifcfg-eth0`.

To make sure everything works out, it is best to reboot and then verify if
the zone assignment worked out:

    $ firewall-cmd --get-zone-of-interface=eth0
    external
    $

### Services / Ports

Open the relevant ports for "runtime", i.e. do not (yet) make them permanent:

    $ sudo firewall-cmd --zone=external --add-service=http
    $ sudo firewall-cmd --zone=external --add-service=https 
    $ sudo firewall-cmd --zone=external --add-service=openvpn
    $ sudo firewall-cmd --zone=external --add-port=1194/tcp

If everything works, i.e., you can connect to the VPN and get traffic through
the VPN, go and make these rules permanent:

    $ firewall-cmd --runtime-to-permanent

### IPv6

When you host uses "dynamic" IPv6 addresses, i.e. through 
"Router Advertisements" (RA), IPv6 forwarding will NOT work. This is because
enabling IPv6 forwarding disables listening for RAs. There are two things you 
can do, you need to do one of them:

1. switch to a fixed IPv6 address on your server;
2. modify a `sysctl` setting on your system.

We assume you know how to do the first thing, the second thing requires adding
a line to `/etc/sysctl.conf`:

    net.ipv6.conf.eth0.accept_ra=2

Where `eth0` is your external interface. After you did that, "apply" it:

    $ sudo sysctl --system
