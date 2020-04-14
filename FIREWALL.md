---
title: Configuring the Firewall
description: Configure the VPN Firewall
category: documentation
---

# Introduction

A very simple static firewall based on `iptables` is installed when running the 
deploy scripts. It allows connections to the VPN, SSH, HTTP and HTTPS ports. In 
addition it uses NAT for both IPv4 and IPv6 client traffic.

This document explains how to modify the firewall for common scenarios that
deviate from the default and on how to tailor the VPN configuration for your 
particular set-up. Much more is possible with `iptables` that is out
of scope of this document. We only collected some common situations below.

The _annotated_ default firewall configuration files as installed on new 
deployments can be found here:

* [Single Server](README.md#deployment)
  * [IPv4](resources/firewall/iptables)
  * [IPv6](resources/firewall/ip6tables)

* [Multi Node Server](MULTI_NODE.md)
  * Controller
    * [IPv4](resources/firewall/controller/iptables)
    * [IPv6](resources/firewall/controller/ip6tables)
  * Node
    * [IPv4](resources/firewall/node/iptables)
    * [IPv6](resources/firewall/node/ip6tables)

You can of course also use the firewall software of your choice, or fully 
disable the firewall! As our goal was to keep things as simple and easy as 
possible by default.

## CentOS, Red Hat Enterprise Linux and Fedora

You can find the firewall rules in `/etc/sysconfig/iptables` (IPv4) and 
`/etc/sysconfig/ip6tables` (IPv6). 

After making changes, you can restart the firewall using:

    $ sudo systemctl restart iptables && sudo systemctl restart ip6tables

You can fully disable the firewall if you want to use your own firewall:

    $ sudo systemctl disable --now iptables && sudo systemctl disable --now ip6tables

## Debian

You can find the firewall rules in `/etc/iptables/rules.v4` (IPv4) 
and `/etc/iptables/rules.v6` (IPv6). 

After making changes, you can restart the firewall using:

    $ sudo systemctl restart netfilter-persistent

You can fully disable the firewall if you want to use your own firewall:

    $ sudo systemctl disable --now netfilter-persistent

## IPv4 vs IPv6

The configuration of IPv4 and IPv6 firewalls is _almost_ identical. When 
modifying the configuration files you, obviously, have to use the IPv4 style
addresses in the IPv4 firewall, and the IPv6 style addresses in the IPv6 
firewall. In addition, the ICMP types are slightly different:

|              | IPv4                   | IPv6                   |
| ------------ | ---------------------- | ---------------------- |
| Protocol     | `icmp`                 | `ipv6-icmp`            |
| Error Packet | `icmp-host-prohibited` | `icmp6-adm-prohibited` |

So when modifying the firewall files, make sure you use the correct protocol
and error packet description. You can see this in the default firewall as 
listed above.

# Improving the Defaults

The default firewall works well, but can be improved upon by matching it more
with your system. Two steps I always take:

1. Specifying the exact network interfaces for which to allow "forwarding"
2. Switch to `SNAT` for IPv4 and IPv6 NAT

## Specifying Interfaces

The default `FORWARD` rules used are:

    -A FORWARD -i tun+ ! -o tun+ -j ACCEPT
    -A FORWARD ! -i tun+ -o tun+ -j ACCEPT
    -A FORWARD -j REJECT --reject-with icmp-host-prohibited

This allows all traffic coming from the OpenVPN `tun` devices to all other 
devices that are not also OpenVPN `tun` devices. If you know the external 
interface you can use that instead. For example, if your external interface is
`eth0`, the rules would look like this:

    -A FORWARD -i tun+ -o eth0 -j ACCEPT
    -A FORWARD -i eth0 -o tun+ -j ACCEPT
    -A FORWARD -j REJECT --reject-with icmp-host-prohibited

This allows all traffic to and from the VPN clients. This is fine in case NAT
is used. For [Public IP Addresses](PUBLIC_ADDR.md) we will explain how to 
restrict this further.

## Using SNAT

The default `POSTROUTING` rule in the "NAT" table is:

    -A POSTROUTING -j MASQUERADE

It is recommended to use `SNAT` and be explicit about the IP address to NAT to,
i.e.:

    -A POSTROUTING -s 10.0.0.0/8 -j SNAT --to-source 192.0.2.1

Make sure you replace `10.0.0.0/8` with your VPN client IP range and 
`192.0.2.1` with your public IP address.

**NOTE**: for IPv6 the situation is similar, except you'd use the IPv6 range(s) 
and address(es).

# NAT to Multiple Public IP Addresses

When using NAT with many clients, it makes sense to "share" the traffic over
multiple public IP addresses.

The default `POSTROUTING` rule in the "NAT" table is:

    -A POSTROUTING -j MASQUERADE

You can replace this by:

    -A POSTROUTING -s 10.0.0.0/8 -j SNAT --to-source 192.0.2.1-192.0.2.8

Make sure you replace `10.0.0.0/8` with your VPN client IP range and 
`192.0.2.1-192.0.2.8` with your public IP addresses. All IP addresses in the 
specified `--to-source` range will be used, specified IPs included.

**NOTE**: for IPv6 the situation is similar, except you'd use the IPv6 range(s) 
and address(es).

# Use Different Public IP Address per VPN Profile

When using [Multiple Profiles](MULTI_PROFILE.md), you may want to use a 
different public IP address.

The default `POSTROUTING` rule in the "NAT" table is:

    -A POSTROUTING -j MASQUERADE

You can replace this by:

    -A POSTROUTING -s 10.0.1.0/24 -j SNAT --to-source 192.0.2.1
    -A POSTROUTING -s 10.0.2.0/24 -j SNAT --to-source 192.0.2.2
    -A POSTROUTING -s 10.0.3.0/24 -j SNAT --to-source 192.0.2.3

Make sure you replace the IP ranges specified in `-s` with your VPN client IP 
ranges assigned to the profiles, and the `--to-source` address with your public
IP addresses.

**NOTE**: for IPv6 the situation is similar, except you'd use the IPv6 range(s) 
and address(es).

# Reject IPv6 Client Traffic

As the VPN server is "dual stack" throughout, it is not possible to "disable" 
IPv6. However, one can easily modify the firewall to prevent all IPv6 traffic
over the VPN to be rejected. By _rejecting_ instead of _dropping_, clients will
quickly fall back to IPv4, there will not be any delays in establishing 
connections.

The default `FORWARD` rules used are:

    -A FORWARD -i tun+ ! -o tun+ -j ACCEPT
    -A FORWARD ! -i tun+ -o tun+ -j ACCEPT
    -A FORWARD -j REJECT --reject-with icmp6-adm-prohibited

You can simply remove all of them except the last one:

    -A FORWARD -j REJECT --reject-with icmp6-adm-prohibited

This will cause all IPv6 to be rejected. The VPN becomes thus effectively 
IPv4 only.

# Public IP Addresses

If you want to use [Public Addresses](PUBLIC_ADDR.md), this has some 
implications for the firewall:

1. NAT needs to be disabled;
2. Incoming traffic for VPN clients may need to be blocked.

**NOTE**: it is possible to use NAT with IPv4 and public IP addresses for IPv6,
actually this is recommended!

## Disabling NAT

By removing all `POSTROUTING` rules from the "NAT" table takes care of 
disabling NAT.

## Restricting Incoming Traffic

The default `FORWARD` rules used are:

    -A FORWARD -i tun+ ! -o tun+ -j ACCEPT
    -A FORWARD ! -i tun+ -o tun+ -j ACCEPT
    -A FORWARD -j REJECT --reject-with icmp-host-prohibited

When using public IP addresses this allows traffic from the outside to reach 
the VPN clients. This may not be wanted. Restricting this is easy:

    -A FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT
    -A FORWARD -i tun+ -o eth0 -j ACCEPT
    -A FORWARD -j REJECT --reject-with icmp-host-prohibited

Assuming `eth0` is your external network interface, this allows VPN clients to 
initiate connections and to receive responses, but outside systems cannot 
initiate a connection to the VPN clients.

**NOTE**: for IPv6 the situation is similar.
