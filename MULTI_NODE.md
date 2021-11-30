# Multi Node Setup

When you want to scale up your deployment, i.e. have multiple nodes connected 
with one controller, this document is for you!

This document will show how to set up multiple nodes. The VPN clients will 
automatically be distributed over the nodes.

## Requirements

At least 3 machines (or VMs) running Debian >= 11. The two machines that will 
be the nodes ideally have the same specifications. They also SHOULD have CPU 
AES acceleration, e.g. AES-NI.

All three need to be set up with static IP configurations and working DNS. Make 
sure all works properly before starting the setup. For example, my test 
deployment uses:

Role       | DNS Host               | IPv4       | IPv6         |
---------- | ---------------------- | ---------- | ------------ |
Controller | vpn.example.org        | 192.0.2.10 | 2001:db8::10 |
Node A     | node-a.vpn.example.org | 192.0.2.20 | 2001:db8::20 |
Node B     | node-b.vpn.example.org | 192.0.2.30 | 2001:db8::30 |

We will use NAT for IPv4 and IPv6 client traffic.

Perform these steps on the hosts:

    $ curl -L -O https://github.com/eduvpn/documentation/archive/v3.tar.gz
    $ tar -xzf v3.tar.gz
    $ cd documentation-3

**TIP**: whenever you modify a `.php` file, make sure the syntax is correct 
after editing:

    $ php -l /path/to/file.php

This will tell you whether or not the syntax is correct!

## Controller

On the controller host:

    $ sudo -s
    # ./deploy_debian_controller.sh

Make note of the credentials that are printed at the end, you can use them to
test your server!

After the controller is installed, make sure you'll get a valid TLS 
certificate, for example using the included `lets_encrypt_debian.sh` script:

    # ./lets_encrypt_debian.sh

Now visit your site at https://vpn.example.org/. Make sure there is no TLS 
error and you can login with the credentials you noted before.

By default there is a `default` profile. We will duplicate this and rename 
it. For this, edit `/etc/vpn-user-portal/config.php`. You will find something 
like this:

```
'vpnProfiles' => [
    [
        'profileId' = 'default',
        'displayName' => 'Default',
        'hostName' => 'vpn.example.org',
        'dnsServerList' => ['9.9.9.9', '2620:fe::fe'],
        'wRangeFour' => '10.43.43.0/24',
        'wRangeSix' => 'fd43::/64',
        'oRangeFour' => '10.42.42.0/24',
        'oRangeSix' => 'fd42::/64',

        ...
        ...
    ],
],
```

To make this a multi node, you need to modify some of the options. Some options
also take a array if they are _node specific_, see 
[Profile Configuration](PROFILE_CONFIG.md) for an overview.

```
'vpnProfiles' => [
    [
        'profileId' = 'default',
        'displayName' => 'Default',
        'hostName' => ['node-a.vpn.example.org', 'node-b.vpn.example.org'],
        'dnsServerList' => ['9.9.9.9', '2620:fe::fe'],
        'wRangeFour' => ['10.43.43.0/24', '10.45.45.0/24'],
        'wRangeSix' => ['fd43::/64', 'fd45::/64'],
        'oRangeFour' => ['10.42.42.0/24', '10.44.44.0/24'],
        'oRangeSix' => ['fd42::/64', 'fd44::/64'],
        'nodeUrl' => ['http://node-a.vpn.example.org:41194', 'http://node-b.vpn.example.org:41194'],
        
        ...
        ...
    ],
],
```

You can of course choose your own `xRangeFour` and `xRangeSix`, but make sure 
they are not duplicated, or overlap!

Next, modify the `<Files node-api.php>` section in 
`/etc/apache2/conf.d/vpn-user-portal.conf` by adding the IP addresses of the 
nodes:

```
<Files node-api.php>
    <RequireAny>
        Require local
        # When using separate VPN node(s) running (vpn-server-node),
        # add the IP address(es) of the node(s) here
        Require ip 192.0.2.0/24
        Require ip 2001:db::/32
    </RequireAny>
</Files>
```

Restart Apache:

    $ sudo systemctl restart apache2

Before moving on to the nodes, make note of the value of 
`/etc/vpn-user-portal/node.key`. You'll need it next!

## Nodes

The instructions below will be only shown for Node A, but they are identical
for Node B... so you have to perform them twice, please note that on Node B 
you should replace any occurrence of `node-a` with `node-b`. Ideally you 
perform these steps in parallel on both machines.

