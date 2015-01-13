# Introduction
This document describes an approach for deploying the eduVPN software in such a
way to allow independent organizations for using eduVPN as their own internal
VPN solution.

We try to accomplish a number of things:

- Have a way to separate the various configurations safely where use by
  organization X does not interfere with use by organization Y;
- Make it possible to provide organization specific client and server 
  configurations
- Not necessarily route all traffic over the VPN, but only certain IP ranges;

The goal is to make this is easy and secure as possible with the least amount 
of modifications required to both servers and clients.

We will also look at load balancing options where multiple servers 
share the load. 

# Considerations
There are a number of approaches to accomplishing multiple organization 
support:

1. Modify the management (and VPN) software to support multiple organizations 
   with different server and client configurations;
2. Create additional instances each with their own VPN service and 
   configuration(s)

We prefer the second option for a number of reasons:

1. The software does not need to be modified at all;
2. It will be possible to install the software anywhere: somewhere centralized 
   or directly under control of the organization;
3. Running one VPN service introduces additional complications regarding the 
   VPN service configuration and possibly require modification of the VPN 
   software to enforce the separation of the multiple organizations using the
   service

There is also a hybrid solution possible where multiple VPN services are 
controlled by one management platform, but there does not seem to be a benefit
in doing so without also duplicating the management interface. This will keep 
it much simpler without needing to support multiple (client) configuration
templates and also allows for a PKI infrastructure per organization and allow
easy migrating from a centralized system to a distributed one and the other way
around.

# Software Maintenance
Due to the availability of RPM packages and the available infrastructure to 
support software updates it will be trivial to maintain additional instances. 
After a one-time setup, the instance can be updated by just using the 
platform's update mechanism, i.e. `yum update`.

By having multiple instances it also becomes possible to easily test software 
updates on test instances.

If the software will be hosted at a central location the following 

# User Authentication
Every instance of the eduVPN service will require a separate configuration 
for the user authentication. Currently only SAML is supported, but once 
organizations are interested in running the eduVPN deployment locally 
additional authentication backends like LDAP or RADIUS can easily be 
implemented. For SaaS solutions using SAML seems to be the most convenient as 
that infrastructure is already widely deployed, through SURFconext, direct SAML 
IdP connections or eduGAIN.

# Load Balancing
When providing public routeable addresses the servers need to each only contain
a subset of the IP addresses, so not all servers can contain all IP addresses. 
The rest of the configuration can remain the same though as for the one server
setup. The client needs to just list the other VPN servers in the client 
configuration file and a `remote-random` option.

For example:

    remote vpn1.example.org
    remote vpn2.example.org
    remote-random

This will randomly try either `vpn1.example.org` or `vpn2.example.org`.

Of course, the servers will need to divide the available address space among
themselves. In case public routable addresses are used they will need to be 
split in multiple non-overlapping blocks. "Real" load balancing and fail over
are not provided. Also when the client connects to any other server it will 
get an IP address from a different range. So assuming for all our VPN clients
we have the range `192.168.42.0/24` we can split this in 4 equally sized 
blocks. The following `server` configuration directives would be used, one on
each server:

    server 192.168.42.0 255.255.255.192
    server 192.168.42.64 255.255.255.192
    server 192.168.42.128 255.255.255.192
    server 192.168.42.192 255.255.255.192

In case of load balancing one server configuration should be generated and 
duplicated 4 times and then only the `server` line needs to be modified.

Because of the architecture choices made above regarding support for multiple
organization these load balancing instructions are mostly relevant for the 
generic eduVPN case where a lot of users are expected. However, they can just
as well be applied to the instances of a specific institute if they expect to
have many (concurrent) users.

# Work To Be Done
We need to update the deployment manual to describe more configurations on how
to route only certain IP ranges over the VPN while not (by default) routing
all traffic over the VPN to support the access to private resources at an 
organization without interfering with the rest of the user's traffic. Also the
server/client template needs to be updated to show some example for supporting
multiple servers in the load balancing case.
