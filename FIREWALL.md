# Firewall

**NOTE**: if you installed your server before the default became _nftables_, 
look [here](FIREWALL_IPTABLES.md) for _iptables_ documentation. We switched
to _nftables_ by default for new installations on 2023-09-08.

**NOTE**: if you are currently using _iptables_, but would like to switch to
_nftables_ you can use this document and "port" any changes you may have made
based on the various sections below. If you can't figure it out, you can always
contact [us](mailto:eduvpn-support@lists.geant.org).

**NOTE**: Debian 11 and Ubuntu 22.04 ship with a version of _nftables_ that is
too old, i.e older than 1.0.3 that added 
[support](https://lwn.net/Articles/896732/) for wildcards in interface sets. 
Therefor you can't use e.g. `iifname { "tun*", "wg0" }` on those OSes. You'll 
have to either use a separate line if you want to use wildcards, or, mention 
the interfaces explicitly as is done in the _nftables_ rules deployed out of 
the box. Of course, if you run on Debian, please deploy on Debian 12, or 
upgrade to Debian 12 first ;-)

A very simple static firewall based on _nftables_ is installed when running the 
deploy scripts. It allows connections to the VPN, SSH, HTTP and HTTPS ports. In 
addition it uses NAT for both IPv4 and IPv6 client traffic.

This document explains how to modify the firewall for common scenarios that
deviate from the default and on how to tailor the VPN configuration for your 
particular set-up. Much more is possible with _nftables_ that is out
of scope of this document. We only collected some common situations below.

