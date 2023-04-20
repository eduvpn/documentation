# Source Routing

**NOTE**: this is a WORK IN PROGRESS!

There are a number of situations to do _source routing_ or _policy routing_.

1. You already have a dedicated NAT router, i.e. CGNAT ("Carrier Grade NAT");
2. You have a (layer 2) connection to the target location from your VPN box 
   where the VPN traffic needs to be sent over, i.e. when the VPN server is
   located outside the network where the traffic needs to go.

These require that you do not send the traffic from the VPN clients over the 
VPN server's default gateway.

Luckily, it is relatively easy to fix. We document this for **CentOS, 
Fedora and Ubuntu**. We created a physical test setup similar to what you see below.


## Test setup

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
          192.168.178.2 (eth0) |                192.168.178.3 |
                        .------------.                     .-----.
                        | VPN Server |-------------------->| NAT |
                        '------------'                     '-----'
                10.10.10.1     192.168.1.100      192.168.1.1
                (wg0/tun0)	   (eth1)
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
3. You installed the VPN server using the deployment script `deploy_<os>.sh`.
4. The network where you route your client traffic over has _static routes_ 
   back to your VPN server:
    - There is an IPv4 static route for `10.10.10.0/24` via `192.168.1.100`;
    - There is an IPv6 static route for `fd00:4242:4242:4242::/64` via 
      `fd00:1010:1010:1010::100`;

## Source Routing CentOS and Fedora

### Routing table

We'll need to add a new routing table in `/etc/iproute2/rt_tables`, e.g.:

```
200     vpn
```

### Routing rules

First we test it manually, before making these rules permanent:

```
$ sudo ip -4 rule add to 10.10.10.0/24 lookup main
$ sudo ip -4 rule add from 10.10.10.0/24 lookup vpn
$ sudo ip -6 rule add to fd00:4242:4242:4242::/64 lookup main
$ sudo ip -6 rule add from fd00:4242:4242:4242::/64 lookup vpn
```

The `to` rules are needed to make sure traffic between VPN clients uses the 
`main` table so traffic between VPN clients remains possible (if allowed by
the firewall).

### Routes

First we test it manually before making these routes permanent:

```
$ sudo ip -4 ro add default via 192.168.1.1 table vpn
$ sudo ip -6 ro add default via fd00:1010:1010:1010::1 table vpn
```

### Making it permanent

```
# echo 'to 10.10.10.0/24 lookup main' >/etc/sysconfig/network-scripts/rule-eth1
# echo 'from 10.10.10.0/24 lookup vpn' >/etc/sysconfig/network-scripts/rule-eth1
# echo 'to fd00:4242:4242:4242::/64 lookup main' >/etc/sysconfig/network-scripts/rule6-eth1
# echo 'from fd00:4242:4242:4242::/64 lookup vpn' >/etc/sysconfig/network-scripts/rule6-eth1
# echo 'default via 192.168.1.1 table vpn' > /etc/sysconfig/network-scripts/route-eth1
# echo 'default via fd00:1010:1010:1010::1 table vpn' > /etc/sysconfig/network-scripts/route6-eth1
```

When you use NetworkManager you need to install the package 
`NetworkManager-dispatcher-routing-rules.noarch`.

## Source Routing Ubuntu

### Routing table

We'll need to add a new routing table in `/etc/iproute2/rt_tables`, e.g.:

```
200     vpn
```

### Routing rules with netplan

We'll need to add the routing in the netplan configuration file `/etc/netplan/<your_filename>.yaml`, e.g.:

```
network:
  version: 2
  ethernets:
    eth0:
      addresses:
        - 192.168.178.2/24
      nameservers:
        addresses:
          - 1.1.1.1
          - 8.8.8.8
        search:
          - domain.xyz
      routes:
        - to: 0.0.0.0/0
          via: 192.168.178.1
      routing-policy:
        - from: 10.10.10.0/24
          table: 200
        - from: fd00:4242:4242:4242::/64
          table: 200
    eth1:
      addresses:
        - 192.168.1.100/24
        - fd00:1010:1010:1010::100/64
      routes:
        - to: default
          via: 192.168.1.1
          table: 200
        - to: default
          via: fd00:1010:1010:1010::1
          table: 200
```

### Apply changes

```
netplan generate && netplan apply
```

## Troubleshooting

It is smart to reboot your system to see if all comes up as expected:

```
$ ip -4 rule show table vpn
32765:	from 10.10.10.0/24 lookup vpn 
$ ip -4 ro show table vpn
default via 192.168.1.1 dev eth1 
$ ip -6 rule show table vpn
32765:	from fd00:4242:4242:4242::/64 lookup vpn 
$ ip -6 ro show table vpn
default via fd00:1010:1010:1010::1 dev eth1 metric 1024 pref medium
```

## Firewall

See the [firewall](FIREWALL.md) documentation on how to update your firewall
as needed.
