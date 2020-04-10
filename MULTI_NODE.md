---
title: Multi Node
description: Set up a controller with two nodes
category: howto
---

**WORK IN PROGRESS (2020-04-06)**

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
the duplicate to `node-b`. Also add the `useVpnDaemon` option:

    <?php return array (
      'useVpnDaemon' => true,
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
not the same for both profiles.

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

Finally, we need to create a CA to secure the connection between the controller
and nodes. You can do this on the controller, or on your own system. We use 
[vpn-ca](https://github.com/letsconnectvpn/vpn-ca) for this. You can easily
install it on the controller:

    $ sudo yum -y install vpn-ca
    $ mkdir -p ${HOME}/ca
    $ cd ${HOME}/ca
    $ vpn-ca -init
    $ vpn-ca -client vpn-daemon-client -not-after CA
    $ vpn-ca -server vpn-daemon-node-a -not-after CA
    $ vpn-ca -server vpn-daemon-node-b -not-after CA
    $ chmod 0640 *.crt *.key

Now install the `vpn-daemon-client` certificate:

    $ sudo mkdir -p /etc/vpn-server-api/vpn-daemon
    $ sudo chmod 0710 /etc/vpn-server-api/vpn-daemon
    $ sudo cp ca.crt vpn-daemon-client.crt vpn-daemon-client.key /etc/vpn-server-api/vpn-daemon
    $ sudo chgrp -R apache /etc/vpn-server-api/vpn-daemon

Copy the `ca.crt`, `vpn-daemon-node-a.*` to Node A and `ca.crt`, 
`vpn-daemon-node-b.*` to Node B for later use.

Before moving on to the nodes, make not of the `vpn-server-node` secret under
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

Modify `/etc/sysconfig/vpn-daemon`:

    ENABLE_TLS=-enable-tls
    LISTEN=:41194

**NOTE**: when specifying the IP address to listen on, vpn-daemon sometimes
fails to start at boot... so we listen on everything here. If anyone knows a
fix, please let us know!

Now copy the certificates/keys you copied to the node already before to the 
right place:

    $ sudo cp ca.crt                /etc/pki/vpn-daemon/
    $ sudo cp vpn-daemon-node-a.crt /etc/pki/vpn-daemon/server.crt
    $ sudo cp vpn-daemon-node-a.key /etc/pki/vpn-daemon/private/server.key
    $ sudo chgrp -R vpn-daemon      /etc/pki/vpn-daemon

Start/enable the daemon:

    $ sudo systemctl enable --now vpn-daemon

Next we have to update the node configuration and the firewall. First edit 
`/etc/vpn-server-node/config.php` and add the following configuration options:

    'useVpnDaemon' => true,
    'profileList' => ['node-a'],

Now the firewall in `/etc/vpn-server-node/firewall.php`:

Under `inputRules` you add this:

    [
        'proto' => ['tcp'], 
        'src_net' => ['145.0.6.71/32', '2001:610:188:418:145:0:6:71/128'], 
        'dst_port' => [41194]
    ],

This allows the controller to access the daemon. Make sure you also update the
`natRules` section, for now we keep NAT for both IPv4 and IPv6:

    'natRules' => [
        'node-a' => [
            'enableNat' => ['IPv4', 'IPv6']
        ],
    ],

Now you are ready to apply the changes and it should work without error:

    $ sudo documentation-2/apply_changes.sh

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

The `ta.key` is the fallback "TLS Crypt" key. If that file exists, the profile 
specific keys are ignored.

On the nodes, apply the changes again:

    $ sudo documentation-2/apply_changes.sh

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

The way the software is currently set up requires some care when e.g. updating
the various machines. The steps to follow:

1. Stop all OpenVPN processes on the node(s) (`stop_node.sh`);
2. Update the controller (`update_controller.sh`) and reboot if necessary;
3. Update the node(s) (`update_node.sh`);
4. Reboot, if necessary, *or* start the node(s) (`start_node.sh`).

Stopping the node(s) first is required to make sure all clients are cleanly 
disconnected and the disconnect event is logged at the controller.

You can find these scripts in the `multi_node` folder of the documentation
repository.

**NOTE**: make sure you ran `apply_changes.sh` on all nodes before using the
update scripts.

## Firewall

The default firewall is nice to get going quickly. But we can do a little 
better than that on the nodes and tightening it some more. This is because we 
know the specific environment we run in.

First, we disable the firewall regeneration in 
`/etc/vpn-server-node/config.php` by adding adding `manageFirewall` and setting
it to `false`. This prevents the `apply_changes.sh` script from overwriting 
our custom firewall.

In the example below, `ens160` is the external interface that links the 
machine(s) to the Internet.

`/etc/sysconfig/iptables`:

```
*nat
-P PREROUTING ACCEPT
-P INPUT ACCEPT
-P OUTPUT ACCEPT
-P POSTROUTING ACCEPT
-A POSTROUTING -s 10.1.0.0/25 -j SNAT --to-source 145.0.6.72
COMMIT
*filter
-P INPUT ACCEPT
-P FORWARD ACCEPT
-P OUTPUT ACCEPT
-A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
-A INPUT -i lo -j ACCEPT
-A INPUT -p icmp -j ACCEPT
-A INPUT -p tcp -m tcp --dport 22 -m conntrack --ctstate NEW,UNTRACKED -j ACCEPT
-A INPUT -s 145.0.6.71/32 -p tcp -m tcp --dport 41194 -m conntrack --ctstate NEW,UNTRACKED -j ACCEPT
-A INPUT -p udp -m udp --dport 1194 -m conntrack --ctstate NEW,UNTRACKED -j ACCEPT
-A INPUT -p tcp -m tcp --dport 1194 -m conntrack --ctstate NEW,UNTRACKED -j ACCEPT
-A INPUT -m conntrack --ctstate INVALID -j DROP
-A INPUT -j REJECT --reject-with icmp-host-prohibited
-A FORWARD -i tun+ -o ens160 -j ACCEPT
-A FORWARD -i ens160 -o tun+ -j ACCEPT
-A FORWARD -j REJECT --reject-with icmp-host-prohibited
COMMIT
```

`/etc/sysconfig/ip6tables`:

```
*nat
-P PREROUTING ACCEPT
-P INPUT ACCEPT
-P OUTPUT ACCEPT
-P POSTROUTING ACCEPT
-A POSTROUTING -s fd00:1:1:1::/64 -j SNAT --to-source 2001:610:188:418:145:0:6:72
*filter
-P INPUT ACCEPT
-P FORWARD ACCEPT
-P OUTPUT ACCEPT
-A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
-A INPUT -i lo -j ACCEPT
-A INPUT -p ipv6-icmp -j ACCEPT
-A INPUT -p tcp -m tcp --dport 22 -m conntrack --ctstate NEW,UNTRACKED -j ACCEPT
-A INPUT -s 2001:610:188:418:145:0:6:71/128 -p tcp -m tcp --dport 41194 -m conntrack --ctstate NEW,UNTRACKED -j ACCEPT
-A INPUT -p udp -m udp --dport 1194 -m conntrack --ctstate NEW,UNTRACKED -j ACCEPT
-A INPUT -p tcp -m tcp --dport 1194 -m conntrack --ctstate NEW,UNTRACKED -j ACCEPT
-A INPUT -m conntrack --ctstate INVALID -j DROP
-A INPUT -j REJECT --reject-with icmp6-adm-prohibited
-A FORWARD -i tun+ -o ens160 -j ACCEPT
-A FORWARD -i ens160 -o tun+ -j ACCEPT
-A FORWARD -j REJECT --reject-with icmp6-adm-prohibited
COMMIT
```
