---
title: Scaling
description: Performance/Scaling Notes
---

Most organizations start by deploying a single server, which can scale quite 
well to ~ 1000 simultaneously connected clients assuming >= 16 CPU cores with 
AES-NI and adequate network performance, e.g. 10+ Gbit interface(s).

There are many aspects of "scaling", and not all will be answered here, but 
this document will provide input about how to design and configure your VPN 
server(s) in order to handle a large amount of VPN clients.

# One Server

Most simple deploys have a single server setup. So how well does that scale 
with the current software? The important metric here is "concurrent connected 
clients".

## Hardware

It is recommend to run "bare metal" and not on a virtual platform. One can 
start with a virtual machine, and move to bare metal later to increase the 
performance of the VPN server. It is hard to quantify the benefits of moving to
bare metal as it depends on the VM platform that is being used and how it is 
configured. Dedicated network interfaces, for example using IOMMU may also 
increase the performance.

A CPU with AES-NI (hardware accelerated AES) is highly recommended. It will
substantially improve the performance.

For networking, it is recommended to use 10+ Gbit networking equipment. It is 
possible to use 2 NICs, one to handle the VPN traffic, and one to handle the 
"plain" traffic. This could potentially increase the performance by a factor of
two.

## Server Configuration

Gathering information from other VPN operators resulted in estimating that one 
needs one CPU core for ~64 concurrent client connections. As the OpenVPN 
software is not multi threaded, client connections will not automatically be 
"distributed" over CPU cores. So in order to use multiple cores, we need 
multiple OpenVPN server processes on one server. The approach we took is to 
start multiple OpenVPN server processes and distribute clients over them.

The server software is currently limited to 64 OpenVPN processes per VPN 
profile. This means that for single server deploys, the software scales 
to ~64 CPU cores, allowing for 64 * 64 = 4096 clients to connect. This will be 
rounded down due to "loss" of VPN server IPs and IPv4 network/broadcast 
addresses. Of course, a machine with 64 cores is still pretty rare. It will be
more common to divide this over multiple (physical) machines.

To issue an IP address to all connected clients in this scenario, one would 
need a `/20` IPv4 network configured in the `range` setting of the VPN profile.
As for IPv6, at least an `/100` is required in the `range6` option. Each 
OpenVPN process will get a `/112`, the smallest block currently supported by 
OpenVPN.

Additional UDP/TCP ports (up to 64) can be configured with `vpnProtoPorts`. For 
example:

    'vpnProtoPorts' => [
        'udp/1194',
        'tcp/1194',
        'udp/1195',
        'tcp/1195',
        'udp/1196',
        'tcp/1196',
        'udp/1197',
        'tcp/1197',
        'udp/1198',
        'tcp/1198',
        'udp/1199',
        'tcp/1199',
        'udp/1200',
        'tcp/1200',
        'udp/1201',
        'tcp/1201',
    ],

See [OpenVPN Processes](PROFILE_CONFIG.md#openvpn-processes) for more 
information.

## Client

In order to distribute client connections over the various ports, the client
configuration is generated with one UDP and TCP port picked at random. So for 
example, when a user downloads a configuration, the `remote` lines could be 
like this:

    remote vpn.example 1195 udp
    remote vpn.example 1200 tcp

Because every configuration download will result in another (random) selection
of ports, the load will eventually be distributed among the various processes.

Starting from release 2.1.1 of 
[vpn-user-portal](https://github.com/eduvpn/vpn-user-portal) the following way
of dealing with "special" ports is implemented, assuming they are used. Special 
ports are always added at the end of the configuration files, below the 
"remote" lines as mentioned above. By special ports the following ports and 
protocols are meant:

* `udp/53`
* `udp/443`
* `tcp/80`
* `tcp/443`

They have a higher chance of working in restricted networks. If they are made 
available through `vpnProtoPorts`, or `exposedVpnProtoPorts` one UDP and one 
TCP port is picked at random from the special ports, that way at most 4 
"remotes" are listed in the client configuration, e.g.:

    remote vpn.example 1195 udp
    remote vpn.example 1200 tcp
    remote vpn.example 443 udp
    remote vpn.example 80 tcp

# Multiple Servers

It is also possible to deploy extra servers with OpenVPN processes. This can
currently be configured in two ways:

1. Over a private (V)LAN between the controller (portal) and additional 
   node(s). Documented [here](ADD_NODE.md).
2. Over a TLS connection between the controller (portal) and additional 
   node(s). Documented [here](ADD_DAEMON_NODE.md).

The first one has been supported since 2.x of eduVPN / Let's Connect!. The 
second one is supported in vpn-server-api >= 2.0.5.
