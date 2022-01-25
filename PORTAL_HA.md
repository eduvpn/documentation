# Introduction

The VPN service consists of two separate components:

1. Portal/Controller(s)
2. Node(s)

On default installations, using `deploy_${DIST}.sh` these two components are 
installed on the same server.

It is possible to split (both of them) and run them on multiple machines. The
reason for doing this are twofold:

1. Survive downtime when one of the Portal/Controller(s) goes down;
2. Scale up to many more VPN connections than can be handled by a single 
   machine

This document describes how to do (1), i.e. deploy multiple "Portal/Controller" 
machines. Deploying multiple "Nodes" to accomplish (2) is documented 
[here](MULTI_NODE.md).

For some organizations deploying the VPN service, solving (1) is not considered 
necessary because their virtual platform takes care of this to a satisfying 
degree. 

When deploying the VPN service you can choose to solve just (2), or both (1) 
and (2). In either case, the first step is always to deploy a separate 
"Portal/Controller" and "Node" on two different machines. We provide deployment 
scripts for this, i.e.`deploy_${DIST}_controller.sh` and 
`deploy_${DIST}_node.sh`.


If you want to service as many VPN users as possible we are talking about 
scalability. You can accomplish this by adding additional VPN nodes. We call
this "Multi Node" and is documented [here](MULTI_NODE.md).

If you want to make your VPN service as reliable as possible, i.e. being able
to "survive" downtime of one or more of the machines, 

# Memcached Installation

On all of your portal servers:

```
$ sudo dnf -y install memcached
$ sudo systemctl enable --now memcached
```

# Memcached Configuration

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

# Portal Configuration

Make sure you have the required PHP module installed for memcache:

```
$ sudo dnf -y install php-pecl-memcached
```

If this module were not yet installed, restart PHP:

```
$ sudo systemctl restart php-fpm
```

Modify the session configuration in `/etc/vpn-user-portal/config.php`:

```php
'sessionModule' => 'MemcacheSessionModule',
'MemcacheSessionModule' => [
    'serverList' => [
        'p1.home.arpa:11211', 
        'p2.home.arpa:11211'
    ]
],
```

FIXME: the below is not actually true
```
$ sudo vpn-maint-reset-system
```

This should not show any errors. When you now login to your portal all should
work. 

If you were using local users, you can add them again:

```
$ sudo -u apache vpn-user-portal-add-user
```

# Other Aspects

Some additional files need to be copied from one of the portals to the 
other(s), e.g. VPN CA, OAuth key, OpenVPN/WireGuard key material and HTTPS 
certificate.

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











Fedora 35

p1.home.arpa        Controller/Portal
p2.home.arpa        Controller/Portal
n1.home.arpa        OpenVPN/WG node
n2.home.arpa        OpenVPN/WG node
db.home.arpa        MariaDB server

# On the Portals

- install all updates
- reboot

sudo dnf -y install memcached
sudo systemctl enable --now memcached

hostnamectl set-hostname X.home.arpa

./deploy_fedora_v3_controller.sh

Use p.home.arpa as hostname in deploy script (shared between the portals)

    //    // MariaDB/MySQL
        'Db' => [
            'dbDsn' => 'mysql:host=db.home.arpa;port=3306;dbname=vpn',
            //'dbDsn' => mysql:unix_socket=/var/lib/mysql/mysql.sock;dbname=vpn',
            'dbUser' => 'vpn',
            'dbPass' => 's3cr3t',
        ],


        'Session' => [
    //        // Whether to use memcached for sessions
    //        // DEFAULT: false
            'useMemcached' => true,

    //        // list of memcached servers host:port
    //        // DEFAULT: []
            'memcachedServerList' => [
                'p1.home.arpa:11211',
		'p2.home.arpa:11211',
            ],
        ],


## CA 

[fkooman@fralen-tuxed-net tmp-ca]$ vpn-ca -init-ca -domain-constraint .home.arpa
[fkooman@fralen-tuxed-net tmp-ca]$ vpn-ca -server -name p.home.arpa


httpd

		Require host n1.home.arpa
		Require host n2.home.arpa




# On the Nodes


# DB

- install all updates
- reboot

sudo dnf -y install mariadb-server



Fedora 35

p1.home.arpa        Controller/Portal
p2.home.arpa        Controller/Portal
n1.home.arpa        OpenVPN/WG node
n2.home.arpa        OpenVPN/WG node
db.home.arpa        MariaDB server

# On the Portals

- install all updates
- reboot

sudo dnf -y install memcached
sudo systemctl enable --now memcached

hostnamectl set-hostname X.home.arpa

./deploy_fedora_v3_controller.sh

Use p.home.arpa as hostname in deploy script (shared between the portals)

    //    // MariaDB/MySQL
        'Db' => [
            'dbDsn' => 'mysql:host=db.home.arpa;port=3306;dbname=vpn',
            //'dbDsn' => mysql:unix_socket=/var/lib/mysql/mysql.sock;dbname=vpn',
            'dbUser' => 'vpn',
            'dbPass' => 's3cr3t',
        ],


        'Session' => [
    //        // Whether to use memcached for sessions
    //        // DEFAULT: false
            'useMemcached' => true,

    //        // list of memcached servers host:port
    //        // DEFAULT: []
            'memcachedServerList' => [
                'p1.home.arpa:11211',
		'p2.home.arpa:11211',
            ],
        ],


## CA 

[fkooman@fralen-tuxed-net tmp-ca]$ vpn-ca -init-ca -domain-constraint .home.arpa
[fkooman@fralen-tuxed-net tmp-ca]$ vpn-ca -server -name p.home.arpa


httpd

		Require host n1.home.arpa
		Require host n2.home.arpa




# On the Nodes


# DB

- install all updates
- reboot

sudo dnf -y install mariadb-server

