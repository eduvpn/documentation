# Firewall

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

```bash
$ sudo systemctl restart iptables && sudo systemctl restart ip6tables
```

You can fully disable the firewall as well:

```bash
$ sudo systemctl disable --now iptables && sudo systemctl disable --now ip6tables
```

## Debian

You can find the firewall rules in `/etc/iptables/rules.v4` (IPv4) 
and `/etc/iptables/rules.v6` (IPv6). 

After making changes, you can restart the firewall using:

```bash
$ sudo systemctl restart netfilter-persistent
```

You can fully disable the firewall as well:

```bash
$ sudo systemctl disable --now netfilter-persistent
```

## IPv4 vs IPv6

The configuration of IPv4 and IPv6 firewalls is _almost_ identical. When 
modifying the configuration files you, obviously, have to use the IPv4 style
addresses in the IPv4 firewall, and the IPv6 style addresses in the IPv6 
firewall. In addition, the ICMP type is different, i.e. `icmp` for IPv4 and 
`ipv6-icmp` for IPv6, see the `iptables` and `ip6tables` for examples.

## Improving the Defaults

The default firewall works well, but can be improved upon by updating it to 
match your deployment.

## Restricting SSH Access

By default, SSH is allowed from everywhere, *including* the VPN clients. It 
makes sense to restrict this a set of hosts or a "bastion" host.

The default `INPUT` rule for SSH is:

```
-A INPUT -p tcp -m state --state NEW -m tcp --dport 22 -j ACCEPT
```

You can modify these rules like this:

```
-A INPUT -s 192.0.2.0/24    -p tcp -m state --state NEW -m tcp --dport 22 -j ACCEPT
-A INPUT -s 198.51.100.0/24 -p tcp -m state --state NEW -m tcp --dport 22 -j ACCEPT
```

This allows only SSH connections coming from `192.0.2.0/24` and 
`198.51.100.0/24`. This will also prevent VPN clients from accessing the SSH 
server.

## Opening Additional VPN Ports

By default, one port, both for TCP and UDP are open for OpenVPN 
connections:

```
-A INPUT -p udp -m state --state NEW -m udp --dport 1194 -j ACCEPT
-A INPUT -p tcp -m state --state NEW -m tcp --dport 1194 -j ACCEPT
```

You can easily add more by using "ranges", e.g.

```
-A INPUT -p udp -m state --state NEW -m udp --dport 1194:1197 -j ACCEPT
-A INPUT -p tcp -m state --state NEW -m tcp --dport 1194:1197 -j ACCEPT
```

## NAT to Multiple Public IP Addresses

When using NAT with many clients, it makes sense to "share" the traffic over
multiple public IP addresses.

The default `POSTROUTING` rule in the "NAT" table is:

```
-A POSTROUTING -s 10.0.0.0/8 -o eth0 -j MASQUERADE
-A POSTROUTING -s 172.16.0.0/12 -o eth0 -j MASQUERADE
-A POSTROUTING -s 192.168.0.0/16 -o eth0 -j MASQUERADE
```

Assuming all IP addresses assigned to VPN clients are in the `10.0.0.0/8` 
prefix, you can replace this by for example this line:

```
-A POSTROUTING -s 10.0.0.0/8 -j SNAT --to-source 192.0.2.1-192.0.2.8
```

Make sure you replace `10.0.0.0/8` with your VPN client IP range and 
`192.0.2.1-192.0.2.8` with your public IP addresses. All IP addresses in the 
specified `--to-source` range will be used, specified IPs included.

**NOTE**: for IPv6 the situation is similar, except you'd use the IPv6 range(s) 
and address(es).

## NAT to Different Public IP Addresses per Profile

When using [Multiple Profiles](MULTI_PROFILE.md), you may want to NAT to 
different public IP addresses. You could for example use:

```
-A POSTROUTING -s 10.0.1.0/24 -j SNAT --to-source 192.0.2.1
-A POSTROUTING -s 10.0.2.0/24 -j SNAT --to-source 192.0.2.2
-A POSTROUTING -s 10.0.3.0/24 -j SNAT --to-source 192.0.2.3
```

Make sure you replace the IP ranges specified in `-s` with your VPN client IP 
ranges assigned to the profiles, and the `--to-source` address with your public
IP addresses.

