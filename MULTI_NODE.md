---
title: Multi Node
description: Set up a controller with two nodes
category: advanced
---

**WORK IN PROGRESS (2020-09-24)**

When you want to scale up your deployment, i.e. have multiple nodes connect 
with one controller, this document is for you!

This document will show how to set up multiple nodes. The OpenVPN clients will
be distributed over the nodes using DNS round-robin.

If you already installed the software on one machine already, and want to 
convert your current installation into a controller you can use the 
`convert_to_controller.sh` script.

## Requirements

At least 3 machines (or VMs) running CentOS 7. The two machines that will be
the nodes ideally have the same specifications. They also SHOULD have CPU AES 
acceleration, e.g. AES-NI.

All three need to be set up with static IP configurations and working DNS. Make 
sure all works properly before starting the setup. For example, my test 
deployment uses:

Role       | DNS Host                 | IPv4       | IPv6
---------- | ------------------------ | ---------- | ---------------------------
Controller | frkovpn.tuxed.net        | 145.0.6.71 | 2001:610:188:418:145:0:6:71
Node A     | node-a.frkovpn.tuxed.net | 145.0.6.72 | 2001:610:188:418:145:0:6:72
Node B     | node-b.frkovpn.tuxed.net | 145.0.6.73 | 2001:610:188:418:145:0:6:73

We will use NAT for IPv4 and IPv6 client traffic.

Perform these steps on the hosts:

    $ curl -L -O https://github.com/eduvpn/documentation/archive/v2.tar.gz
    $ tar -xzf v2.tar.gz
    $ cd documentation-2

**TIP**: whenever you modify a `.php` file, make sure the syntax is correct 
after editing:

    $ php -l /path/to/file.php

This will tell you whether or not the syntax is correct!

## Controller

On the controller host:

    $ sudo -s
    # ./deploy_centos_controller.sh

Make note of the credentials that are printed at the end, you can use them to
test your server!

After the controller is installed, make sure you'll get a valid TLS 
certificate, for example using the included `lets_encrypt_centos.sh` script:

    # ./lets_encrypt_centos.sh

Now visit your site at https://frkovpn.tuxed.net/. Make sure there is no TLS 
error and you can login with the credentials you noted before.

By default there is an `internet` profile. We will duplicate this and rename 
it. For this, edit `/etc/vpn-server-api/config.php`. You will find something 
like this:

    <?php return array (
      'vpnProfiles' =>
      array (
        'internet' =>
        array (
            // ...
        ),
      ),
    );

Now copy the `internet` section below it and rename `internet` to `node-a` and
the duplicate to `node-b`. Also add the `useVpnDaemon` option and the 
`vpnDaemonTls` option. Initially we disable TLS between the controller and the
nodes(s):

    <?php return array (
      'useVpnDaemon' => true,
      'vpnDaemonTls' => false,
      'vpnProfiles' =>
      array (
        'node-a' =>
        array (
            // ...
        ),
        'node-b' =>
        array (
            // ...
        ),
      ),
    );

Modify the configuration keys in the respective sections:

Node    | Option        | Value
------- | ------------- | -------------
a       | managementIp  | 145.0.6.72
a       | profileNumber | 1
a       | hostName      | node-a.frkovpn.tuxed.net
a       | displayName   | Node A
a       | range         | 10.1.0.0/25
a       | range6        | fd00:1:1:1::/64
b       | managementIp  | 145.0.6.73
b       | profileNumber | 2
b       | hostName      | node-b.frkovpn.tuxed.net
b       | displayName   | Node B
b       | range         | 10.2.0.0/25
b       | range6        | fd00:2:2:2::/64

You can of course choose your own `range` and `range6`, but make sure they are 
NOT the same for both profiles and do not overlap.

The `managementIp` value MUST contain the IP address of the node(s) at which
it can be reached from the controller.