Make sure you can reach the API endpoint:

    $ curl https://vpn.example.org/vpn-user-portal/node-api.php
    {"error":"missing authentication information"}

This error is expected as no secret was provided. This just makes sure the 
controller is configured correctly and allows requests from the nodes.

Next, it is time to install the software. You should have downloaded and 
unpacked the archive already, see [Requirements](#Requirements).

    $ cd documentation-3
    $ sudo -s
    # ./deploy_debian_node.sh

The script will ask for the API URL and the _node key_. The API URL is the URL 
we tested above. The secret is the one extracted at the end of the previous 
section.

The script will output some errors about being unable to start OpenVPN. This is
because we changed the controller's default configuration. It is fine, we will
fix that shortly!

Modify `/etc/default/vpn-daemon`:

    LISTEN=:41194

Start/enable the daemon:

    $ sudo systemctl enable --now vpn-daemon

The firewall also requires tweaking, open it to allow traffic from the 
controller to the node's VPN daemon:

In `/etc/iptables/rules.v4`:

    -A INPUT -s 192.0.2.10/32 -p tcp -m state --state NEW -m tcp --dport 41194 -j ACCEPT

In `/etc/iptables/rules.v6`, if you prefer using IPv6:

    -A INPUT -s 2001:db8::10/128 -p tcp -m state --state NEW -m tcp --dport 41194 -j ACCEPT

Now you are ready to apply the changes and it should work without error:

    $ sudo vpn-maint-apply-changes

Restart the firewall:

    $ sudo systemctl restart netfilter-persistent

Make sure you repeat these steps on Node B as well!

Now is the time to test everything. Go to the portal at 
`https://vpn.example.org/`, download a configuration, test it with your 
client. Download a configuration for both profiles and make sure they work. 
Login to the admin portal using the `admin` user and password you noted at the
end of the controller install and make sure you see your client(s) under 
"Connections" in the portal when connected.

## TLS

When everything works properly using HTTP, you SHOULD switch to HTTPS for
communication between controller and node(s). Without TLS there is no
encryption and no authentication. Enabling TLS will fix this.

We'll create a tiny CA and issue server certificates for the node(s) and a 
client certificate for the controller. We use 
[vpn-ca](https://git.sr.ht/~fkooman/vpn-ca) which is already installed on 
your controller, but you can also download and install it on your own system.

```
$ vpn-ca -init-ca -name "Management CA" -domain-constraint .vpn.example.org
$ vpn-ca -server  -name node-a.vpn.example.org
$ vpn-ca -server  -name node-b.vpn.example.org

...

$ vpn-ca -client  -name vpn-daemon-client
```

Copy `ca.crt`, `node-X.vpn.example.org.crt` and `node-X.vpn.example.org.key` to
the respective node(s). Store them in `/etc/vpn-daemon` as `ca.crt`, 
`server.crt` and `server.key`. Make sure they can be read by the `vpn-daemon` 
process:

```
$ sudo -s
$ cd /etc/vpn-daemon
$ chmod 0640 *
$ chgrp vpn-daemon *
```

Modify `/etc/sysconfig/vpn-daemon` and enable the `CREDENTIALS_DIRECTORY` 
option:

```
CREDENTIALS_DIRECTORY=/etc/vpn-daemon
```

Now restart `vpn-daemon`:

```
$ sudo systemctl restart vpn-daemon
```

Repeat this on all your nodes.

On your controller(s) you copy the `ca.crt`, `vpn-daemon-client.crt` and 
`vpn-daemon-client.key` to `/etc/vpn-user-portal/vpn-daemon` and modify the
`nodeUrl` option(s) in the profile configuration in 
`/etc/vpn-user-portal/config.php` to `https://`.

Viewing the portal "Info" page should show your node(s) as green and have the 
lock icon visible. Now you are all good!

If there are any problems, review the `vpn-daemon` log on your node(s):

```
$ sudo journalctl -t vpn-daemon
```

If your daemon is running properly, you can try `curl` from your controller(s) 
to verify the TLS connection can be established:

```
$ curl \
    --cacert /etc/vpn-user-portal/vpn-daemon/ca.crt \
    --cert /etc/vpn-user-portal/vpn-daemon/vpn-daemon-client.crt \
    --key /etc/vpn-user-portal/vpn-daemon/vpn-daemon-client.key \
    https://node-a.vpn.example.org:41194/i/node 
```
