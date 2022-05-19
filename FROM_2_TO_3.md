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

When you already run Debian 11, make sure your system is fully up to date and 
freshly rebooted:

```
$ sudo vpn-maint-update-system
$ sudo reboot
```

Furthermore, we assume that you have documentation on the things you changed 
on your 2.x server installation, for example the TLS certificates.

## Backup

It is important to make backups of the configuration files and database as they 
will help you with configuring/restoring the 3.x server. Those files are:

* `/etc/vpn-user-portal/config.php`
* `/etc/vpn-server-api/config.php`
* `/etc/vpn-server-node/config.php`

As for the database files:

* `/var/lib/vpn-user-portal/db.sqlite`
* `/var/lib/vpn-server-api/db.sqlite`

Copy them to a safe location. If you made any other manual changes to any of 
the configuration files, you MUST make a backup of this file as well, e.g.:

* `/etc/apache2/sites-available/vpn.example.org.conf` (Apache)
* `/etc/iptables/rules.v4` (IPv4 firewall)
* `/etc/iptables/rules.v6` (IPv6 firewall)
* `/etc/sysctl.d/70-vpn.conf` (sysctl)

You MAY also want to backup your TLS key, certificate and chain if you are not
using Let's Encrypt or any other ACME capable certificate authority.

## Remove 2.x

Now we'll fully remove the 2.x software and deploy the 3.x server with the 
normal deploy script.

### Repository

Remove all files under `/etc/apt/sources.list.d` that reference eduVPN or Let's 
Connect!. Also remove the files under `/etc/apt/trusted.gpg.d` that are related 
to eduVPN.

### Software

Delete all the software we will replace when running the new deploy:

```
$ sudo apt remove --purge vpn-user-portal vpn-server-api vpn-server-node vpn-maint-scripts
$ sudo apt autoremove --purge
```

## Install 3.x

Now you are ready to follow the the [steps](DEPLOY_DEBIAN.md) to install 3.x.
Continue reading below on things you have to consider *after* deploying 3.x.

## Post Upgrade Steps

### Configuration

This section will help you convert your 2.x configuration to a 3.x 
configuration. We'll use the 2.x configuration to selectively update the 3.x 
configuration in the right place as needed. It is HIGHLY RECOMMENDED that you 
update the freshly installed configuration file selectively based on the 
instructions below.

In 3.x the _vpn-server-api_ component no longer exists, and thus the 
configuration that was previously spread out over _vpn-user-portal_ and 
_vpn-server-api_ are now consolidated in _vpn-user-portal_.

In 2.x some credentials were directly specified in the configuration files, 
this has been replaced by files in 3.x, so the configuration files no longer
contain secrets.

#### Profile Configuration

