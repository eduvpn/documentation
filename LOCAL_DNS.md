---
title: Local DNS
description: Run Local DNS Resolver on VPN server
category: advanced
---

New VPN server installations, performed using `deploy_${DIST}.sh`, will use the 
DNS servers used by the server itself (as configured in `/etc/resolv.conf`) for
the VPN clients as well. If no usable address is available, e.g. only 
"localhost" addresses are configured there, the public DNS service offered by 
[Quad9](https://quad9.net/) is used. 

It is possible to run your own local DNS resolver for the VPN clients. This has 
a number of benefits:

- Ability to apply filters to e.g. block known malware domains;
- The upstream DNS is unreliable, sells your query data or is slow;
- You do not want to use the "public DNS" services as offered by Quad9, 
  Cloudflare or Google.

Running your own DNS resolver can also be a good idea if no upstream DNS server 
is provided by your ISP.

**NOTE**: if your organization has a (trusted) DNS service you SHOULD probably
use those! See [PROFILE_CONFIG](PROFILE_CONFIG.md), look for the `dns` option.

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

### CentOS 

    $ sudo yum -y install unbound

### Fedora

    $ sudo dnf -y install unbound

### Debian 

    $ sudo apt -y install unbound

## Configure Unbound

You need to change the Unbound configuration. You can add the following file
to `/etc/unbound/conf.d/VPN.conf` on CentOS/Fedora, and in 
`/etc/unbound/unbound.conf.d/VPN.conf` on Debian:

    server:
        interface: 0.0.0.0
        interface: ::0
        access-control: 10.0.0.0/8 allow
        access-control: fd00::/8 allow

        # disable DoH
        # See: https://use-application-dns.net/
        # See: https://support.mozilla.org/en-US/kb/configuring-networks-disable-dns-over-https
        local-zone: use-application-dns.net refuse
 
With these options Unbound listens on all interfaces and the ranges 
`10.0.0.0/8` and `fd00::/8` are white-listed. These ranges are the defaults for 
deploys done by the `deploy_${DIST}.sh` scripts.

Enable Unbound during boot, and (re)start it:

    $ sudo systemctl enable unbound
    $ sudo systemctl restart unbound

## Profile Configuration

Modify `/etc/vpn-server-api/config.php` for each of the VPN profiles 
where you want to use "local DNS", set the `dns` entry to:

    'dns' => ['@GW4@', '@GW6@'],

The `@GW4@` and `@GW6@` strings will be replaced by the IPv4 and IPv6 address 
of the gateway.

## Firewall

In order to allow the VPN clients to reach the DNS server, the firewall needs
to be relaxed to allow traffic to `udp/53` and `tcp/53` coming from the VPN 
clients.

Follow the instructions [here](FIREWALL.md#local-dns)

## Apply

To apply the configuration changes:

    $ sudo vpn-maint-apply-changes

If the command is not available, install the `vpn-maint-scripts` package first.
