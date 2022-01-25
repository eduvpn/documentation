 # Introduction

By default, the VPN service is installed on one system using the 
`deploy_${DIST}.sh` script. This works really well for small(ish) deployments, 
the _availability_ and _reliability_ depend directly on that of the system or
virtual machine the service is running on.

By deploying a virtual environment that can has "high availability" and can be 
scaled (dynamically) this might be more than enough for most deployments, even
when handling lots of VPN connections. One can handle _a lot_ of connections on
a system with 64 CPU cores and 10 Gb network. Just saying :-)

Something is to be said for keeping everything on one system or virtual 
machine: it is easy to create a backup/snapshot of the system and restore it 
in a few minutes in case of trouble.

If you do not have a "high available" virtual cluster at your disposal you may
require something more, i.e. split the VPN service over multiple systems where
you can tolerate one or more machines going offline.

Of course, everything has trade-offs. If you are not careful, your service 
could easily become _less_ available than just running everything on a 
Raspberry Pi in your office closet.

# Terminology

The software conceptually consists of two components that can be "split" and
run on different systems.

1. Controller / Portal
2. Node

The "Controller / Portal" handles the Web UI, User Authentication, OAuth API 
for the VPN applications and and service configuration. 

The "Node" is responsible for configuring the VPN software, i.e. OpenVPN and 
WireGuard, reporting to the "Controller / Portal" and handling the VPN 
connections.

```
.-----------------------------------------------.
| VPN Server                                    |
|                                               |
|                                               |
|                                               |
.-----------------.       .---------------------.
| Portal /        |       | Node                |
| Controller      |       |                     |
|                 |       |                     |
|                 |       |                     |
|                 |<----->|                     |
|                 |       |                     |
.----.            |       .-----------.---------.
| DB |            |       | WireGuard | OpenVPN |
'----'------------'-------'-----------'---------'
```

# Handling More VPN Connections

If you are not so worried about _availability_, but just want to be able to 
handle more VPN connections than can be offered by a single system, e.g. you 
can't increase the number of CPU cores anymore, reach the network limit, or 
want to "exit" your VPN traffic in different locations, what you are looking 
for is a "Multi Node" setup. This is extensively documented 
[here](MULTI_NODE.md).

You can add as many nodes as you want to a single "Controller / Portal". Of 
course, this can be combined with making the "Controller / Portal" redundant as
explained in the next section. 

For example, the diagram below shows 3 systems, where there are two "Nodes" 
and one "Controller / Portal":

```
                .----------------.
                | Portal /       |
                | Controller     |
                |                |
                |                |
           .--->|                |<---.
           |    |                |    |
           |    .----.           |    |
           |    | DB |           |    |
           |    '----'-----------'    |
           |                          |
           v                          v
.---------------------.    .---------------------.
| Node (1)            |    | Node (2)            |
|                     |    |                     |
|                     |    |                     |
|                     |    |                     |
|                     |    |                     |
|                     |    |                     |
.-----------.---------.    .-----------.---------.
| WireGuard | OpenVPN |    | WireGuard | OpenVPN |
'-----------'---------'    '-----------'---------'
```

When a VPN client attempts to connect, it will pick a "Node" at random, but 
first make sure the node is up. So if one node is down for maintenance, the 
VPN client would simply pick another node and connect to that one.

# Making the "Controller / Portal" Redundant

If you _are_ worried about _availability_, you may want to duplicate the 
"Portal / Controller" as well. Obviously, this only makes sense if you have 
more than one node, otherwise there's still a single point of failure 
(your "Node").

```
               .------------------.
         .---->| Database Cluster |<-----.
         |     '------------------'      |
         |                               |
         |                               |
         |                               |
.----------------.              .----------------.
| Portal /       |              | Portal /       |
| Controller (1) |              | Controller (2) |
|                |              |                |
|                |              |                |
|                |              |                |
|                |              |                |
|                |              |                |
|                |              |                |
'--------.-------'              '--------.-------'
          \                             /
           \                           /
            \                         /
.------------'-----------------------'-----------.
| Load Balancer / "Round Robin DNS" / keepalived |
'------------.----------------------.------------'
            /                        \
           '                          '
.---------------------.    .---------------------.
| Node (1)            |    | Node (2)            |
|                     |    |                     |
|                     |    |                     |
|                     |    |                     |
|                     |    |                     |
|                     |    |                     |
.-----------.---------.    .-----------.---------.
| WireGuard | OpenVPN |    | WireGuard | OpenVPN |
'-----------'---------'    '-----------'---------'
```

Going this way, requires you to have a (network) database available that is 
already "High Available", probably a database cluster. It MUST be more reliable 
than a single "Portal / Controller" system. If you do not have this, or are not 
sure how to set this up, duplicating the "Portal / Controller" makes no sense.

Setting up a database cluster is outside of the scope of this documentation, 
we assume you will have one.

Once you decided to go this way, continue reading the documentation 
[here](REDUNDANT_PORTAL.md).
