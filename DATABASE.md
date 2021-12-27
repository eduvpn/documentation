# Introduction

The VPN server supports various databases. The default is 
[SQLite](https://sqlite.org/).

For SQLite, no configuration is needed, it will work out of the box.

We'll describe how to configure [MariaDB](https://mariadb.org/), however the
same will work for MySQL.

We also support [PostgreSQL](https://www.postgresql.org/), but it receives less
testing.

We assume you used `deploy_${DIST}.sh` to install the VPN service.

**NOTE**: this document only explains how to install a *basic* MariaDB. You 
**SHOULD** be very familiar with MariaDB/MySQL before attemping this! If you 
are not, please stay with the default SQLite database!

# Installation

We'll show how to install MariaDB on Fedora. Other distributions are very 
similar. We assume how to "convert" these instructions to your relevant 
platform. If you can not do that, you should probably not be reading this 
document!

## MariaDB Installation

Follow the instructions below to configure your MariaDB server:

```
$ sudo dnf -y install mariadb-server
$ sudo systemctl enable --now mariadb
$ sudo mysql_secure_installation
```

You can leave most things at their defaults, but set a `root` password when 
asked, you will need it below.

## MariaDB Configuration

Now you need to create a database and a user with a password.

```
$ mysql -u root -p
```

Provide the `root` password, and run the following commands. Replace the name 
of the database and user if you want. Make sure you choose your own password.

### Local Access

If you install the MariaDB on the same system as your VPN service, run the 
following commands:

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

### Remote Access

If you install the MariaDB on a different system from your VPN service, as you
SHOULD, run the following commands:

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

# Configuration

You can configure the database in `/etc/vpn-user-portal/config.php`:

```php
    ...

    'Db' => [
	    'dbDsn' => 'mysql:host=db.example.org;dbname=vpn',
	    'dbUser' => 'vpn',
	    'dbPass' => 's3cr3t',
    ],

    ...
```

After changing the configuration, try to access the VPN portal. This SHOULD
automatically create the tables in your MariaDB server and migrate the database
schema to a newer version (if necessary).

## Manual Database Initialization & Migration

You can disable this automatic initialiation and migration behavior by setting 
the `autoInitMigrate` option to `false` under the `Db` section in 
`/etc/vpn-user-portal/config.php`. This may be necessary if the account 
accessing your MariaDB server does not have the required permissions to 
`CREATE` or `ALTER` tables.

You can still (manually) trigger the initialization/migration by calling:

```bash
$ /usr/libexec/vpn-user-portal/db-update
```

This of course requires adequate permissions on the database. If you really 
want to perform every step manually, you need to look in 
`/usr/share/vpn-user-portal/schema` for the migration SQL scripts. Make sure 
you also set the correct schema version in the `version` table after you 
performed the migrations!
