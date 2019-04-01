# Introduction

This document describes how to add a new VPN server to your VPN setup. We 
assume you setup your current VPN server using `deploy_${DIST}.sh`.

Adding more servers will allow you to handle more VPN users concurrently.

When using multiple servers, we'll make a distinction between _controller_ and
_node(s)_. The controller runs the portal and API, the node runs the OpenVPN 
process(es).

# Prerequisites

In order to add a node to your VPN setup there needs to be a *SECURE* way for
the controller to communicate with the node. Typically you'd use a private 
VLAN for this. However, how exactly this is done is out of scope here.

We assume your node will be reachable by the controller so it can access the 
OpenVPN management ports, i.e. TCP ports 11940 and up.

Note: these ports MUST only be available to the controller NOT to the public
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
* `range` and `range6` - set them to the IP addresses issued by the node;
* `extIf` - set the external interface of the _node_.

Next, we want to allow access from the node to the `vpn-server-api` component, 
modify `/etc/httpd/conf.d/vpn-server-api.conf` and add `Require ip` lines 
containing the _public_ IP address(es) of the node. Make sure you restart 
Apache!

Next, take note of the secret under `apiConsumers => vpn-server-node` in 
`/etc/vpn-server-api/config.php`, you'll need it on the node
later.

## Node

Currently we do not have a `deploy_node_${DIST}.sh` unfortunately. You'll have
to manually walk through the `deploy_${DIST}.sh` and perform the relevant steps
until such time we have proper documentation for this.

Modify `/etc/vpn-server-node/config.php` and make sure `apiPass` and
`apiUri` are set correctly. The `apiPass` contains the string you took note of
when setting up the controller.

The `apiUrl` will look like this: 
`https://vpn.example.org/vpn-server-api/api.php`.

Now you should be able to configure the node:

    $ vpn-server-node-server-config
    $ vpn-server-node-generate-firewall --install

This should generate the OpenVPN configuration files and generate and install
the firewall rules.
