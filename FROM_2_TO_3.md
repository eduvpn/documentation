This document will help you migrate your existing server from eduVPN / Let's 
Connect! 2.x to 3.x.

## Limitations

All your users will need to reauthorize their eduVPN / Let's Connect! 
applications with your server and/or re-download the configurations files they 
manually got through the portal once the upgrade is complete.

## Requirements

You MUST be running the server on Debian 11, if you are not running on Debian 
11, but on a previous version of Debian, follow the instructions here first:

* [Debian 9 to Debian 10](https://github.com/eduvpn/documentation/blob/v2/UPGRADE_DEBIAN_9_TO_10.md);
* [Debian 10 to Debian 11](https://github.com/eduvpn/documentation/blob/v2/UPGRADE_DEBIAN_10_TO_11.md)

You probably have to go first from Debian 9 to 10 and then to 11 if you are 
still running Debian 9. If you try to go in 1 step, be extra careful and read
all upgrade instructions carefully to make sure this is actually possible.

When you already run Debian 11, make sure your system is fully update to date
and freshly rebooted:

```
$ sudo vpn-maint-update-system
$ sudo reboot
```

Furthermore, we assume that you have documentation on the things you changed 
on your 2.x server installation, for example the TLS certificates.

## Backup

It is important to make backups of the configuration files as they will help 
you with configuring the 3.x server. Those files are:

* `/etc/vpn-user-portal/config.php`
* `/etc/vpn-server-api/config.php`
* `/etc/vpn-server-node/config.php`

Copy them to a safe location. If you made any other manual changes to any of 
the configuration files, you MUST make a backup of this file as well, e.g.:

* `/etc/apache2/sites-available/vpn.example.org.conf` (Apache)
* `/etc/iptables/rules.v4` (IPv4 firewall)
* `/etc/iptables/rules.v6` (IPv6 firewall)
* `/etc/sysctl.d/70-vpn.conf` (sysctl)

If you are using the local user database, you will lose the accounts defined 
there, so you MUST now create a backup of those accounts:

```
$ sudo apt install sqlite3
$ sudo sqlite3 /var/lib/vpn-user-portal/db.sqlite ".dump users"
```

Store the output for later as you will need it to restore the accounts!

## Remove 2.x

No we'll fully remove the 2.x software and deploy the 3.x server with the 
normal deploy script.

### Repository

Remove all files under `/etc/apt/sources.list.d` that reference eduVPN of Let's 
Connect!. Also remove the files under `/etc/apt/trusted.gpg.d` that are related 
to eduVPN.

### Software

Delete all the software we will replace when running the new deploy:

```
$ sudo apt remove --purge vpn-user-portal vpn-server-api vpn-server-node vpn-maint-scripts
$ sudo apt autoremove --purge
```

## Install 3.x

This should have taken care of removing everything from 2.x. 

Now you are ready to follow the the [steps](DEPLOY_DEBIAN.md) to install 3.x.
Continue reading below on things you have to consider *after* deploying 3.x.

## Post Upgrade Steps

### Restore Local User Accounts

TBD.

### php-saml-sp

The [php-saml-sp](https://www.php-saml-sp.eu/) software used to be part of the 
eduVPN / Let's Connect! repository, but is NOT anymore. So if you want to keep 
using it, you MUST upgrade to the latest version. Fortunately, there are no 
configuration changes required and all that is needed is to perform the 
upgrade.

Add the new repository:

```
$ curl https://repo.php-saml-sp.eu/fkooman+repo@tuxed.net.asc | sudo tee /etc/apt/trusted.gpg.d/fkooman+repo@tuxed.net.asc
$ echo "deb https://repo.php-saml-sp.eu/v2/deb bullseye main" | sudo tee /etc/apt/sources.list.d/php-saml-sp_v2.list
```

Perform the upgrade:

```
$ sudo apt update
$ sudo apt dist-upgrade
```

The latest version makes some dependencies obsolete that can now be deleted as
well:

```
$ sudo apt autoremove --purge
```
