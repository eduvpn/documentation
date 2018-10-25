# Introduction

There are many aspects of "scaling", and not all will be answered, but it 
should give the reader a general idea about how well the server works with many 
clients.

# One Server

Most simple deploys have one server. So how well does that scale with the 
current software? The important metric here is "concurrent connected clients".

## Hardware

It is recommend to run "bare metal" and not on a virtual machine. One can start
with a virtual machine, but for (very) serious use it makes sense to run on a 
physical machine.

A machine up to 16 cores is supported. Having a CPU with AES-NI is highly 
recommended as that will improve the performance substantially.

For networking, it is recommended to use 10Gbit+ networking equipment. It is 
possible to use 2 NICs, one to handle the VPN traffic, and one to handle the 
"plain" traffic. This could potentially increase the performance by a factor of
two.

## Server Configuration

Gathering information from other VPN operators resulted in estimating that one 
needs one CPU core for ~64 concurrent client connections. As the OpenVPN 
server is not multi threaded, client connections will not automatically be 
"distributed" over CPU cores. So in order to use multiple cores, we need 
multiple OpenVPN server processes on one server. The approach we took is to 
indeed start multiple OpenVPN server processes and distribute clients over 
them.

The server software is currently limited to 16 OpenVPN processes per VPN 
profile. This means that for simple single server deploys, the software scales 
to ~16 CPU cores, allowing for 16 * 64 = 1024 clients to connect. This will be 
rounded down due to loss of VPN server IPs and IPv4 network/broadcast 
addresses.

To issue an IP address to all connected clients in this scenario, one would 
need a `/22` IPv4 network configured in the `range` setting of the VPN profile.
As for IPv6, there is a lot of space available, so pretty much any range will 
do in the `range6` configuration option.

In addition, the UDP/TCP ports can be listed in the `vpnProtoPorts` list. For 
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

This list contains 16 entries. Please note that the number of listed ports 
should be either 1, 2, 4, 8 or 16.

## Client

In order to distribute client connections over the various ports, the client
configuration contains a random subset of this list. One UDP and one TCP 
entry is chosen from this list. So for example, when a user downloads a 
configuration, the `remote` lines could be like this:

    remote vpn.example 1195 udp
    remote vpn.example 1200 tcp

Because every configuration download will result in another (random) selection
of ports, the load will eventually be distributed among the various processes.
