---
title: Add Node
description: Add a VPN node for handling OpenVPN connections
category: howto
---

This document describes how to add a new VPN server to your VPN setup. We 
assume you setup your current VPN server using `deploy_${DIST}.sh`.

Adding more servers will allow you to handle more VPN users concurrently.

When using multiple servers, we'll make a distinction between _controller_ and
_node(s)_. The controller runs the portal and API, the node runs the OpenVPN 
process(es). A typical deploy looks like this:

* Machine 1 has both _controller_ and _node_ functionality in location X;
* Machine 2 has _node_ functionality in location Y;
* Machine _n_ has _node_ functionality in location _N_.

Those machines can be in the same data center, or in physically different 
locations.

# Prerequisites

In order to add node(s) to your VPN setup there needs to be a _secure_ way for
the controller to communicate with the node(s). Typically you'd use a private 
VLAN for this. However, how exactly this is done is out of scope here.

We assume your node(s) will be reachable by the controller so it can access the 
OpenVPN management ports, i.e. TCP ports 11940 and up.

Note: those ports MUST only be available to the controller NOT to the public
Internet!

# Setup

## Controller

Initially we'll leave the controller, your existing VPN server, alone. We'll 
just add a new "profile" that is delegated to your new node.

Add a new profile as described [here](MULTI_PROFILE.md). In addition pay close
attention to the following options:

* `managementIp` - set it to the private VLAN IP address of the node;
* `hostName` - set it to the hostname of the VPN node that points to its 
  public IP address;
* `range` and `range6` - set them to the IP addresses you want that particular 
  node to issue to the clients.

Next, we want to allow access from the node to the `vpn-server-api` component 
on the controller. Modify `/etc/httpd/conf.d/vpn-server-api.conf` and add 
`Require ip` lines containing the _public_ IP address(es) of the node. Make 
sure you restart Apache! **NOTE**: the traffic from the _node_ to the 
controller does NOT go over the private VLAN, but connects via HTTPS to the
controller!

Next, take note of the secret under `apiConsumers => vpn-server-node` in 
`/etc/vpn-server-api/config.php`, you'll need it on the node
later.

## Node

You can use the `deploy_${DIST}_node.sh` for installing the node. It will only
install the relevant software to connect to your controller and handle VPN 
connections.

The deploy script will ask for your API URL, which is the full HTTPS URL to 
your VPN controller. Replace the host name with your controller's name, e.g. 
`https://vpn.example.org/vpn-server-api/api.php`.

You will need the API secret as well that you took note of before, the script
will also ask for that!

If everything was setup correctly, the node script should run without any 
problems!

You need to apply the changes on the node, as shown 
[here](PROFILE_CONFIG.md#apply-changes) if you make any changes to the 
profile's configuration on the controller.