Next, modify the `RequireAny` section in 
`/etc/httpd/conf.d/vpn-server-api.conf` by adding the IP addresses of the 
nodes:

    <RequireAny>
        Require local
        Require ip 145.0.6.72
        Require ip 2001:610:188:418:145:0:6:72
        Require ip 145.0.6.73
        Require ip 2001:610:188:418:145:0:6:73
    </RequireAny>

Restart Apache:

    $ sudo systemctl restart httpd

Before moving on to the nodes, make note of the `vpn-server-node` secret under
the `apiConsumers` section in `/etc/vpn-server-api/config.php`. You'll need it
next!

## Nodes

The instructions below will be only shown for Node A, but they are identical
for Node B... so you have to perform them twice, please note that on Node B 
you should replace any occurrence of `node-a` with `node-b`. Ideally you 
perform these steps in parallel on both machines.

Make sure you can reach the API endpoint:

    $ curl https://frkovpn.tuxed.net/vpn-server-api/api.php
    {"error":"missing authentication information"}

This error is expected as no secret was provided. This just makes sure the 
controller is configured correctly and allows requests from the nodes.

Next, it is time to install the software. You should have downloaded and 
unpacked the archive already, see [Requirements](#Requirements).

    $ cd documentation-2
    $ sudo -s
    # ./deploy_centos_node.sh

The script will ask for the API URL and the secret. The API URL is the URL we
tested above. The secret is the one extracted at the end of the previous 
section.

The script will output some errors about being unable to start OpenVPN. This is
because we changed the controller's default configuration. It is fine, we will
fix that shortly!

First we install the [vpn-daemon](https://github.com/letsconnectvpn/vpn-daemon):

    $ sudo yum -y install vpn-daemon

Modify `/etc/sysconfig/vpn-daemon` (on Debian: `/etc/default/vpn-daemon`):

    LISTEN=:41194

Start/enable the daemon:

    $ sudo systemctl enable --now vpn-daemon

Next we have to update the node configuration. Edit 
`/etc/vpn-server-node/config.php` and add the following configuration options:

    'useVpnDaemon' => true,
    'profileList' => ['node-a'],

The firewall also requires tweaking, open it to allow traffic from the 
controller to the node's VPN daemon:

In `/etc/sysconfig/iptables`:

    -A INPUT -s 145.0.6.71/32 -p tcp -m state --state NEW -m tcp --dport 41194 -j ACCEPT

In `/etc/sysconfig/ip6tables`, if you prefer using IPv6:

    -A INPUT -s 2001:610:188:418:145:0:6:71/128 -p tcp -m state --state NEW -m tcp --dport 41194 -j ACCEPT

Now you are ready to apply the changes and it should work without error:

    $ sudo vpn-maint-apply-changes

Restart the firewall:

    $ sudo systemctl restart iptables
    $ sudo systemctl restart ip6tables

Make sure you repeat these steps on Node B as well!

Now is the time to test everything. Go to the portal at 
`https://frkovpn.tuxed.net/`, download a configuration, test it with your 
client. Download a configuration for both profiles and make sure they work. 
Login to the admin portal using the `admin` user and password you noted at the
end of the controller install and make sure you see your client(s) under 
"Connections" in the portal when connected to either "Node A" or "Node B" 
profile with your VPN client.

## Load Balancing

Now that everything works, we can _merge_ the profiles to setup a round-robin
DNS based load balancing over the nodes.

On the controller you need to modify `/etc/vpn-server-api/config.php` again.

For the `node-b` profile set `hideProfile` to `true`. The `hostName` key in 
both profiles gets the value `nodes.frkovpn.tuxed.net`. Update the 
`displayName` of `node-a` to something generic, e.g. `Secure Internet`.

As, by default, each profile uses its own "TLS Crypt" key, we need to make sure
both of them use to same key now that the profiles are "merged":

    $ sudo cp /var/lib/vpn-server-api/tls-crypt-node-a.key /var/lib/vpn-server-api/ta.key
    $ sudo chown apache.apache /var/lib/vpn-server-api/ta.key
    
The `ta.key` is the fallback "TLS Crypt" key. If that file exists, the profile 
specific keys are ignored. Keep in mind to restore the `ta.key` file in case 
you do a `vpn-maint-reset-controller` as all files in `/var/lib/vpn-server-api`
will be wiped.

On the nodes, apply the changes again:

    $ sudo vpn-maint-apply-changes

As for DNS, you can use the following configuration:

    nodes.frkovpn   IN  A       145.0.6.72
                    IN  A       145.0.6.73
                    IN  AAAA    2001:610:188:418:145:0:6:72
                    IN  AAAA    2001:610:188:418:145:0:6:73

From now on, the load should be distributed over the VPN nodes once you 
download a new configuration. You can monitor this through the portal on the
"Connections" page. By connecting multiple devices you should see them connect 
to the different nodes instead of all to one node.

## Maintenance

The `vpn-maint-scripts` package has instructions for maintaining a multi node
setup. Please refer to those instructions 
[here](https://github.com/letsconnectvpn/vpn-maint-scripts).

## TLS between Controller and Node(s)

### Controller

Finally, we need to create a CA to secure the connection between the controller
and nodes. You can do this on the controller, or on your own system. We use 
[vpn-ca](https://github.com/letsconnectvpn/vpn-ca) for this. It is already 
installed on your controller:

    $ mkdir -p ${HOME}/ca
    $ cd ${HOME}/ca
    $ vpn-ca -init-ca -name "VPN Service CA"
    $ vpn-ca -client -name vpn-daemon-client -not-after CA
    $ vpn-ca -server -name vpn-daemon -not-after CA
    $ vpn-ca -server -name vpn-daemon -not-after CA
    $ chmod 0640 *.crt *.key

Now install the `vpn-daemon-client` certificate:

    $ sudo mkdir -p /etc/vpn-server-api/vpn-daemon
    $ sudo chmod 0710 /etc/vpn-server-api/vpn-daemon
    $ sudo cp ca.crt vpn-daemon-client.crt vpn-daemon-client.key /etc/vpn-server-api/vpn-daemon
    $ sudo chgrp -R apache /etc/vpn-server-api/vpn-daemon

Finally, remove the `vpnDaemonTls` option from 
`/etc/vpn-server-api/config.php` to force using TLS.

### Node 

Copy the `ca.crt`, `vpn-daemon.crt`, `vpn-daemon.key` to Node A and Node B. On 
the node(s) copy the certificates/keys to the right place:

    $ sudo cp ca.crt                /etc/pki/vpn-daemon/
    $ sudo cp vpn-daemon.crt /etc/pki/vpn-daemon/server.crt
    $ sudo cp vpn-daemon.key /etc/pki/vpn-daemon/private/server.key
    $ sudo chgrp -R vpn-daemon      /etc/pki/vpn-daemon

Modify `/etc/sysconfig/vpn-daemon` (on Debian: `/etc/default/vpn-daemon`):

    ENABLE_TLS=-enable-tls
    LISTEN=:41194

Restart the daemon:

    $ sudo systemctl restart vpn-daemon

Test everything again as mentioned in the last paragraph of the previous 
"Nodes" section without TLS.

## FAQ

**Can I also have multiple profiles on the nodes?**

This document only talks about one profile per VPN node. In case you have 
multiple profiles, you also need to read [MULTI_PROFILE](MULTI_PROFILE.md). 
Make sure you use different `vpnProtoPorts` for your different profiles. You 
can't have two profiles on the same node claim `udp/1194` for example.

**What if I want to use public IPv6 addresses for my VPN clients?**

Check [PUBLIC_ADDR](PUBLIC_ADDR.md) in order to deal with this. Make sure you
also update the (IPv6) firewall to remove the NAT section.
