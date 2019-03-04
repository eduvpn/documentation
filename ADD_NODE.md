# Introduction

This document describes how to add a new VPN server to your VPN setup. We 
assume you setup your current VPN server using `deploy_${DIST}.sh`.

Adding more servers will allow you to handle more VPN users concurrently.

When using multiple servers, we'll make a distinction between _controller_ and
_node(s)_. The controller runs the portal and API, the node runs the OpenVPN 
process(es).

# Prerequisites

In order to add a node to your VPN setup, you need to arrange for a private
network, e.g. a management VLAN, between the controller and node(s). How this 
is done is out of scope for this document. Make sure you can "ping" in both 
directions and there is no network filtering, e.g. with firewall rules, taking 
place.

This private network is used by the controller to retrieve a list of connected
clients and have the ability to "kick" VPN clients offline.

# Setup

## Controller

Initially we'll leave the controller, your existing node alone. We'll just add
a new "profile" that is delegated to your new node.

Add a new profile as described [here](MULTI_PROFILE.md). In addition pay close
attention to the following options:

* `managementIp` - set it to the _private_ IP address of the node;
* `hostName` - set it to the hostname of the VPN node that points to its 
  public IP address;
* `range` and `range6` - set them to the IP addresses issued by the node;
* `extIf` - set the external interface of the _node_.

Next, we want to allow access from the node to the `vpn-server-api` component, 
modify `/etc/httpd/conf.d/vpn-server-api.conf` and add `Require ip` lines 
containing the _public_ IP address(es) of the node.

Next, take note of the secret under `apiConsumers => vpn-server-node` in 
`/etc/vpn-server-api/default/config.php`, you'll need it on the node
later.

## Node

Currently we do not have a `deploy_node_${DIST}.sh` unfortunately. You'll have
to manually walk through the `deploy_${DIST}.sh` and perform the relevant steps
until such time we have proper documentation for this.
