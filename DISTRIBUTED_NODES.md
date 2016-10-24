# Distributed Nodes

This document describes how to configure multiple PoPs around the world to 
allow users to choose the PoP closest to their location to e.g. reduce the 
latency. This document assumes we have 3 VMs, it can also be done with less, 
i.e. 2 VMs, but that will not be described here.

# Security

At this time, the nodes in the network MUST trust each other. A 
breach of one of them has consequences for the entire network of nodes! The 
threat model does NOT include containing a breach of one of the nodes. For 
example, a breached node can:

- contact all other nodes and access the OpenVPN management interfaces;
  - listing current connections (including the real client IPs);
  - killing connections;
- obtain additional VPN server certificates;
- ...

## Controller

Install the controller with the `deploy_controller.sh` script. Make sure you 
set the hostname correctly. 

**NOTE**: make sure you take note of the secrets that are printed at the end of 
the installation, you need those to install the nodes.

We configure two profiles, that are running on different machines in 
`/etc/vpn-server-api/vpn.example/config.yaml`. There is already an `internet` 
profile that you can delete. Make sure it looks similar to the configuration 
below, of course you can modify the various fields to match your situation.

    vpnProfiles:
        europe:
            profileNumber: 1
            displayName: 'Internet Access (Europe)'
            extIf: eth0
            useNat: true
            defaultGateway: true
            hostName: europe.vpn.example
            range: 10.0.0.0/24
            range6: 'fd00:4242:4242::/48'
            dns: [8.8.8.8, 8.8.4.4, '2001:4860:4860::8888', '2001:4860:4860::8844']
            dedicatedNode: true
            listen: '::'

        asia:
            profileNumber: 2
            displayName: 'Internet Access (Asia)'
            extIf: eth0
            useNat: true
            defaultGateway: true
            hostName: asia.vpn.example
            range: 10.20.30.0/24
            range6: 'fd00:4445:4647::/48'
            dns: [8.8.8.8, 8.8.4.4, '2001:4860:4860::8888', '2001:4860:4860::8844']
            dedicatedNode: true
            listen: '::'

**NOTE**: make sure the DNS entries, `europe.vpn.example` and 
`asia.vpn.example` point to the OpenVPN nodes for IPv4 (and optionally IPv6).

**NOTE**: the `extIf` is the external interface on the **node** that is used 
to access the Internet on the node, not on the controller.

## Nodes

Take the recorded secrets from `deploy_controller.sh` above and put them in 
the `deploy_node.sh` at the top. Then run the `deploy_node.sh` script and the
node should be automatically configured.

**TODO** the management IP for the nodes is not set yet, we have to do 
something with that. Maybe create a "node-config" script that prints all 
information you need for deploying the nodes...

