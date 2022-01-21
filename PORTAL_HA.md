# Introduction

This document explains how to run a "high available" and "redundant" setup.

It will explain how to store the application database inside 
[PostgreSQL](https://www.postgresql.org/) or [MariaDB](https://mariadb.org/) 
and the (browser) session information inside 
[memcached](https://www.memcached.org/) instead of the local file system. This 
is useful if you want to make the VPN service "high available" or provide load 
balancing between servers.
 
* **NOTE**: this ONLY applies to eduVPN/Let's Connect! 3.x!
* **NOTE**: do this ONLY for new servers, there is NO automatic migration from 
  SQLite to PostgreSQL/MariaDB!
* **NOTE**: you can use this if you want to deploy multiple portal instances 
  using the same storage backend;
* **NOTE**: your PostgreSQL/MariaDB setup should have higher availability than 
  your individual portal(s), otherwise this setup makes no sense;

If you take all this in consideration, see 
[Portal Configuration](#portal-configuration) on how to connect to your MariaDB
server. Make sure you replace the server location and credentials.

We assume you are using `deploy_fedora_v3_controller.sh` on all your 
controller(s) with the same domain name, e.g. `vpn.example.org` and will use 
"round robin" DNS or some other load balancing technology, e.g. a proxy. Again,
make sure this proxy has a higher availability than your VPN portal(s).

On your node(s) you run `deploy_fedora_v3_node.sh`.

# Database Configuration

See [this](DATABASE.md) on how to configure PostgreSQL or MariaDB.

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

Make sure you have the required PHP module installed for MariaDB/MySQL:

```
$ sudo dnf -y install php-pecl-memcached
```

If these modules were not yet installed, restart PHP:

```
$ sudo systemctl restart php-fpm
```

Modify the session configuration in `/etc/vpn-user-portal/config.php`:

```
    ...
    
    'Session' => [
        // Whether to use memcached for sessions
        // DEFAULT: false
        'useMemcached' => false,

        // list of memcached servers host:port
        // DEFAULT: []
        'memcachedServerList' => [
            'localhost:11211',
        ],
    ],

    ...
```

Make the following changes:

```
    'useMemcached' => true,
    'memcachedServerList' => ['p1.home.arpa:11211', 'p2.home.arpa:11211'],
```

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

