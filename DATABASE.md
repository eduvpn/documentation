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

## Database Info

You can show the current status of your database:

```bash
$ /usr/libexec/vpn-user-portal/db
```

This will tell you whether initialization or migration is required, e.g.:

```bash
$ /usr/libexec/vpn-user-portal/db
Current Schema Version : 2022010202
Required Schema Version: 2022010202
Status                 : **OK**
```

## Database Initialization

If you need to initialize the database:

```bash
$ /usr/libexec/vpn-user-portal/db --init
```

You can override your database configuration with `--dsn`, `--user`, `--pass` 
options in case you need different credentials to perform a database 
initialization.

## Database Migration

Updates to the VPN software MAY require database migrations. This will be 
inidicated in the release notes of newer versions.

You can perform the migration:

```bash
$ /usr/libexec/vpn-user-portal/db --migrate
```

You can override your database configuration with `--dsn`, `--user`, `--pass` 
options in case you need different credentials to perform a database 
migration.

If a migration is needed, but not performed the VPN portal will give a clear 
error message. 

## Manual Initialization / Migration

If you really want to perform every step manually, you need to look in 
`/usr/share/vpn-user-portal/schema` for the SQL schema files. The latest 
version available there SHOULD be used for initialization, the files with `_` 
are the migration queries that need to be run to migrate from one version to 
the next.

**NOTE**: make sure you also create/update the `version` table that contains 
the current version, e.g.:

```sql
CREATE TABLE version (current_version TEXT NOT NULL);
INSERT INTO version VALUES('2021123001');
```
