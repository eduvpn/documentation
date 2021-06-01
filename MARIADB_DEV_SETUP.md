# Introduction

This instruction tells you how to store the VPN database inside MariaDB instead
of the default SQLite.

* **NOTE**: this ONLY applies to eduVPN/Let's Connect! 3.x!
* **NOTE**: do this ONLY for new servers, there is NO migration from SQLite to
MariaDB!
* **NOTE**: ONLY use MariaDB as a backend if you have a "high available" 
MariaDB/MySQL cluster that is redundant. There is no point in switching to 
MariaDB/MySQL on a single server, it will actually be slower!
* **NOTE**: these instructions are only for TESTING by installing a MariaDB 
server on your VPN server. You do NOT want this in production, but instead you
want a high available remote MariaDB/MySQL cluster!

If you take all this in consideration, see [#portal-configuration] on how to
connect to your cluster. For testing you can continue in the next paragraph.

# Installation

Follow the instructions below to configure your MariaDB server:

```
$ sudo dnf -y install mariadb-server
$ sudo systemctl start mariadb
$ sudo mysql_secure_installation
```

You can leave most things at their defaults, but set a root password when 
asked, you need it below.

# Database Configuration

Now you need to create a database for eduVPN/Let's Connect! and user / password 
to access the database.

```
$ mysql -u root -p
```

Provide the password, and run the following commands. Replace the name of the
database and user if you want. Make sure you choose your own password.

```
MariaDB [(none)]> CREATE DATABASE vpn;
MariaDB [(none)]> GRANT ALL PRIVILEGES ON vpn.* to vpn@localhost identified by 's3cr3t';
MariaDB [(none)]> FLUSH PRIVILEGES;
MariaDB [(none)]> QUIT
```

Now you should be able to connect to the database using your newly created 
account:

```
$ mysql vpn -u vpn -p
```

# Portal Configuration

Make sure you have the required PHP module installed for MariaDB/MySQL:

```
$ sudo dnf -y install php-mysqlnd
```

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
