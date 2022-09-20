# Introduction

Setting up multiple VPN nodes is one part of making the VPN service 
"High Available". The other is setting up a redundant portal. A complete 
overview of the options can be found [here](HA.md).

Setting up multiple nodes allows the "load" of the VPN service to be 
distributed over multiple (virtual) servers and avoid (extensive) downtime when 
one of the nodes goes down.

In this document we'll show how to deploy a VPN service that has one controller 
and three nodes. One node is located in Amsterdam, two in Frankfurt. This will
demonstrate all possible configuration scenarios.

Here, the VPN clients choosing "Amsterdam" will always connect to the 
same node (`ams1.vpn.example.org`), clients choosing "Frankfurt" will end up on 
one of the two nodes, either `fra1.vpn.example.org` or `fra2.vpn.example.org`, 
randomly selected when connecting to the VPN.

Of course your setup can also start with one controller and one node!

**NOTE**: the algorithm deciding which node the VPN client will connect to is 
currently very simple. It randomly picks one from the list of VPN nodes that is
up. In the future we envision also considering the "load" of the node before 
deciding.

## Requirements

In this scenario we require 4 machines (or VMs) running Debian >= 11. Ideally, 
nodes all have the same specifications.

All four need to be set up with static IP configurations and working DNS. Make 
sure all works properly before starting the setup. For example, our test 
deployment uses:

| Role          | DNS Host               | IPv4         | IPv6           |
| ------------- | ---------------------- | ------------ | -------------- |
| Controller    | `vpn.example.org`      | `192.0.2.10` | `2001:db8::10` |
| Node 0 (ams1) | `ams1.vpn.example.org` | `192.0.2.20` | `2001:db8::20` |
| Node 1 (fra1) | `fra1.vpn.example.org` | `192.0.2.30` | `2001:db8::30` |
| Node 2 (fra2) | `fra2.vpn.example.org` | `192.0.2.40` | `2001:db8::40` |

We will use NAT for IPv4 and IPv6 client traffic.

Perform these steps on the hosts:

```bash
$ curl -L -O https://github.com/eduvpn/documentation/archive/v3.tar.gz
$ tar -xzf v3.tar.gz
$ cd documentation-3
```

## Controller

On the controller host:

```bash
$ sudo -s
# ./deploy_debian_controller.sh
```

Make note of the user credentials that are printed at the end, you can use them 
to test your server!

After the controller is installed, make sure you'll get a valid TLS 
certificate, for example using the included `lets_encrypt_debian.sh` script:

```bash
$ sudo -s
# ./lets_encrypt_debian.sh
```

Now visit your site at https://vpn.example.org/. Make sure there is no TLS 
error and you can login with the credentials you noted before.

### Configuration

We'll modify `/etc/vpn-user-portal/config.php` and remove the existing 
"default" profile and replace it with our `ams` and `fra` profiles:

```php
'ProfileList' => [
    // Our Node in Amsterdam
    [
        'profileId' => 'ams',
        'displayName' => 'Amsterdam',
        'hostName' => 'ams1.vpn.example.org',
        'wRangeFour' => ['172.23.114.0/24', '10.123.94.0/24'],
        'wRangeSix' => ['fd36:2246:1d09:3014::/64', 'fdb6:21f2:f9c:34fb::/64'],
        'defaultGateway' => true,
        'dnsServerList' => ['9.9.9.9', '2620:fe::9'],
        'nodeUrl' => 'http://ams1.vpn.example.org:41194',
        'onNode' => 0,
    ],

    // Our Nodes in Frankfurt	
    [
        'profileId' => 'fra',
        'displayName' => 'Frankfurt',
        'hostName' => ['fra1.vpn.example.org', 'fra2.vpn.example.org'],
        'wRangeFour' => ['10.61.60.0/24', '10.7.192.0/24'],
        'wRangeSix' => ['fd85:f1d9:20b7:b74c::/64', 'fd89:79cb:b63c:717e::/64'],
        'defaultGateway' => true,
        'dnsServerList' => ['9.9.9.9', '2620:fe::9'],
        'nodeUrl' => ['http://fra1.vpn.example.org:41194', 'http://fra2.vpn.example.org:41194'],
        'onNode' => [1, 2],
    ],
],
```

