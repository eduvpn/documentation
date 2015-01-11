# Introduction
This document describes deployment considerations for deploying the software to 
allow various configurations for both the VPN server and VPN client.

We try to accomplish a number of things:

- Have a way to separate the various configurations safely;
- Make it possible to provide organization specific client and server 
  configurations
- Allow support for not routing all traffic over the VPN, but only certain IP
  ranges;

The goal is to make this is easy as possible with the least amount of 
modifications required to both servers and clients.

# Considerations
There are a number of approaches to accomplishing multiple organization 
support:

1. Modify the management software to support multiple organizations with 
   different server and client configurations;
2. Create additional instances with their own VPN service and configuration(s)

We will choose the second option for a number of reasons:

1. The software does not need to be modified at all;
2. It will be possible to install the software anywhere: centralized or 
   directly under control of the organization;
3. Running one VPN service introduces additional complications regarding the 
   VPN service configuration

It is still possible to have one VPN box
There is also a hybrid solution possible where multiple VPN services are 
controlled by one management platform, but there does not seem to be a benefit
in doing so without also duplicating the management interface. This will keep 
it much simpler without needing to support multiple (client) configuration
templates.

# Software Maintenance
Due to the availability of RPM packages and the available infrastructure to 
support software updates it will be trivial to maintain additional instances. 
After a one-time setup the instance can be updated by just using the platform's 
update mechanism.

By having multiple instances it also becomes possible to easily test software 
updates on test instances.

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
config and possibly a `randomize-hosts` option.

# Work To Be Done
We need to update the deployment manual to describe more configurations on how
to route only certain IP ranges over the VPN while not (by default) routing
all traffic over the VPN to support the access to private resources at an 
organization without interfering with the rest of the user's traffic.
