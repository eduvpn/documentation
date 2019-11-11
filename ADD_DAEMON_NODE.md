---
title: Add Node(s)
description: Add additional VPN nodes for handling OpenVPN connections
category: howto
---

This document describes how to add new VPN servers to your VPN setup. We 
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

In order to securely add node(s) to your VPN setup we implemented a simple 
[VPN daemon](https://github.com/letsconnectvpn/vpn-daemon) that runs on the 
node(s). This communication channel is protected by TLS and will be accessed
from the VPN controller.

The VPN daemon should only be reachable from the VPN controller!

# Setup

## Controller

Initially we'll leave the controller, your existing VPN server, alone. We'll 
just add a new "profile" that is delegated to your new node.

Add a new profile as described [here](MULTI_PROFILE.md). In addition pay close
attention to the following options:

* `managementIp` - set it to the (public) IP address of your node;
* `hostName` - set it to the hostname of the VPN node that points to its 
  public IP address;
* `range` and `range6` - set them to the IP addresses you want that particular 
  node to issue to the clients.

Next, we want to allow access from the node to the `vpn-server-api` component 
on the controller. Modify `/etc/httpd/conf.d/vpn-server-api.conf` and add 
`Require ip` lines containing the _public_ IP address(es) of the node. Make 
sure you restart Apache!

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

You can restrict the profiles you deploy on the node. By default, all profiles
will be deployed. 

You can use the configuration option `profileList` in 
`/etc/vpn-server-node/config.php`. It takes an array containing a list of 
profiles to deploy on this particular node. The default, when the option is 
missing, is to deploy _all_ profiles on this node. Example:

    'profileList' => ['office', 'sysadm'],

You need to apply the changes on the node, as shown 
[here](PROFILE_CONFIG.md#apply-changes) if you make any changes to the 
profile's configuration on the controller.

### Daemon 

Now to allow the controller to contact the node, we have to setup the daemon.

    $ sudo yum -y install vpn-daemon
    $ sudo systemctl enable --now vpn-daemon

Enable TLS by removing the comment in `/etc/sysconfig/vpn-daemon` and set the
`LISTEN` line to the IP address that you configured in the `managementIp` in
the controller, e.g.

    ENABLE_TLS=-enable-tls
    LISTEN=145.100.181.30:41194

Now we need to generate TLS certificates:

    $ sudo yum -y install vpn-ca

Create a working directory for generating the CA and certificates:

    $ mkdir ${HOME}/ca
    $ cd ${HOME}/ca
    $ vpn-ca -init
    $ vpn-ca -server vpn-daemon
    $ vpn-ca -client vpn-daemon-client
    $ chmod 0640 *.crt *.key

Copy the certificates to the right place:

    $ cp ca.crt vpn-daemon.crt /etc/pki/vpn-daemon/
    $ cp vpn-daemon.key /etc/pki/vpn-daemon/private/
    $ chgrp -R vpn-daemon /etc/pki/vpn-daemon

Restart vpn-daemon:

    $ sudo systemctl restart vpn-daemon

Make sure `vpn-daemon` runs:

    $ ps aux | grep vpn-daemon
    vpn-dae+ 12680  0.0  1.3 211724 13596 ?        Ssl  11:09   0:00 /usr/bin/vpn-daemon -enable-tls -listen 145.100.181.30:41194

If not, check the log, it probably has something to do with the certificates 
being unreadable:

    $ journalctl -f -t vpn-daemon

Copy `ca.crt`, `vpn-daemon-client.crt` and `vpn-daemon-client.key` to your 
controller and put them in the `/etc/vpn-server-api/vpn-daemon` directory. 
Make sure the permissions are correct.

On your **controller**: 
    
    $ sudo mkdir /etc/vpn-server-api/vpn-daemon
    $ cp ca.crt vpn-daemon-client.crt vpn-daemon-client.key /etc/vpn-server-api/vpn-daemon
    $ chmod 0640 /etc/vpn-server-api/vpn-daemon/*
    $ chgrp -R apache /etc/vpn-server-api/vpn-daemon

Now everything should work... Test it by downloading a configuration file from
the portal for your new node and make sure you can connect.
