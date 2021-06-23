# Introduction

**WORK IN PROGRESS**

**TODO**: think about storing keys/CA in the database instead, would make it 
much easier and no need to keep them manually synchronized...

This document tells you how to store the application database inside 
[MariaDB](https://mariadb.org/) and the (browser) session information inside 
[memcached](https://www.memcached.org/) instead of the local file system. This 
is useful if you want to make the VPN service "high available" or provide load 
balancing between servers. When we mention MariaDB below, the same should apply 
to MySQL as well.
 
* **NOTE**: this ONLY applies to eduVPN/Let's Connect! 3.x!
* **NOTE**: do this ONLY for new servers, there is NO migration from SQLite to
  MariaDB!
* **NOTE**: you can use this if you want to deploy multiple portal instances 
  using the same storage backend;
* **NOTE**: your MariaDB setup should have higher availability than your 
  individual portal(s) otherwise this setup makes no sense;

These instructions tell you how to setup a simple MariaDB server. This is by 
no means complete and MUST NOT be used in production like this. Please talk to
your local database expert first! It will also document how to configure 
Memcached on your portal machines to share the (browser) session information.

If you take all this in consideration, see 
[Portal Configuration](#portal-configuration) on how to connect to your MariaDB
server. Make sure you replace the server location and credentials.

We assume you are using `deploy_fedora_v3.sh` on all your portals with the same
domain name, e.g. `vpn.example.org` and will use "round robin" DNS for HA / 
load balancing.

# MariaDB Installation

Follow the instructions below to configure your MariaDB server:

```
$ sudo dnf -y install mariadb-server
$ sudo systemctl enable --now mariadb
$ sudo mysql_secure_installation
```

You can leave most things at their defaults, but set a `root` password when 
asked, you will need it below.

# MariaDB Configuration

Now you need to create a database and a user with a password.

```
$ mysql -u root -p
```

Provide the `root` password, and run the following commands. Replace the name 
of the database and user if you want. Make sure you choose your own password.

## Local Access

```
MariaDB [(none)]> CREATE DATABASE vpn;
MariaDB [(none)]> GRANT ALL PRIVILEGES ON vpn.* to vpn@localhost IDENTIFIED BY 's3cr3t';
MariaDB [(none)]> FLUSH PRIVILEGES;
MariaDB [(none)]> QUIT
```

Now you should be able to connect to the database using your newly created 
account:

```
$ mysql vpn -u vpn -p
```

## Remote Access

```
MariaDB [(none)]> CREATE DATABASE vpn;
MariaDB [(none)]> GRANT ALL PRIVILEGES ON vpn.* to vpn@'%' IDENTIFIED BY 's3cr3t';
MariaDB [(none)]> FLUSH PRIVILEGES;
MariaDB [(none)]> QUIT
```

Now you should be able to connect to your database server from your VPN portal
using your newly created account:

```
$ mysql vpn -h db.example.org -u vpn -p
```

**NOTE**: you MUST make sure only your VPN portals can reach MariaDB and not
the complete Internet! It seems by default MariaDB listens in `:::3306` which
means all interfaces (both IPv4 and IPv6). You MUST firewall this port and 
restrict access to your VPN portals only!

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

# Portal Configuration

Make sure you have the required PHP module installed for MariaDB/MySQL:

```
$ sudo dnf -y install mariadb php-mysqlnd php-pecl-memcached
```

Modify the PHP session configuration in `/etc/php-fpm.d/www.conf`, find the
lines that refer to PHP sessions:

```
php_value[session.save_handler] = files
php_value[session.save_path]    = /var/lib/php/session
```

Replace them with this:

```
php_value[session.save_handler]              = memcached
php_value[session.save_path]                 = "10.5.5.1:11211,10.5.5.2:11211"
php_value[memcached.sess_number_of_replicas] = 1
```

Where `10.5.5.1` and `10.5.5.2` are the (private) IP addresses of your VPN 
portals. The `memcached.sess_number_of_replicas` value is one less than the 
number of Memcached servers, i.e. portals you setup.

Restart PHP:

```
$ sudo systemctl restart php-fpm
```

Now you can configure the portal by modifying 
`/etc/vpn-user-portal/config.php` and add the following section:

```
...

'Db' => [
	'dbDsn' => 'mysql:host=localhost;dbname=vpn',
	'dbUser' => 'vpn',
	'dbPass' => 's3cr3t',
],

...
```

Now you should be able to "reset" the server and use the MariaDB server:

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
