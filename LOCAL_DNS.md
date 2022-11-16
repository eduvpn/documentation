---
title: Local DNS
description: Run Local DNS Resolver on VPN server
category: advanced
---

New VPN server installations, performed using `deploy_${DIST}.sh`, will use the 
the public DNS service offered by [Quad9](https://quad9.net/) by default.

It is possible to run your own local DNS resolver for the VPN clients. This has 
a number of benefits:

- Ability to apply filters to e.g. block known malware domains;
- The upstream DNS is unreliable, sells your query data or is slow;
- You do not want to use the "public DNS" services as offered by Quad9, 
  Cloudflare or Google.

Running your own DNS resolver can also be a good idea if no upstream DNS server 
is provided by your ISP.

**NOTE**: if your organization has a (trusted) DNS service you SHOULD probably
use that one! See [Profile Config](PROFILE_CONFIG.md), look for the 
`dnsServerList` option.

# Configuration

Setting a local recursive DNS server takes a few steps:

1. Install a recursive DNS server, we'll use 
   [Unbound](https://nlnetlabs.nl/projects/unbound/about/) here;
2. Configure the DNS server to allow the VPN clients to use it for recursive
   queries;
3. Configure the VPN firewall to allow VPN clients to access the local DNS 
   server;
4. Make the VPN profiles use the "local DNS".

## Install Unbound

### Fedora

```
$ sudo dnf -y install unbound
```

### Debian 

```
$ sudo apt -y install unbound
```

## Configure Unbound

You need to change the Unbound configuration. You can add the following file
to `/etc/unbound/conf.d/VPN.conf` on CentOS/Fedora, and in 
`/etc/unbound/unbound.conf.d/VPN.conf` on Debian:

```
server:
    interface: 0.0.0.0
    interface: ::0
    access-control: 10.0.0.0/8 allow
    access-control: 172.16.0.0/12 allow
    access-control: 192.168.0.0/16 allow
    access-control: fc00::/7 allow

    # disable DoH
    # See: https://use-application-dns.net/
    # See: https://support.mozilla.org/en-US/kb/configuring-networks-disable-dns-over-https
    local-zone: use-application-dns.net refuse
    
    # disable iCloud Private Relay
    # See: https://developer.apple.com/support/prepare-your-network-for-icloud-private-relay
    local-zone: mask.icloud.com. refuse
    local-zone: mask-h2.icloud.com. refuse
```

With these options Unbound listens on all interfaces and the RFC 1981 and 4193 
ranges are allowed. These ranges are the defaults for deploys done by the 
`deploy_${DIST}.sh` scripts.

Enable Unbound during boot, and (re)start it:

```
$ sudo systemctl enable unbound
$ sudo systemctl restart unbound
```

## Profile Configuration

Modify `/etc/vpn-user-portal/config.php` for each of the VPN profiles 
where you want to use "local DNS", point the `dnsServerList` entry to
the IPv4 (and IPv6) address(es) of your DNS server or the template variables
`@GW4@` and/or `@GW6@`:

```
'dnsServerList' => ['@GW4@', '@GW6@'],
```

The `@GW4@` and `@GW6@` template variables are replaced by the gateway IP 
addresses of the VPN server. You can of course also specify real IP addresses 
here, but make sure the DNS servers are reachable by the VPN clients and that 
traffic to the DNS server(s) is routed over the VPN if you are not using a 
"default gateway" configuration.

**NOTE**: the template variables `@GW4@` and `@GW6@` are available in 
vpn-user-portal >= 3.1.6. 

## Firewall

In order to allow the VPN clients to reach the DNS server, the firewall needs
to be relaxed to allow traffic to `udp/53` and `tcp/53` coming from the VPN 
clients.

Follow the instructions [here](FIREWALL.md#local-dns)

## Apply

To apply the configuration changes:

```
$ sudo vpn-maint-apply-changes
```
