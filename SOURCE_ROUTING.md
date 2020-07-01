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

## Firewall

See the [firewall](FIREWALL.md) documentation on how to update your firewall
as needed.

## Finishing Touches

There are two problems still left to be resolved with the above solution:

1. Traffic *between* the OpenVPN processes is also sent to the default gateway
   of the `vpn` table, this prevents "client to client" traffic, even if they 
   firewall would allow it;
2. It is not possible to ping the gateway, i.e. the IP address assign to the 
   VPN server `tun` interfaces, as all traffic is sent to the default gateway.

We cannot do this "statically" as the `tun` interfaces do not yet exist when 
the network is brought up. It is also tricky as there is not a really easily 
understood convention of `tun` device numbering.

In order to fix this, a script can be run on OpenVPN server process start. In 
vpn-server-node >= 2.2.2 the `--up` command is automatically added to 
server configuration when a script with the name `/etc/openvpn/up` 
exists. There is no need for a `--down` script as the routing table is 
automatically cleaned up when the `tun` devices disappear.

An possible example script that solves the above two issues is shown below. It
depends on `/usr/bin/ipcalc` and `/usr/sbin/ip` commands. Make sure you modify
the script as necessary for your platform:

    #!/bin/sh
    NETWORK4=$(/usr/bin/ipcalc -n $ifconfig_local $ifconfig_netmask | cut -d '=' -f 2)
    PREFIX4=$(/usr/bin/ipcalc -p $4 $5 | cut -d '=' -f 2)
    NETWORK6=$(/usr/bin/ipcalc -n $ifconfig_ipv6_local/$ifconfig_ipv6_netbits | cut -d '=' -f 2)
    PREFIX6=$ifconfig_ipv6_netbits

    echo /usr/sbin/ip -4 ro add $NETWORK4/$PREFIX4 dev $dev table vpn
    echo /usr/sbin/ip -6 ro add $NETWORK6/$PREFIX6 dev $dev table vpn

    /usr/sbin/ip -4 ro add $NETWORK4/$PREFIX4 dev $dev table vpn
    /usr/sbin/ip -6 ro add $NETWORK6/$PREFIX6 dev $dev table vpn

**NOTE**: make sure the `/etc/openvpn/up` script is made executable, 
i.e. don't forget to do a `chmod 0755 /etc/openvpn/up`!
