# LDAP

This document describes how to configure LDAP. We assume you used the 
`deploy_${DIST}.sh` script to deploy the software.

The LDAP integration can be used both for _authentication_ and _authorization_.

This document talks about _authentication_. See [ACL](ACL.md) for more on 
_authorization_.

**NOTE**: from version 3.4.0 of `vpn-user-portal`, the `userIdAttribute` key 
MUST be set, it is no longer optional.

## Introduction

In order to configure LDAP on your VPN server for authentication it is a good 
idea to start with `ldapsearch` if you are not absolutely sure what to 
configure. Once `ldapsearch` works, it becomes easier to configure the LDAP
module.

First, install `ldapsearch` and the PHP module for LDAP:

```bash
$ sudo dnf install openldap-clients php-ldap  # Fedora / EL
$ sudo apt install ldap-utils php-ldap        # Debian / Ubuntu
```

Restart PHP to activate the LDAP module:

```
$ sudo systemctl restart php-fpm                            # Fedora / EL
$ sudo systemctl restart php$(/usr/sbin/phpquery -V)-fpm    # Debian / Ubuntu
```
 
You need a couple of details first, you can obtain those from your LDAP 
administrator, you need _at least_:

* LDAP host;
* The attribute to use for user authentication;
* Whether or not this attribute is part of the user's DN.

### FreeIPA

