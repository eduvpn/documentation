# Introduction

Most organizations start by deploying a single server, which can scale quite 
well to ~ 1000 simultaneously connected clients assuming >= 16 CPU cores with 
AES-NI and adequate network performance, e.g. 10+ Gbit interface(s).

There are many aspects of "scaling", and not all will be answered here, but this document 
will provide input about how to design and configure your VPN server(s) in order to handle a large amount of VPN clients.

# One Server

Most simple deploys have a single server setup. So how well does that scale with the 
current software? The important metric here is "concurrent connected clients".

## Hardware

It is recommend to run "bare metal" and not on a virtual platform. One can 
start with a virtual machine, and move to bare metal later to increase the 
performance of the VPN server. It is hard to quantify the benefits of moving to
bare metal as it depends on the VM platform that is being used and how it is 
configured. Dedicated network interfaces, for example using IOMMU may also 
increase the performance.

The current architecture limits the number of OpenVPN processes to 16 per 
profile. It makes sense to match the number of CPU cores with the number of 
OpenVPN processes. So up to 16 cores per server (profile) makes sense. It is in 
no way required to start with 16 cores for a VM server, but it is possible to 
slowly grow to 16 cores when the VPN server use increases.

A CPU with AES-NI (hardware accelerated AES) is highly recommended. It will
substantially improve the performance.

For networking, it is recommended to use 10+ Gbit networking equipment. It is 
possible to use 2 NICs, one to handle the VPN traffic, and one to handle the 
"plain" traffic. This could potentially increase the performance by a factor of
two.

## Server Configuration

Gathering information from other VPN operators resulted in estimating that one 
needs one CPU core for ~64 concurrent client connections. As the OpenVPN 
software is not multi-threaded, client connections will not automatically be 
"distributed" over CPU cores. So in order to use multiple cores, we need 
multiple OpenVPN server processes on one server. The approach we took is to 
start multiple OpenVPN server processes and distribute clients over them.

The server software is currently limited to 16 OpenVPN processes per VPN 
profile. This means that for simple single server deploys, the software scales 
to ~16 CPU cores, allowing for 16 * 64 = 1024 clients to connect. This will be 
rounded down due to "loss" of VPN server IPs and IPv4 network/broadcast 
addresses.

To issue an IP address to all connected clients in this scenario, one would 
need a `/22` IPv4 network configured in the `range` setting of the VPN profile.
As for IPv6, at least an `/108` is required in the `range6` option. Each 
OpenVPN process will get a `/112`, the smallest block currently supported by 
OpenVPN.

Additional UDP/TCP ports (up to 16) can be configured with `vpnProtoPorts`. For 
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
configuration contains a random subset of this list. One UDP and one TCP 
entry is chosen from this list. So for example, when a user downloads a 
configuration, the `remote` lines could be like this:

    remote vpn.example 1195 udp
    remote vpn.example 1200 tcp

Because every configuration download will result in another (random) selection
of ports, the load will eventually be distributed among the various processes.
