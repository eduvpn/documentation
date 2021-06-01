# Introduction

This instruction tells you how to store the VPN database inside MySQL/MariaDB 
instead of the default SQLite. We will demonstrate with a MariaDB server only,
but MySQL should be similar.

* **NOTE**: this ONLY applies to eduVPN/Let's Connect! 3.x!
* **NOTE**: do this ONLY for new servers, there is NO migration from SQLite to
  MariaDB!
* **NOTE**: you can use this if you want to deploy multiple portal instances 
  using the same storage backend;
* **NOTE**: your MariaDB setup should have higher availability than your 
  portal(s) otherwise it makes no sense;

These instructions tell you how to setup a simple MariaDB server. This is by 
no means complete and MUST NOT be used in production like this. Please talk to
your local database expert first!

If you take all this in consideration, see 
[Portal Configuration](#portal-configuration) on how to connect to your MariaDB
server. Make sure you replace the server location and credentials.

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

```
MariaDB [(none)]> CREATE DATABASE vpn;
MariaDB [(none)]> GRANT ALL PRIVILEGES ON vpn.* to vpn@localhost IDENTIFIED BY 's3cr3t';
MariaDB [(none)]> FLUSH PRIVILEGES;
MariaDB [(none)]> QUIT
```

If you want to allow remote connections, you can use the following `GRANT`:

```
MariaDB [(none)]> GRANT ALL PRIVILEGES ON vpn.* to vpn@'%' IDENTIFIED BY 's3cr3t';
```

Now you should be able to connect to the database using your newly created 
account:

```
$ mysql vpn -u vpn -p
```

Or when connecting to a remote server:

```
$ mysql vpn -h db.example.org -u vpn -p
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
