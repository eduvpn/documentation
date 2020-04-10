---
title: Add Node(s)
description: Add additional VPN nodes for handling OpenVPN connections
category: howto
---

**NOTE**: the daemon is currently only supported on CentOS and Fedora!

**NOTE**: if you have only 1 VPN server and do not want to deploy additional
servers, check the documentation on how to switch to the daemon on one server 
[here](VPN_DAEMON.md).

**NOTE**: if you want to deploy a controller with node(s) we recommend you
look at [this](MULTI_NODE.md) documentation!

This document describes how to add new VPN servers to your VPN setup. We 
assume you setup your current VPN server using `deploy_${DIST}.sh` and have 
everything on one machine.

Adding more servers will allow you to handle more VPN users concurrently!

When using multiple servers, we'll make a distinction between _controller_ and
_node(s)_. The controller runs the portal and API, the node runs the OpenVPN 
process(es). A typical deploy looks like this:

* Machine 1 has both _controller_ and _node_ functionality in location X (this 
  is what you end up with when you use `deploy_${DIST}.sh`);
* Machine 2 has _node_ functionality in location Y;
* Machine _n_ has _node_ functionality in location _N_.

Those machines can be in the same data center, or in physically different 
locations.

# Prerequisites

In order to securely add node(s) to your VPN setup we implemented a simple 
[VPN daemon](https://github.com/letsconnectvpn/vpn-daemon) that runs on the 
node(s). The communication channel between the controller and node is 
protected by TLS (client certificates) when contacting remote nodes.

# Setup

## Controller

First we switch our controller to use the daemon as well to talk to the local
OpenVPN processes. This is rather simple:

    $ sudo yum -y install vpn-daemon
    $ sudo systemctl enable --now vpn-daemon

Modify `/etc/vpn-server-api/config.php` and add the configuration key 
`useVpnDaemon` and set its value to `true` in the "root", i.e. on the same 
level as `vpnProfiles`.

Make sure everything still works, i.e. you can see connected clients when 
visiting the "Connections" tab in the portal.

### CA 

As the daemon will use TLS with client certificates when talking to remote 
daemons, and **only** when talking to remote daemons, we have to set up a 
(new) PKI with our own root certificate and generate server & client 
certificates. These certificates will be valid for 5 years, the default of the
CA. The `--no-after CA` flag means the certificates will expire at the exact 
same moment as the CA.

    $ sudo yum -y install vpn-ca

Generate the CA and certificates:

    $ vpn-ca -init
    $ vpn-ca -server vpn-daemon -not-after CA
    $ vpn-ca -client vpn-daemon-client -not-after CA

Now you have to copy the `ca.crt`, `vpn-daemon-client.crt` and 
`vpn-daemon-client.key` to `/etc/vpn-server-api/vpn-daemon` and make sure the 
web server can read them:

    $ sudo mkdir -p /etc/vpn-server-api/vpn-daemon
    $ sudo chmod 0710 /etc/vpn-server-api/vpn-daemon
    $ chmod 0640 ca.crt vpn-daemon-client.crt vpn-daemon-client.key
    $ sudo cp ca.crt vpn-daemon-client.crt vpn-daemon-client.key /etc/vpn-server-api/vpn-daemon
    $ sudo chgrp -R apache /etc/vpn-server-api/vpn-daemon

Keep track of the `vpn-daemon.crt` and `vpn-daemon.key` files as you'll need
them later on the node.

### Profile

Add a new profile to your server as described [here](MULTI_PROFILE.md). For 
every node you need to add an additional profile. You need to take care of 
setting the following options correctly for the new node:

* `managementIp` - set it to the IP address on which you will contact your 
  new node;
* `hostName` - set it to the hostname of the VPN node that points to its 
  public IP address;
* `range` and `range6` - set them to the IP addresses you want that particular 
  node to issue to the clients.

If you want to use "round robin" DNS to balance the load over various nodes
you can set the `hostName` to the same hostname of your other profile. You 
can also use the `hideProfile` in the configuration to not show it to users
directly.

Next, we want to allow access from the node(s) to the `vpn-server-api` API 
component on the controller. Modify `/etc/httpd/conf.d/vpn-server-api.conf` and 
add `Require ip` lines containing the IP address(es) of the node(s). Most 
likely this will be the public IP address(es) of the node(s). Make sure you 
restart Apache!

Take note of the secret under `apiConsumers => vpn-server-node` in 
`/etc/vpn-server-api/config.php`, you'll need it on the node
later.

Set the configuration option `profileList` in `/etc/vpn-server-node/config.php` 
and list only the VPN profiles that are active on the controller, not the one 
you want to deploy on the node, e.g.:

    'profileList' => ['internet'],

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
problems! If it doesn't you can always re-run it.

You can restrict the profiles you deploy on the node. By default, all profiles
will be deployed, which is not always what you want.

You can use the configuration option `profileList` in 
`/etc/vpn-server-node/config.php`. It takes an array containing a list of 
profiles to deploy on this particular node. The default, when the option is 
missing, is to deploy _all_ profiles on this node. Example:

    'profileList' => ['internet-far-away'],

Next, you have to modify the firewall configuration in 
`/etc/vpn-server-node/firewall.php` to allow access to the daemon from your 
controller:

    [
        'proto' => ['tcp'],
        'src_net' => ['x.y.z.a/32'],
        'dst_port' => [41194],
    ],

Here `x.y.z.a` is the IP address of your controller. If you are using NAT on
your node, make sure to also update `natRules` in the firewall config.

Tell the node to use the daemon by adding this to 
`/etc/vpn-server-node/config.php`:

    'useVpnDaemon' => true,

To apply the changes run the `apply_changes.sh` script from this repository 
on your VPN server.

Now, we are ready to configure the daemon.

### Daemon 

Now to allow the controller to contact the node, we have to setup the daemon.

    $ sudo yum -y install vpn-daemon

Enable TLS by removing the comment in `/etc/sysconfig/vpn-daemon` and set the
`LISTEN` line to the IP address that you configured in the `managementIp` in
the controller, e.g.

    ENABLE_TLS=-enable-tls
    LISTEN=x.y.z.b:41194

Where `x.y.z.b` is the IP address of the node. This is probably the public
IP address of the node.

**NOTE** we have some problems with automatically starting `vpn-daemon` on boot
when you specify an IP address. The IP won't be assigned to the interface 
before `vpn-daemon` tries to start and thus fail to start. The (dirty) solution 
is to use `LISTEN=:41194` so it listens on ALL IPs and interfaces. It is VERY
important then to firewall this port appropriately. See above where this is 
done.

Copy the certificates you generated on the controller to the right place on the
node:

    $ cp ca.crt           /etc/pki/vpn-daemon/
    $ cp vpn-daemon.crt   /etc/pki/vpn-daemon/server.crt
    $ cp vpn-daemon.key   /etc/pki/vpn-daemon/private/server.key
    $ chgrp -R vpn-daemon /etc/pki/vpn-daemon

Start the daemon and enable it on boot:

    $ sudo systemctl enable --now vpn-daemon

Make sure `vpn-daemon` runs:

    $ ps aux | grep vpn-daemon
    vpn-dae+ 12680  0.0  1.3 211724 13596 ?        Ssl  11:09   0:00 /usr/bin/vpn-daemon -enable-tls -listen 145.100.181.30:41194

If not, check the log, it probably has something to do with the certificates 
being unreadable:

    $ journalctl -f -t vpn-daemon

Once the daemon runs, everything should work. Try to connect to the new 
profile using the eduVPN / Let's Connect! app or through the portal.
