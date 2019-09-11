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

Currently we do not have a `deploy_node_${DIST}.sh` unfortunately. You'll have
to manually walk through the `deploy_${DIST}.sh` and perform the relevant steps
until such time we have proper documentation for this. You *only* need to 
install the `vpn-server-node` package, not any of the other packages related to
the portal. After installing `vpn-server-node`, you can modify the default
configuration in `/etc/vpn-server-node/config.php` and make sure `apiPass` and
`apiUri` are set correctly. The `apiPass` contains the string you took note of
when setting up the controller.

The `apiUri` will look like this: 
`https://vpn.example.org/vpn-server-api/api.php`.

Now you should be able to configure the node, by running this on the node:

    $ vpn-server-node-server-config
    $ vpn-server-node-generate-firewall --install

This should generate the OpenVPN configuration files and generate and install
the firewall rules. You need to apply the changes on the node, as shown 
[here](PROFILE_CONFIG.md#apply-changes).