You can also compare the "Profile Configuration" documentation for 
[2.x](https://github.com/eduvpn/documentation/blob/v2/PROFILE_CONFIG.md) and 
[3.x](https://github.com/eduvpn/documentation/blob/v3/PROFILE_CONFIG.md) in 
case you want to clarify some of the options. For completeness sake, there is 
also a 
[list](https://github.com/eduvpn/vpn-server-api/blob/v2/CONFIG_CHANGES.md) of 
configuration changes for the 2.x server since the release of 2.0.0.

In 3.x the `vpnProfiles` key has been renamed to `ProfileList`. The `profileId`
is now an option inside the profile and no longer the array "key". The 
`profileNumber` is no longer needed. In 2.x the configuration looks like this
for example:

```
'vpnProfiles' => [
    'foo' => [
        'profileNumber' => 1,
        'displayName' => 'Foo Profile',
        ...
        ...
    ],
],
```

And in 3.x it will look like this, all other things equal:

```
'ProfileList' => [
    [
        'profileId' => 'foo',
        'displayName' => 'Foo Profile',
        ...
        ...
    ],
],
```

As for the individual options, the table below will help you make the 
conversion:

| Option (in 2.x)        | Type       | Option (in 3.x)                              | Type                 |
| ---------------------- | ---------- | -------------------------------------------- | -------------------- |
| `profileNumber`        | `int`      | _Obsolete_                                   | _N/A_                | 
| `displayName`          | `string`   | `displayName`                                | `string`             |
| `range`                | `string`   | `oRangeFour`                                 | `string`             |
| `range6`               | `string`   | `oRangeSix`                                  | `string`             |
| `hostName`             | `string`   | `hostName`                                   | `string`             |
| `listen`               | `string`   | `oListenOn`                                  | `string`             |
| `managementIp`         | `string`   | `nodeUrl`                                    | `string`             |
| `defaultGateway`       | `bool`     | `defaultGateway`                             | `bool`               |
| `blockLan`             | `bool`     | `oBlockLan`                                  | `bool`               |
| `routes`               | `string[]` | `routeList`                                  | `string[]`           |
| `dns`                  | `string[]` | `dnsServerList`                              | `string[]`           |
| `dnsDomain`            | `string`   | `dnsSearchDomainList`                        | `string[]`           |
| `dnsDomainSearch`      | `string[]` | `dnsSearchDomainList`                        | `string[]`           |
| `clientToClient`       | `bool`     | _Obsolete_                                   | _N/A_                |
| `enableLog`            | `bool`     | `oEnableLog`                                 | `bool`               |
| `enableAcl`            | `bool`     | _Obsolete_                                   | _N/A_                |
| `aclPermissionList`    | `string[]` | `aclPermissionList`                          | `string[]` or `null` |
| `vpnProtoPorts`        | `string[]` | `oUdpPortList`, `oTcpPortList`               | `int[]`              |
| `exposedVpnProtoPorts` | `string[]` | `oExposedUdpPortList`, `oExposedTcpPortList` | `int[]`              |
| `hideProfile`          | `bool`     | _Obsolete_                                   | _N/A_                |
| `tlsOneThree`          | `bool`     | _Obsolete_                                   | _N/A_                |
| `tlsProtection`        | `string`   | _Obsolete_                                   | _N/A_                | 

**NOTE**: `clientToClient` is now handled exclusively by the firewall on the 
VPN server.

#### Authentication

The authentication modules have been renamed:

| Name (in 2.x)              | Name (in 3.x)          |                                      |
| -------------------------- | ---------------------- | ------------------------------------ |
| `FormPdoAuthentication`    | `DbAuthModule`         | [Documentation](DB_AUTH.md)          |
| `FormLdapAuthentication`   | `LdapAuthModule`       | [Documentation](LDAP.md)             |
| `FormRadiusAuthentication` | `RadiusAuthModule`     | [Documentation](RADIUS.md)           |
| `MellonAuthentication`     | `MellonAuthModule`     | [Documentation](MOD_AUTH_MELLON.md)  |
| `ShibAuthentication`       | `ShibAuthModule`       | [Documentation](SHIBBOLETH_SP.md)    |
| `PhpSamlSpAuthentication`  | `PhpSamlSpAuthModule`  | [Documentation](PHP_SAML_SP.md)      |
| `ClientCertAuthentication` | `ClientCertAuthModule` | [Documentation](CLIENT_CERT_AUTH.md) |
| _N/A_                      | `OidcAuthModule`       | [Documentation](MOD_AUTH_OPENIDC.md) |

Please refer to the documentation links and compare your current authentication 
configuration with the 3.x documentation. There may be minor changes required,
but that should be rather obvious. The configuration file itself, i.e. 
`/etc/vpn-user-portal/config.php` should also be very helpful and contains 
information about all options.

#### Miscellaneous 

### Restore Local User Accounts

Using the `sqlite3` command line tool you can migrate your old users database
to the new server. Install the `sqlite3` package on Debian/Ubuntu, or the 
`sqlite` package on Fedora.

```
$ sudo sqlite3 /var/lib/vpn-user-portal/db.sqlite
```

Now _attach_ your 2.x database file:

```sql
ATTACH DATABASE /path/to/2.x/vpn-user-portal/db.sqlite AS v2;
```

Delete the user from your _new_ installation that were created during 
installation:

```sql
DELETE FROM main.local_users;
```

And migrate over the users from the 2.x database to the new one:

```sql
INSERT INTO main.local_users SELECT * FROM v2.users;
```

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