If you want to generate your own random IPv4 and IPv6 prefixes to avoid 
"collisions" for use in the `wRangeFour` and `wRangeSix` configuration options, 
you can use `ipcalc-ng`:

| Address Family | Command                               |
| -------------- | ------------------------------------- |
| IPv4           | `ipcalc-ng -4 -r 24 -n --no-decorate` |
| IPv6           | `ipcalc-ng -6 -r 64 -n --no-decorate` |

See [Profile Config](PROFILE_CONFIG.md) for an explanation of what all the 
configuration options mean exactly.

Next, modify the `<Files node-api.php>` section in 
`/etc/apache2/conf-available/vpn-user-portal.conf` by adding the IP addresses 
of the nodes, make sure `Require ip` lists all the IP addresses, if you want 
to allow only 1 address use the `/32` prefix (IPv4) or `/128` (IPv6):

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

```bash
$ sudo systemctl restart apache2
```

For each node you want to add you need to generate a new "Node Key". By default 
we have one for node 0 (`ams1.vpn.example.org`), but we need keys for node 1 
and 2 (the two nodes in Frankfurt):

```bash
$ sudo /usr/libexec/vpn-user-portal/generate-secrets --node 1
$ sudo /usr/libexec/vpn-user-portal/generate-secrets --node 2
```

Copy the generated `node.0.key`, `node.1.key` and `node.2.key` to the 
respective nodes. We'll put them in the correct place in the next section.

## Nodes

The instructions below will be only shown for Node 0, but they are identical
for Node 1 and 2... You have to perform these instructions three times.

Make sure you can reach the API endpoint from the node(s):

```bash
$ curl https://vpn.example.org/vpn-user-portal/node-api.php
{"error":"authentication required"}
```

This error is expected as no secret was provided. This just makes sure the 
controller is configured correctly and allows requests from the nodes.

