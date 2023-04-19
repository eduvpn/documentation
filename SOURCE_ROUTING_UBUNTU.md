# Source Routing Ubuntu

**COPY FROM**: [SOURCE_ROUTING](SOURCE_ROUTING.md)

**NOTE**: this is a WORK IN PROGRESS!

There are a number of situations to do _source routing_ or _policy routing_.

1. You already have a dedicated NAT router, i.e. CGNAT ("Carrier Grade NAT");
2. You have a (layer 2) connection to the target location from your VPN box 
   where the VPN traffic needs to be sent over, i.e. when the VPN server is
   located outside the network where the traffic needs to go.

These require that you do not send the traffic from the VPN clients over the 
VPN server's default gateway.

In this example it shows your how to configure it on Ubuntu.

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
         192.168.178.2 (ens33) |                192.168.178.3 |
                        .------------.                     .-----.
                        | VPN Server |-------------------->| NAT |
                        '------------'                     '-----'
                10.10.10.1     192.168.1.100      192.168.1.1
				(tun0)		   (ens35)
```

## Assumptions

1. Your VPN clients get IP addresses assigned from the `10.10.10.0/24` and 
   `fd00:4242:4242:4242::/64` pools, the VPN server has `10.10.10.1` and
   `fd00:4242:4242:4242::1` on the `tun0` device;
2. A network connection between the VPN box and the NAT router exists through
   another interface, e.g. `ens35`:
    - the VPN box has the IP addresses `192.168.1.100` and 
      `fd00:1010:1010:1010::100` on this network;
    - the remote NAT router has the IP addresses `192.168.1.1` and 
      `fd00:1010:1010:1010::1` on this network;
3. You installed the VPN server using `deploy_debian.sh`.
4. The network where you route your client traffic over has _static routes_ 
   back to your VPN server:
    - There is an IPv4 static route for `10.10.10.0/24` via `192.168.1.100`;
    - There is an IPv6 static route for `fd00:4242:4242:4242::/64` via 
      `fd00:1010:1010:1010::100`;

## Source Routing

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
    ens33:
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
    ens35:
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

It is smart to reboot your system to see if all comes up as expected:

```
$ ip -4 rule show table vpn
32765:	from 10.10.10.0/24 lookup vpn proto static
$ ip -4 ro show table vpn
default via 192.168.1.1 dev ens35 proto static 
$ ip -6 rule show table vpn
32765:	from fd00:4242:4242:4242::/64 lookup vpn proto static
$ ip -6 ro show table vpn
default via fd00:1010:1010:1010::1 dev ens35 metric 1024 pref medium
```

## Firewall

See the [firewall](FIREWALL.md) documentation on how to update your firewall
as needed.