For simple [FreeIPA](https://www.freeipa.org/page/Main_Page) setups these are
sufficient. Here the `uid` we want to use for users to authenticate is part of 
the DN:

```bash
$ ldapsearch \
    -W \
    -H ldap://ipa.tuxed.example \
    -D "uid=fkooman,cn=users,cn=accounts,dc=tuxed,dc=example" \
    -b "uid=fkooman,cn=users,cn=accounts,dc=tuxed,dc=example"
```

After providing the user's password, you should see all the LDAP attributes 
associated with that user account, e.g. `memberOf`, `mail`, `uid`.

### Active Directory

If you are using 
[Active Directory](https://en.wikipedia.org/wiki/Active_Directory), it is 
slightly different, replace `DOMAIN` with the name of your domain and `fkooman` 
with a valid user in your AD:

```bash
$ ldapsearch \
        -W \
        -H ldap://ad.example.org \
        -D "DOMAIN\fkooman" \
        -b "dc=example,dc=org" \
        "(sAMAccountName=fkooman)"
```

You can use the old "NetBIOS domain name" as in the example above, _or_ some 
other 
[options](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-adts/6a5891b8-928e-4b75-a4a5-0e3b77eaca52), 
e.g. `userPrincipalName`:

```bash
$ ldapsearch \
        -W \
        -H ldap://ad.example.org \
        -D "fkooman@example.org" \
        -b "dc=example,dc=org" \
        "(userPrincipalName=fkooman@example.org)"
```

### Search First

If you want to use an attribute that is NOT part of the DN, you first need to 
perform a search for the user's DN, based on the attribute + value you 
want. For example we want the users to login with the `uidNumber` attribute and
my `uidNumber` happens to be `572600001`:

For this we do an _anonymous bind_ to figure out my DN in the LDAP:

```bash
$ ldapsearch \
    -LLL \
    -x \
    -H ldap://server.ipa.test \
    -b "cn=users,cn=accounts,dc=ipa,dc=test" \
    "(uidNumber=572600001)" \
    dn
```

This returns my DN, in this case 
`dn: uid=fkooman,cn=users,cn=accounts,dc=ipa,dc=test` which we can now use to
bind now to the server to verify the password:

```bash
$ ldapsearch \
    -LLL \
    -W \
    -H ldap://server.ipa.test \
    -D "uid=fkooman,cn=users,cn=accounts,dc=ipa,dc=test" \
    -b "uid=fkooman,cn=users,cn=accounts,dc=ipa,dc=test"
```

If this works, we can use this information as explained below in the 
configuration examples.

## Configuration

You can configure the portal to use LDAP. This is configured in the file 
`/etc/vpn-user-portal/config.php`.

You have to set `authMethod` first:

```php
'authMethod' => 'LdapAuthModule',
```

Next is configuring the LDAP server in the `LdapAuthModule` section. The table
below lists all available settings.

| Option                    | Required | Type            | Example                                     | Since |
| ------------------------- | -------- | --------------- | ------------------------------------------- | ----- |
| `ldapUri`                 | Yes      | `string`        | `ldaps://ldap.example.org`                  |       |
| `userIdAttribute`         | Yes      | `string`        | `uid`                                       |       |
| `bindDnTemplate`          | No*      | `string`        | `uid={{UID}},ou=people,dc=example,dc=org`   |       |
| `baseDn`                  | No*      | `string`        | `ou=people,dc=example,dc=org`               |       |
| `userFilterTemplate`      | No*      | `string`        | `(uid={{UID}})`                             |       |
| `addRealm`                | No       | `string`        | `example.org`                               |       |
| `searchBindDn`            | No       | `string`        | `cn=admin,dc=example,dc=org`                |       |
| `searchBindPass`          | No       | `string`        | `s3cr3t`                                    |       |
| `permissionAttributeList` | No       | `array<string>` | `['memberOf']`                              |       |
| `tlsCa`                   | No       | `string`        | `/etc/vpn-user-portal/ldap/ldap-ca.crt`     | 3.4.0 |
| `tlsCert`                 | No       | `string`        | `/etc/vpn-user-portal/ldap/ldap-client.crt` | 3.4.0 |
| `tlsKey`                  | No       | `string`        | `/etc/vpn-user-portal/ldap/ldap-client.key` | 3.4.0 |

**NOTE**: `{{UID}}` is a special template variable that is replaced by what the 
user specifies in the "User Name" box at login in the portal. If you specify 
`DOMAIN\{{UID}}` as `bindDnTemplate` in the configuration, the actual "bind DN" 
will become `DOMAIN\fkooman` assuming the user entered `fkooman` as 
"User Name" in the portal.

**NOTE**: _*_ you MUST either specify `bindDnTemplate`, or `baseDn` together 
with `userFilterTemplate` to be able to find a DN for a particular user. If you 
are using a `bindDnTemplate` that is not a "real DN", e.g. when using 
`DOMAIN\{{UID}}` you MUST also specify `baseDn` and `userFilterTemplate` in 
order to search for the actual DN of the user account. See 
[Active Directory](#active-directory).

The `userIdAttribute` is used to _normalize_ the user identity. For LDAP both 
`fkooman` and `FKOOMAN` are the same. By querying the `userIdAttribute` we take
the exact same format as used in the LDAP server. This avoids creating multiple
accounts in the VPN service with different case. You MUST specify the 
`userIdAttribute`.

You can restrict access to the VPN service to a subset of the users in the 
LDAP server by following the [ACL](ACL.md) documentation, or (not recommended) 
by using a filter that only returns results in case the user entry matches a 
specific filter.

```php
'LdapAuthModule' => [
    // *** FreeIPA ***
    // -H ldap://ipa.tuxed.example
    'ldapUri' => 'ldap://ipa.tuxed.example',
    // -D "uid=fkooman,cn=users,cn=accounts,dc=tuxed,dc=example"
    'bindDnTemplate' => 'uid={{UID}},cn=users,cn=accounts,dc=tuxed,dc=example',
    // (if -b is the same -D we do NOT specify baseDn...)
    // to normalize the entered user ID, specify the attribute you want to
    // use to identify the user in the VPN server
    'userIdAttribute' => 'uid',

    // *** AD (NetBIOS domain name) ***
    // -H ldap://ad.example.org \
    'ldapUri' => 'ldap://ad.example.org',
    // -D "DOMAIN\fkooman" \
    'bindDnTemplate' => 'DOMAIN\{{UID}}',
    // -b "dc=example,dc=org" \
    'baseDn' => 'dc=example,dc=org',
    // "(sAMAccountName=fkooman)"
    'userFilterTemplate' => '(sAMAccountName={{UID}})',
    // to normalize the entered user ID, specify the attribute you want to
    // use to identify the user in the VPN server
    'userIdAttribute' => 'sAMAccountName',

    // *** AD (userPrincipalName) ***
    // -H ldap://ad.example.org \
    'ldapUri' => 'ldap://ad.example.org',
    // -D "fkooman@example.org" \
    'bindDnTemplate' => '{{UID}}',

    // when the user does NOT specify the realm, e.g. only "fkooman", this
    // option will add "@example.org" to the "User Name" as specified on
    // the login page. If and only if there is no "@" in the provided
    // "User Name".!
    'addRealm' => 'example.org',
    // -b "dc=example,dc=org" \
    'baseDn' => 'dc=example,dc=org',
    // "(userPrincipalName=fkooman@example.org)"
    'userFilterTemplate' => '(userPrincipalName={{UID}})',
    // to normalize the entered user ID, specify the attribute you want to
    // use to identify the user in the VPN server
    'userIdAttribute' => 'userPrincipalName',

    // *** Search First ***
    // -H ldap://server.ipa.test \
    'ldapUri' => 'ldap://server.ipa.test',
    // -b "cn=users,cn=accounts,dc=ipa,dc=test" \
    'baseDn' => 'cn=users,cn=accounts,dc=ipa,dc=test',
    // "(uidNumber=572600001)" \
    'userFilterTemplate' => '(uidNumber={{UID}})',
    // to normalize the entered user ID, specify the attribute you want to
    // use to identify the user in the VPN server
    'userIdAttribute' => 'uidNumber',
    // you can also perform a bind before searching as not all LDAP servers
    // allow anonymous bind to search the directory. If at all possible,
    // allow anonymous bind on your LDAP server from the VPN server.
    // NEVER USE THE LDAP ADMIN ACCOUNT HERE!
    //'searchBindDn' => 'cn=Anonymous Search User,dc=example,dc=org',
    //'searchBindPass' => 's3r3t',

    //'permissionAttributeList' => [],
],
```

This should be all to configure your LDAP!

## Active Directory

When using Active Directory, you always need to set `baseDn` and 
`userFilterTempalate`, this is because when "binding" with AD the DN used is 
not a real DN, but has the format `EXAMPLE\user` or `user@example.org`. An 
example:

```php
'LdapAuthModule' => [
    'ldapUri' => 'ldaps://ad.example.org',
    'bindDnTemplate' =>  'EXAMPLE\\{{UID}}',
    'baseDn' => 'dc=example,dc=org',
    'userFilterTemplate' => '(sAMAccountName={{UID}})',
    'userIdAttribute' => 'sAMAccountName',
    'permissionAttributeList' => ['memberOf'],
],
```

Alternatively, you can also _first_ search for the user, then you do not need
to set `bindDnTemplate`, but you MAY have to set `searchBindDn` and 
`searchBindPass` if the AD does not allow anonymous search (and bind) to 
perform the search. An example:

```php
'LdapAuthModule' => [
    'ldapUri' => 'ldaps://ad.example.org',
    'baseDn' => 'dc=example,dc=org',
    'userFilterTemplate' => '(sAMAccountName={{UID}})',
    'userIdAttribute' => 'sAMAccountName',
    'permissionAttributeList' => ['memberOf'],
    'searchBindDn' => 'EXAMPLE\user',
    'searchBindPass' => 's3r3t',    
],
```

Where `EXAMPLE\user` is a user that has the option to search the AD, you do NOT
want this to be a privileged account!

If is recommended to use `bindDnTemplate` as in that case you do not need to
store any secrets in the LDAP configuration.

## LDAPS

In order to use LDAPS, you can use the LDAPS scheme in the `baseUri`
configuration option, e.g.:

```php
'ldapUri' => 'ldaps://ldap.example.org',
```

### Custom CA

**NOTE**: this only works from vpn-user-portal >= 3.4.0

If your LDAP server does not have a publicly trusted certificate, you can 
configure the CA that issued the certificate in the `LdapAuthModule` section, 
e.g.:

```php
'LdapAuthModule' => [
    
    // ...
    // other LDAP configuration options...
    // ...
    
    'tlsCa' => '/etc/vpn-user-portal/ldap/ldap-ca.crt',
],
```

It is the easiest to create a directory `/etc/vpn-user-portal/ldap` and put the 
CA certificate in there. Make sure the CA cert file has group readable, e.g. 
`0640` permissions.

### Client Certificate Authentication

**NOTE**: this is only available in vpn-user-portal >= 3.4.0

If your LDAP server requires authentication using TLS client certificates, i.e. 
"mutual TLS", you can configure the certificate and key in the `LdapAuthModule` 
section:

```php
'LdapAuthModule' => [
    
    // ...
    // other LDAP configuration options...
    // ...
    
    'tlsCert' => '/etc/vpn-user-portal/ldap/ldap-client.crt',
    'tlsKey' => '/etc/vpn-user-portal/ldap/ldap-client.key', 
],
```

It is the easiest to create a directory `/etc/vpn-user-portal/ldap` and put the 
certificate and key certificate in there. Make sure the certificate and key 
file have group readable, e.g. `0640` permissions.

You **MUST** restart `php-fpm` to pick up the changes. On Fedora / EL:

```bash
$ sudo systemctl restart php-fpm
```

On Debian / Ubuntu:

```bash
$ sudo systemctl restart php$(/usr/sbin/phpquery -V)-fpm
```

## Troubleshooting

You can use `ldapsearch` to figure out what would be the required values for
the various configuration options and test them independently of the VPN 
service. This is HIGHLY recommended!

In case this turns out to not be enough, additional logging is written to 
_syslog_. You can view the log regarding authentication using `journalctl`, 
i.e.:

```bash
$ sudo journalctl -f -t vpn-user-portal
```

After running this, try to authenticate to the portal and if something goes 
wrong, you'll see it in the log, e.g.:

```
$ sudo journalctl -f -t vpn-user-portal
Jul 26 11:10:46 vpn.example.org vpn-user-portal[150350]: Unable to validate credentials: LDAP error: (49) Invalid credentials
Jul 26 11:11:42 vpn.example.org vpn-user-portal[150726]: Unable to validate credentials: user ID attribute "uidX" not available in LDAP response
```