Next, it is time to install the software. You should have downloaded and 
unpacked the archive already, see [Requirements](#Requirements).

```bash
$ cd documentation-3
$ sudo -s
# ./deploy_debian_node.sh
```

On your node, modify `/etc/vpn-server-node/config.php`, set `apiUrl`, 
`nodeNumber` and `profileIdList`:

### Node 0

```php
<?php

return [
    'apiUrl' => 'https://vpn.example.org/vpn-user-portal/node-api.php',
    'nodeNumber' => 0,
    'profileIdList' => ['ams'],    
];
```

### Node 1

```php
<?php

return [
    'apiUrl' => 'https://vpn.example.org/vpn-user-portal/node-api.php',
    'nodeNumber' => 1,
    'profileIdList' => ['fra'],    
];
```

### Node 2

```php
<?php

return [
    'apiUrl' => 'https://vpn.example.org/vpn-user-portal/node-api.php',
    'nodeNumber' => 2,
    'profileIdList' => ['fra'],    
];
```

Next, modify `/etc/default/vpn-daemon`:

```
LISTEN=:41194
```

Restart the daemon:

```bash
$ sudo systemctl restart vpn-daemon
```

Copy the `node.0.key`, `node.1.key` and `node.2.key` on their respective nodes
to `/etc/vpn-server-node/keys/node.key`.

**NOTE**: make sure it only contains the secret and not a trailing return. If 
you are using copy/paste using this:

```bash
$ echo -n 'SECRET' | sudo tee /etc/vpn-server-node/keys/node.key
```

The firewall also requires tweaking, open it to allow traffic from the 
controller to the node's VPN daemon:

In `/etc/iptables/rules.v4`:

```
-A INPUT -s 192.0.2.10/32 -p tcp -m state --state NEW -m tcp --dport 41194 -j ACCEPT
```

In `/etc/iptables/rules.v6`, if you prefer using IPv6:

```
-A INPUT -s 2001:db8::10/128 -p tcp -m state --state NEW -m tcp --dport 41194 -j ACCEPT
```

Restart the firewall:

```bash
$ sudo systemctl restart netfilter-persistent
```

Now you are ready to apply the changes and this should work without error on 
all your nodes:

```bash
$ sudo vpn-maint-apply-changes
```

Make sure you repeat these steps on Node 1 and 2 as well!

**NOTE**: if you also run the [HA Portal](HA_PORTAL.md), you MUST synchronize
the `/var/lib/vpn-user-portal` folder again between the _n_ portals!

Now is the time to test everything. Go to the portal at 
`https://vpn.example.org/`, download a configuration and test it with your 
VPN client. Login with an account that has "Admin" privileges, and make sure 
you see your client(s) under "Connections" in the portal when connected.

## TLS

**NOTE**: these instructions are for Debian, not (yet) for Fedora or Enterprise
Linux!

When everything works properly using HTTP, you SHOULD switch to HTTPS for
communication between controller and node(s). Without TLS there is no
encryption and no authentication. Enabling TLS will fix this.

We'll create a tiny CA and issue server certificates for the node(s) and a 
client certificate for the controller. We use 
[vpn-ca](https://git.sr.ht/~fkooman/vpn-ca) which is already installed on 
your controller, but you can also download and install it on your own system.

```bash
$ vpn-ca -init-ca -name "Management CA" -domain-constraint .vpn.example.org
$ vpn-ca -server  -name node-a.vpn.example.org
$ vpn-ca -server  -name node-b.vpn.example.org

...

$ vpn-ca -client  -name vpn-daemon-client
```

Copy `ca.crt`, `node-X.vpn.example.org.crt` and `node-X.vpn.example.org.key` to
the respective node(s). Store them in the following locations (note the 
`private` folder for the key):

| File                         | Location                                 |
| ---------------------------- | ---------------------------------------- |
| `ca.crt`                     | `/etc/ssl/vpn-daemon/ca.crt`             | 
| `node-X.vpn.example.org.crt` | `/etc/ssl/vpn-daemon/server.crt`         |
| `node-X.vpn.example.org.key` | `/etc/ssl/vpn-daemon/private/server.key` |

Now, enable [System and Service Credentials](https://systemd.io/CREDENTIALS/)
by writing the following content to 
`/etc/systemd/system/vpn-daemon.service.d/credentials.conf`:

```
[Service]
LoadCredential=ca.crt:/etc/ssl/vpn-daemon/ca.crt
LoadCredential=server.crt:/etc/ssl/vpn-daemon/server.crt
LoadCredential=server.key:/etc/ssl/vpn-daemon/private/server.key
```

Make sure to reload the `systemd` daemon and restart `vpn-daemon`:

```bash
$ sudo systemctl daemon-reload
$ sudo systemctl restart vpn-daemon
```

Repeat this on all your nodes.

On your controller(s) you copy the `ca.crt`, `vpn-daemon-client.crt` and 
`vpn-daemon-client.key` to `/etc/vpn-user-portal/keys/vpn-daemon` and modify 
the `nodeUrl` option(s) in the profile configuration in 
`/etc/vpn-user-portal/config.php` to use `https://` instead of `http://`.

Viewing the portal "Info" page should show your node(s) as green and have the 
lock icon visible. Now you are all good!

If there are any problems, review the `vpn-daemon` log on your node(s):

```bash
$ sudo journalctl -t vpn-daemon
```

If your daemon is running properly, you can try `curl` from your controller(s) 
to verify the TLS connection can be established:

```bash
$ curl \
    --cacert /etc/vpn-user-portal/keys/vpn-daemon/ca.crt \
    --cert /etc/vpn-user-portal/keys/vpn-daemon/vpn-daemon-client.crt \
    --key /etc/vpn-user-portal/keys/vpn-daemon/vpn-daemon-client.key \
    https://node-a.vpn.example.org:41194/i/node 
```
