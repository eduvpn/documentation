---
title: Local DNS
description: Run Local DNS Resolver on VPN server
category: howto
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

    $ sudo apt-get -y install unbound

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

Modify `/etc/vpn-server-node/firewall.php` to allow traffic from the VPN
clients to both `udp/53` and `tcp/53`. Replace the IP ranges with your VPN 
client ranges:

    'inputRules' => [

        ...

        // Allow access to local DNS server from VPN clients
        [
            'proto' => ['tcp', 'udp'],
            'src_net' => ['10.0.0.0/8', 'fd00::/8'],
            'dst_port' => [
                53,     // DNS
            ],
        ],

        ...

    ],

## Apply

Do not forget to [apply](PROFILE_CONFIG.md#apply-changes) the changes!
