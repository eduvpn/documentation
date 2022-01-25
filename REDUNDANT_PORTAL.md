# Introduction

In order to make the "Controller / Portal" redundant we have to go through a 
few steps:

1. Install the portal on >= 1 systems;
2. Obtain credentials for a remote database cluster;
3. Configure the database;
4. Synchronize the configuration between;
5. Setup memcache;

# Installation

You can configure the "Controller / Portal" on multiple systems, using the 
`deploy_${DIST}_controller.sh`, and your node(s) using 
`deploy_${DIST}_node.sh`.

Make sure you provide the same hostname when asked when running the deploy 
script, e.g. `vpn.example.org`.

The machines themselves can have the names `p1.vpn.example.org`, 
`p2.vpn.example.org`, ..., or whatever fits for your situation.

You perform all configuration on one of the "Controllers / Portal", and then 
simple copy the configuration / data to the other(s).

# Database

In order to configure the database, perform that from one of the portals you 
just set up and follow the instructions [here](DATABASE.md).

# Memcached

On all of your "Controller / Portal" machines:

```
$ sudo dnf -y install memcached php-pecl-memcached
$ sudo systemctl enable --now memcached
$ sudo systemctl restart php-fpm
```

## Configuration

By default Memcached only listens on `localhost`. For our purpose however each
installation of the portal should be able to reach all Memcached servers. 

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

# Synchronize Configuration

Some files need to be copied from one of the portals to the other(s), e.g. VPN 
CA, OAuth key, OpenVPN/WireGuard key material and HTTPS certificate.

**TODO**: not all file locations are correct yet!

Copy the following files/folders from one of your portals to the other(s):

* File `/etc/vpn-user-portal/config.php`;
* File `/etc/vpn-user-portal/oauth.key`;
* Folder `/var/lib/vpn-user-portal`;

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

`p1.vpn.example.org` in `/etc/keepalived/keepalived.conf`:

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

`p2.vpn.example.org` in `/etc/keepalived/keepalived.conf`:


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
```

Enable/start on both systems:

```bash
$ sudo systemctl enable --now keepalived
```

Update firewall on both, **NOTE**: set the exact IP address:

```
-A INPUT -s 192.168.122.0/24 -p vrrp -j ACCEPT
```

## CA 

[fkooman@fralen-tuxed-net tmp-ca]$ vpn-ca -init-ca -domain-constraint .home.arpa
[fkooman@fralen-tuxed-net tmp-ca]$ vpn-ca -server -name p.home.arpa

# On the Nodes

# DB

- install all updates
- reboot

sudo dnf -y install mariadb-server
