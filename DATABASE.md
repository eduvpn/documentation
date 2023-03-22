# Database

The VPN server supports other databases than just the default 
[SQLite](https://sqlite.org/). For SQLite, no configuration is needed, it works 
out of the box. If you are happy with that, there is no need to read this 
document.

**NOTE (1)**: only consider switching databases if your database has a higher 
reliability than your systems on which you host the VPN server, and you want to 
run a [HA](HA_PORTAL.md) setup.

**NOTE (2)**: this document only explains how to _use_ another database, it 
does NOT explain how to run reliably database infrastructure! The document 
_does_ provide database server installation/configuration instructions to the 
level needed to _test_ the different database backends. This is NOT suitable
for production as-is!

**NOTE (3)**: if you can choose, we recommend you use PostgreSQL and not 
MariaDB/MySQL.

**NOTE (4)**: we assume you used `deploy_${DIST}_controller.sh` and 
`deploy_${DIST}_node.sh` to install the VPN service.

## Configuration

You can configure the database in `/etc/vpn-user-portal/config.php`, replace 
the `host`, `dbname` with the values obtained from your database administrator. 

### PostgreSQL

Make sure you have the `php-pgsql` package installed, on Debian use `apt` 
instead of `dfn`:

```bash
$ sudo dnf install php-pgsql
```

In `/etc/vpn-user-portal/config.php`:

```php
    'Db' => [
        'dbDsn' => 'pgsql:host=db.example.org;dbname=vpn;user=vpn;password=s3cr3t',
    ],
```

Replace `host`, `dbname`, `user` and `password` with the values you obtained 
from your database administrator.

### MariaDB/MySQL

Make sure you have the `php-mysqlnd` package installed:

```bash
$ sudo dnf install php-mysqlnd
```

In `/etc/vpn-user-portal/config.php`:

```php
    'Db' => [
	    'dbDsn' => 'mysql:host=db.example.org;dbname=vpn',
	    'dbUser' => 'vpn',
	    'dbPass' => 's3cr3t',
    ],
```

Replace `host`, `dbname`, `dbUser` and `dbPass` with the values you obtained 
from your database administrator.

### Database Info

You can show the current status of your database, this will tell you whether 
the configuration was done properly, i.e. we are able to connect to the 
database and whether initialization or migration is required, e.g.:

```bash
$ sudo /usr/libexec/vpn-user-portal/db
Current Schema Version : 2022010202
Required Schema Version: 2022010202
Status                 : **OK**
```

### Database Initialization

If you need to initialize the database:

```bash
$ sudo /usr/libexec/vpn-user-portal/db --init
```

You can override your database configuration with `--dsn`, `--user`, `--pass` 
options in case you need different credentials to perform a database 
initialization.

### Database Migration

Updates to the VPN software MAY require database migrations. This will be 
indicated in the release notes of newer versions.

You can perform the migration:

```bash
$ sudo /usr/libexec/vpn-user-portal/db --migrate
```

You can override your database configuration with `--dsn`, `--user`, `--pass` 
options in case you need different credentials to perform a database 
migration.

If a migration is needed, but not performed the VPN portal will give a clear 
error message.

### Manual Initialization / Migration

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

## Database Server Installation

As mentioned above, this is only for testing!

### PostgreSQL Installation

#### Fedora

```
$ sudo dnf -y install postgresql-server 
$ sudo postgresql-setup --initdb
```

#### Debian

```
$ sudo apt -y install postgresql 
```

### PostgreSQL Configuration

First we'll allow password authentication. Modify 
`/var/lib/pgsql/data/pg_hba.conf`. On Debian this is 
`/etc/postgresql/13/main/pg_hba.conf`. Add these lines:

```
host    all             all             127.0.0.1/32            scram-sha-256
host    all             all             ::1/128                 scram-sha-256
```

**NOTE**: make sure these rows are placed *above* the lines that have `METHOD` 
with value `ident`, or replace the ones with `ident` in them.

Replace `127.0.0.1/32` and `::1/128` with the IP(v6) prefixes where the 
PostgreSQL "client" is coming from if you run PostgreSQL on a separate system.

Also modify `/var/lib/pgsql/data/postgresql.conf` 
(or `/etc/postgresql/13/main/postgresql.conf` on Debian) and set:

```
password_encryption = scram-sha-256
```

Also modify the `listen_addresses` option if you want to allow connecting 
from a remote system, e.g.:

```
#listen_addresses = 'localhost'
listen_addresses = '*'
```

Now, start (and auto start on boot) PostgreSQL, on Debian it was auto started, 
so you only need to restart it:

```
$ sudo systemctl enable postgresql
$ sudo systemctl restart postgresql
```

In order to create a database, we need to execute the `createuser` command as
`postgres` user:

```
$ sudo su -l postgres 
$ createuser -d -P vpn
Enter password for new role: 
Enter it again: 
$ exit
```

The `-d` option will allow the user to create databases. The `-P` option will 
ask immediately to specify a password. Provide one!

Create the database:

```
$ createdb -h localhost -U vpn vpn
```

This will ask for the password, provide it. The database will be created. Test
whether you can connect to the database:

```
$ psql -h localhost -U vpn
Password for user vpn: 
psql (13.4)
Type "help" for help.

vpn=> 
```

All good!

## MariaDB Installation

Follow the instructions below to configure your MariaDB server:

```
$ sudo dnf -y install mariadb-server
$ sudo systemctl enable --now mariadb
$ sudo mysql_secure_installation
```

You can leave most things at their defaults, but set a `root` password when 
asked, you will need it below.

### MariaDB Configuration

Now you need to create a database and a user with a password.

```
$ mysql -u root -p
```

Provide the `root` password, and run the following commands. Replace the name 
of the database and user if you want. Make sure you choose your own password.

#### Local Access

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

#### Remote Access

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