For more information on what you can do with _nftables_, see their 
[wiki](https://wiki.nftables.org/).

The default firewall configuration files as installed on new deployments can be 
found here, they may be updated from time to time:

* [Single Server](https://codeberg.org/eduVPN/documentation/src/branch/v3/resources/firewall/nftables.conf)
* Separate Controller/Node
  * [Controller](https://codeberg.org/eduVPN/documentation/src/branch/v3/resources/firewall/controller/nftables.conf)
  * [Node](https://codeberg.org/eduVPN/documentation/src/branch/v3/resources/firewall/node/nftables.conf)

You can of course also use the firewall software of your choice, or fully 
disable the firewall! As our goal was to keep things as simple and easy as 
possible by default.

# Configuration File

You can find the configuration file in the following location:

| OS             | Location                       |
| -------------- | ------------------------------ |
| Debian, Ubuntu | `/etc/nftables.conf`           |
| Fedora, EL     | `/etc/sysconfig/nftables.conf` |

# Manage Firewall

## List

```bash
$ sudo nft list ruleset
```

## Stop

```bash
$ sudo systemctl stop nftables
```

## Start

```bash
$ sudo systemctl start nftables
```

## Restart

```bash
$ sudo systemctl restart nftables
```

## IPv4 vs IPv6

Configuring IPv4 and IPv6 is very similar. Only when IP family specific 
configuration is needed you need to refer to `ip` or `ip6`. You'll see in the
examples below. We'll try to provide always configuration examples for both
IPv4 and IPv6.

## Improving the Defaults

The default firewall works well, but can be improved upon by updating it to 
match your deployment.

## Restricting SSH Access

By default, SSH is allowed from everywhere, *including* the VPN clients. It 
makes sense to restrict this a set of hosts or a "bastion" host.

```
table inet filter {
    chain input {
        ... 

        tcp dport { 22, 1194 } accept
        
        ...
    }
}
```

You can modify it like this:

```
table inet filter {
    chain input {
        ... 

        tcp dport { 1194 } accept
        
        ip saddr { 192.0.2.0/24, 198.51.100.0/24 } tcp dport 22 accept
        ip6 saddr { 2001:db8:1234:5678::1/64 } tcp dport 22 accept

        ...
    }
}
```

## Opening Additional VPN Ports

By default, one port, both for TCP and UDP are open for OpenVPN 
connections:

```
table inet filter {
    chain input {
        ... 

        tcp dport { 22, 1194 } accept
        udp dport { 1194, 51820 } accept
        
        ...
    }
}
```

You can easily add more by using "ranges", e.g.:

```
table inet filter {
    chain input {
        ... 

        tcp dport { 22, 1194-1197 } accept
        udp dport { 1194-1197, 51820 } accept
        
        ...
    }
}
```

Make sure you _also_ enable the additional _tun_ interfaces in the forward 
chain, for example if you have 4 `tun` devices:

```
iifname { "tun0", "tun1", "tun2", "tun3", "wg0" } oifname $EXTERNAL_IF accept
```

On Debian >= 12, Fedora and EL you can also use a wild card:

```
iifname { "tun*", "wg0" } oifname $EXTERNAL_IF accept
```

## NAT to Multiple Public IP Addresses

```
    ...
    
    chain postrouting {
        type nat hook postrouting priority srcnat; policy accept;
        ip saddr { 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16 } oifname $EXTERNAL_IF snat ip to 192.0.2.0/28
        ip6 saddr fc00::/7 oifname $EXTERNAL_IF snat ip6 to 2001:db8:1234:5678::/120
    }
    
    ...
```

See also 
[NAT pooling](https://wiki.nftables.org/wiki-nftables/index.php/Performing_Network_Address_Translation_(NAT)#NAT_pooling).

## NAT to Different Public IP Addresses per Profile

```
    ...

    chain postrouting {
        type nat hook postrouting priority srcnat; policy accept;
        ip saddr 10.0.1.0/24 oifname $EXTERNAL_IF snat ip to 192.0.2.1
        ip saddr 10.0.2.0/24 oifname $EXTERNAL_IF snat ip to 192.0.2.2
        ip saddr 10.0.3.0/24 oifname $EXTERNAL_IF snat ip to 192.0.2.3
        ip6 saddr fd99:1234:5678:9ab0::/64 oifname $EXTERNAL_IF snat ip6 to 2001:db8:1234:5678::
        ip6 saddr fd99:1234:5678:9ab1::/64 oifname $EXTERNAL_IF snat ip6 to 2001:db8:1234:5678::1
        ip6 saddr fd99:1234:5678:9ab2::/64 oifname $EXTERNAL_IF snat ip6 to 2001:db8:1234:5678::2
    }
     
    ...
```

## Allow Client to Client Traffic

```
    ...
    
    chain forward {
        type filter hook forward priority filter; policy drop;
        tcp flags syn tcp option maxseg size set rt mtu
        ct state vmap { invalid : drop, established : accept, related : accept }
        iifname { "tun0", "tun1", "wg0" } oifname { $EXTERNAL_IF, "tun0", "tun1", "wg0" } accept
    }
    
    ...
```

## Reject Forwarding Traffic

```
    ...
    
    chain forward {
        type filter hook forward priority filter; policy drop;
        tcp flags syn tcp option maxseg size set rt mtu
        ct state vmap { invalid : drop, established : accept, related : accept }
        iifname { "tun0", "tun1", "wg0" } oifname $EXTERNAL_IF ip daddr { 10.1.1.0/24, 192.168.1.0/24 } accept
        iifname { "tun0", "tun1", "wg0" } oifname $EXTERNAL_IF ip6 daddr 2001:db8::/32 accept
    }
    
    ...
```

## Reject IPv6 Client Traffic

TBD.

## Public IP Addresses for VPN Clients

### Disabling NAT

You can simply remove the entire `chain postrouting` section.

### Allowing Incoming Traffic

```
    ...
    
    chain forward {
        type filter hook forward priority filter; policy drop;
        tcp flags syn tcp option maxseg size set rt mtu        
        ct state vmap { invalid : drop, established : accept, related : accept }
        iifname { "tun0", "tun1", "wg0" } oifname $EXTERNAL_IF accept
        iifname $EXTERNAL_IF oifname { "tun0", "tun1", "wg0" } accept
    }
    
    ...
```

## TCP MSS Clamping

One rule we did not explain yet is the one that is used for TCP MSS Clamping, 
i.e.:

```
tcp flags syn tcp option maxseg size set rt mtu
```

What this does is rewrite the MSS TCP header to include the maximum MTU of the
path. See the WireGuard [document](WIREGUARD.md#mtu) for more information. If 
you know what you are doing, MTU != MSS! you can also set a specific value, 
e.g.:

```
tcp flags syn tcp option maxseg size set 1324
```
