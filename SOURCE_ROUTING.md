---
title: Source Routing
description: Setup Source/Policy Routing
category: howto
---

**NOTE**: this is a WORK IN PROGRESS!

There are a number of situations to do _source routing_ or _policy routing_.

1. You already have a dedicated NAT router, i.e. CGNAT ("Carrier Grade NAT");
2. You have a (layer 2) connection to the target location from your VPN box 
   where the VPN traffic needs to be sent over, i.e. when the VPN server is
   located outside the network where the traffic needs to go.

These require that you do not send the traffic from the VPN clients over the 
VPN server's default gateway.

Luckily, it is relatively easy to fix. We document this for CentOS (and 
Fedora). We created a physical test setup similar to what you see below.

```
                           Internet
                               ^
                               |
                          .--------.
                          | Router |
                          '--------'
                               ^ 192.168.178.1
                               |
     192.168.178.10            |
      .--------.          .--------.
      | Client |--------->| Switch |<-------------------------.
      '--------'          '--------'                          |
  VPN IP: 10.10.10.2           ^                              |
                               |                              |
                               |                              |
                 192.168.178.2 |                192.168.178.3 |
                        .------------.                     .-----.
                        | VPN Server |-------------------->| NAT |
                        '------------'                     '-----'
                                 192.168.1.100      192.168.1.1
```

## Assumptions

1. Your VPN clients get IP addresses assigned from the `10.10.10.0/24` and 
   `fd00:4242:4242:4242::/64` pools, the VPN server has `10.10.10.1` and
   `fd00:4242:4242:4242::1` on the `tun0` device;
2. A network connection between the VPN box and the NAT router exists through
   another interface, e.g. `eth1`:
  - the VPN box has the IP addresses `192.168.1.100` and 
    `fd00:1010:1010:1010::100` on this network;
  - the remote NAT router has the IP addresses `192.168.1.1` and 
    `fd00:1010:1010:1010::1` on this network;
3. You installed the VPN server using `deploy_centos.sh` or `deploy_fedora.sh`.
4. The network where you route your client traffic over has _static routes_ 
   back to your VPN server:
  - There is an IPv4 static route for `10.10.10.0/24` via `192.168.1.100`;
  - There is an IPv6 static route for `fd00:4242:4242:4242::/64` via 
    `fd00:1010:1010:1010::100`;

## Source Routing

We'll need to add a new routing table in `/etc/iproute2/rt_tables`, e.g.:

    200     vpn

### Rules

First we test it manually, before making these rules permanent:

    $ sudo ip -4 rule add from 10.10.10.0/24 lookup vpn
    $ sudo ip -6 rule add from fd00:4242:4242:4242::/64 lookup vpn

### Routes

First we test it manually before making these routes permanent:

    $ sudo ip -4 ro add default via 192.168.1.1 table vpn
    $ sudo ip -6 ro add default via fd00:1010:1010:1010::1 table vpn

### Making it permanent

    # echo 'from 10.10.10.0/24 lookup vpn' >/etc/sysconfig/network-scripts/rule-eth1
    # echo 'from fd00:4242:4242:4242::/64 lookup vpn' >/etc/sysconfig/network-scripts/rule6-eth1
    # echo 'default via 192.168.1.1 table vpn' > /etc/sysconfig/network-scripts/route-eth1
    # echo 'default via fd00:1010:1010:1010::1 table vpn' > /etc/sysconfig/network-scripts/route6-eth1

When you use NetworkManager you need to install the package 
`NetworkManager-dispatcher-routing-rules.noarch`.

It is smart to reboot your system to see if all comes up as expected:

    $ ip -4 rule show table vpn
    32765:	from 10.10.10.0/24 lookup vpn 
    $ ip -4 ro show table vpn
    default via 192.168.1.1 dev eth1 
    $ ip -6 rule show table vpn
    32765:	from fd00:4242:4242:4242::/64 lookup vpn 
    $ ip -6 ro show table vpn
    default via fd00:1010:1010:1010::1 dev eth1 metric 1024 pref medium

## Disable NAT

In order to disable NAT on the VPN box, you can modify the included firewall 
by editing `/etc/vpn-server-node/firewall.php` and removing the content of 
`natRules`.

Install the new firewall rules:

    $ sudo vpn-server-node-generate-firewall --install

It turns out that a "restart" of `iptables` and `ip6tables` does not (always?) 
flush the NAT table. Just to make sure:

    $ sudo systemctl stop iptables
    $ sudo systemctl stop ip6tables
    $ sudo iptables -F 
    $ sudo iptables -F -t nat
    $ sudo ip6tables -F 
    $ sudo ip6tables -F -t nat
    $ sudo systemctl start iptables
    $ sudo systemctl start ip6tables

**NOTE**: this still leaves behind some `FORWARD` filtering. Unfortunately the
firewall tool is not able to generate files without `FORWARD` filtering. Feel 
free to stop using the tool and directly modify the firewall files in 
`/etc/sysconfig/iptables` and `/etc/sysconfig/ip6tables`. Of course you can
also fully remove the firewall by removing the `iptables-services` package and
rebooting.

## Issues

It is impossible to `ping` the OpenVPN gateway address from a VPN client, the 
routing will actually work. In the example above it is impossible to ping
`10.10.10.1` from the VPN client. I don't know how to fix this at this time...