**NOTE**: for IPv6 the situation is similar, except you'd use the IPv6 range(s) 
and address(es).

## Allow Client to Client Traffic

By default, client-to-client traffic is not allowed:

```
-A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
-A FORWARD -i tun+ -o eth0 -j ACCEPT
-A FORWARD -i wg0 -o eth0 -j ACCEPT
```

You can either allow all forwarding, be specific with IP ranges 
(using the `-s` and `-d` flags) or even interfaces.

```
-A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
-A FORWARD -i wg0 -o eth0 -j ACCEPT
-A FORWARD -i wg0 -o wg0 -j ACCEPT
-A FORWARD -i wg0 -o tun+ -j ACCEPT
-A FORWARD -i tun+ -o eth0 -j ACCEPT
-A FORWARD -i tun+ -o tun+ -j ACCEPT
-A FORWARD -i tun+ -o wg0 -j ACCEPT
```

As an example, you have two WireGuard-only profiles on your server with 
`10.0.0.0/24` and `10.100.100.0/24` prefixes where the first allows access to 
the Internet, and the second only allows connectivity between the clients.

```
-A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
-A FORWARD -i wg0 -s 10.0.0.0/24 -o eth0 -j ACCEPT
-A FORWARD -i wg0 -s 10.100.100.0/24 -d 10.100.100.0/24 -i wg0 -o wg0 -j ACCEPT
```

## Reject Forwarding Traffic

Sometimes you want to prevent VPN clients from reaching certain network, or 
allow them to reach only certain networks. For example in the "split tunnel" 
scenario. By default, the firewall will allow all traffic and just route 
traffic as long as the routing for it is configured.

If you use split tunnel, it could make sense to only allow traffic for the 
ranges you also push to the client. As the client can always (manually) 
override the configuration and try to send all traffic over the VPN, this may
need to be restricted.

If you want to only only traffic _to_ `10.1.1.0/24` and `192.168.1.0/24` from 
your VPN clients, you can use the following:

```
-A FORWARD -i tun+ -d 10.1.1.0/24 -j ACCEPT
-A FORWARD -i tun+ -d 192.168.1.0/24 -j ACCEPT
```

**NOTE**: for IPv6 the situation is similar.

## Reject IPv6 Client Traffic

As the VPN server is "dual stack" throughout, it is not possible to "disable" 
IPv6. However, one can easily modify the firewall to prevent all IPv6 traffic
over the VPN to be rejected. By _rejecting_ instead of _dropping_, clients will
quickly fall back to IPv4, there will not be any delays in establishing 
connections. You can simply remove all `FORWARD` rules and replace it with:

```
-A FORWARD -j REJECT --reject-with icmp6-adm-prohibited
```

This will cause all IPv6 to be rejected. The VPN becomes thus effectively 
IPv4 only. You can of course also use it to reject IPv4 traffic to create an
IPv6-only VPN.

## Public IP Addresses for VPN Clients

If you want to use [Public Addresses](PUBLIC_ADDR.md) for the VPN clients, this 
has some implications for the firewall:

1. NAT needs to be disabled;
2. Incoming traffic for VPN clients may need to be blocked.

**NOTE**: it is possible to use NAT for IPv4 and public IP addresses for IPv6,
actually this is recommended over using IPv6 NAT!

### Disabling NAT

By removing all `POSTROUTING` rules from the "NAT" table takes care of 
disabling NAT.

### Allowing Incoming Traffic

The default `FORWARD` rules used are:

```
-A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
-A FORWARD -i tun+ -o eth0 -j ACCEPT
-A FORWARD -i wg0 -o eth0 -j ACCEPT
```

This restrict any traffic initiating on the outside reaching your VPN clients.

If you want to allow traffic from a designated host to the clients, e.g. for 
remote management, you can use the following:

```
-A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
-A FORWARD -i tun+ -o eth0 -j ACCEPT
-A FORWARD -i wg0 -o eth0 -j ACCEPT
-A FORWARD -i eth0 -o tun+ -s 192.168.11.22/32 -j ACCEPT
-A FORWARD -i eth0 -o wg0 -s 192.168.11.22/32 -j ACCEPT
```

**NOTE**: for IPv6 the situation is similar.
