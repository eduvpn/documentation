# Introduction

Setting up a redundant portal is one part of making the VPN service 
"High Available". The other is running multiple VPN nodes. A complete 
overview of the options can be found [here](HA.md).

In order to make the "Controller / Portal" redundant we have to go through a 
few steps:

1. Install the controller/portal on >= 1 systems
2. Obtain credentials for a remote database cluster
3. Configure the database
4. Synchronize the configuration between the portals
5. Setup memcache
6. Setup keepalived

We'll walk you through all steps in the rest of this document.

# Installation

You can configure the "Controller / Portal" on multiple systems, using the 
`deploy_${DIST}_controller.sh`, and your node(s) using 
`deploy_${DIST}_node.sh`.

Make sure you provide the same hostname when asked when running the deploy 
script, e.g. `vpn.example.org`.

The machines themselves SHOULD have the names `p1.vpn.example.org`, 
`p2.vpn.example.org`, ..., or whatever fits for your situation.

You perform all configuration on one of the "Controllers / Portal", and then 
simple copy the configuration / data to the other(s).

# Database

In order to configure the database, perform that from one of the portals you 
just set up and follow the instructions [here](DATABASE.md).

# Memcached

On all of your "Controller / Portal" machines:

```
$ sudo apt -y install memcached php-memcached
$ sudo systemctl restart php$(/usr/sbin/phpquery -V)-fpm
```

## Configuration

By default Memcached only listens on `localhost`. For our purpose however each
installation of the portal should be able to reach all Memcached servers. 

### Debian / Ubuntu

Modify `/etc/memcached.conf` and change the `-l` line from `-l 127.0.0.1` to
`-l 0.0.0.0,::`

Restart memcached:

```
$ sudo systemctl restart memcached
```

**NOTE**: you MUST make sure you use your firewall to prevent systems on the 
Internet from reaching your Memcached service!

### Fedora 

Modify `/etc/sysconfig/memcached` and change the `OPTIONS` line from 
`OPTIONS="-l 127.0.0.1,::1"` to `OPTIONS=""` to listen on all interfaces.

**NOTE**: you MUST make sure you use your firewall to prevent systems on the 
Internet from reaching your Memcached service! An even better solution would be
to create a (virtual) private network between your portal servers and bind to 
the IP address of those interfaces, e.g. `OPTIONS="-l 10.5.5.1"`.

Restart Memcached:

```
$ sudo systemctl restart memcached
```

**NOTE** when specifying other IP addresses, Memcached MAY fail to start 
because the network is not "up" yet when trying to bind to the specified IP
addresses. In order to fix this:

```
$ sudo systemctl edit --full memcached.service
```

Change `After=network.target` to `After=network-online.target`. Then restart
Memcache again:

```
$ sudo systemctl restart memcached
```

### Portal

Modify the session configuration in `/etc/vpn-user-portal/config.php`:

```php
'sessionModule' => 'MemcacheSessionModule',
'MemcacheSessionModule' => [
    'serverList' => [
        'p1.vpn.example.org:11211', 
        'p2.vpn.example.org:11211',
    ],
],
```

**NOTE**: on `p1.vpn.example.org`, the server `p1.vpn.example.org` SHOULD come
first, and on `p2.vpn.example.org`, the server `p2.vpn.example.org` SHOULD come
first.

# Synchronize Configuration

Some files need to be copied from one of the portals to the other(s), e.g. VPN 
CA, OAuth key, OpenVPN/WireGuard key material and HTTPS certificate.

**TODO**: not all file locations are correct yet!

Copy the following folders from one of your portals to the other(s):

* Folder `/etc/vpn-user-portal`
* Folder `/var/lib/vpn-user-portal`

When making changes to your (portal) configuration, i.e. adding or removing 
profiles, these files/folders will need to be synchronized again!

You'll also need to copy the TLS certificate used by the portal's web server to
be the same on all portals. Make sure you also update 
`/etc/httpd.conf/vpn.example.org.conf` (where `vpn.example.org` is your domain)
to point to the correct certificate.

If you are using 
[Let's Encrypt](https://letsencrypt.org/) you can copy the entire 
`/etc/letsencrypt` folder to your other portals. Make sure you do this at least
every 90 days (the expiry of Let's Encrypt certificates)!

# keepalived

Install `keepalived`:

```bash
$ sudo apt install keepalived
```

On `p1.vpn.example.org` in `/etc/keepalived/keepalived.conf`:

```
vrrp_instance VI_1 {
        state MASTER
        interface eth0
        virtual_router_id 51
        priority 255
        advert_int 1
        authentication {
              auth_type PASS
              auth_pass 12345
        }
        virtual_ipaddress {
              192.168.122.99/24
        }
}

vrrp_instance VI_6 {
        state MASTER
        interface eth0
        virtual_router_id 56
        priority 255
        advert_int 1
        authentication {
              auth_type PASS
              auth_pass 12345
        }
        virtual_ipaddress {
              fd7f:aaec:599a:204::99/64
        }
}
```

On `p2.vpn.example.org` in `/etc/keepalived/keepalived.conf`:


```
vrrp_instance VI_1 {
        state BACKUP
        interface eth0
        virtual_router_id 51
        priority 254
        advert_int 1
        authentication {
              auth_type PASS
              auth_pass 12345
        }
        virtual_ipaddress {
              192.168.122.99/24
        }
}

vrrp_instance VI_6 {
        state BACKUP
        interface eth0
        virtual_router_id 56
        priority 255
        advert_int 1
        authentication {
              auth_type PASS
              auth_pass 12345
        }
        virtual_ipaddress {
              fd7f:aaec:599a:204::99/64
        }
}
```

Make sure you update the `interface` if required, it is not always `eth0`, but
depends on your (VM) platform.

Enable/start on both systems:

```bash
$ sudo systemctl enable --now keepalived
```

Update firewall on both, **NOTE**: set the exact IP address(es) of the other 
portal servers:

```
-A INPUT -s 192.168.122.0/24 -p vrrp -j ACCEPT
```

See also: 

* https://www.redhat.com/sysadmin/ha-cluster-linux
* https://www.redhat.com/sysadmin/keepalived-basics
* https://www.redhat.com/sysadmin/advanced-keepalived

