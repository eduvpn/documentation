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
module. Make sure you test from your VPN server so you are sure you actually
can access the LDAP server. You SHOULD use [TLS](#ldaps) to talk to your LDAP
server.

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

* LDAP host, e.g. `ldap.example.org`;
* The base DN, e.g. `ou=people,dc=example,dc=org`;
* The attribute to use for user authentication, e.g. `uid`;
* Possibly an account to perform a _search_ first to find the user's DN;
* Possibly a mTLS client certificate/key when using e.g. Google's LDAP.

## Configuration

We'll show some example `ldapsearch` commands you can use to verify you have 
all the required information to configure LDAP in your VPN server. Then we'll 
show the configuration "block" to use for your particular scenario.

In order to make the portal use LDAP authentication, you need to modify the 
configuration file `/etc/vpn-user-portal/config.php`.

You have to set `authMethod` first:

```php
'authMethod' => 'LdapAuthModule',
```

Next, you'll configure the `LdapAuthModule` block. Examples for that are shown
below, all allowed configuration options can be found 
[here](#configuration-options).

### Username in DN

The most simple case is the scenario where the username is part of the DN in 
the LDAP server, e.g. `uid=alice,ou=people,dc=example,dc=org`. We can 
directly try to bind with this DN, verify the password and obtain (some) 
attributes. For example:

```bash
$ ldapsearch -LLL -W -x -H ldap://ldap.example.org -D 'uid=alice,ou=people,dc=example,dc=org' -b 'uid=alice,ou=people,dc=example,dc=org' uid memberOf
Enter LDAP Password: 
dn: uid=alice,ou=people,dc=example,dc=org
uid: alice
memberOf: cn=employees,ou=groups,dc=example,dc=org
```

The `ldapsearch` asks for the user's password. After
providing the correct one, it shows the attribute values for the attributes 
`uid` and `memberOf`. The full LDAP configuration will look like this:

```php
'LdapAuthModule' => [
    'ldapUri' => 'ldap://ldap.example.org',
    'bindDnTemplate' => 'uid={{UID}},ou=people,dc=example,dc=org',
    'userIdAttribute' => 'uid',
    'permissionAttributeList' => ['memberOf'],
],
```

### Username NOT in DN

Some LDAP servers do not directly specify the username in the DN of the LDAP 
entries, but it is only available as an attribute. For example the DN looks 
like this: `cn=Bob,ou=people,dc=example,dc=org`. In that case, you'll need 
to search for the user first with the attribute you want to use, for example:

```bash
$ ldapsearch -LLL -x -H ldap://ldap.example.org -b 'ou=people,dc=example,dc=org' '(uid=alice)' uid memberOf
dn: uid=alice,ou=people,dc=example,dc=org
uid: alice
memberOf: cn=employees,ou=groups,dc=example,dc=org
```

This LDAP server allows for _anonymous binds_ to search through the LDAP. If 
your server does not, you need to specify an account to bind to the LDAP in 
order to perform the search for the user's DN. In the example below we use an
"admin" account, obviously you MUST NOT do that and use a read only account
that can only be used to search the LDAP.

```bash
$ ldapsearch -LLL -W -x -H ldap://ldap.example.org -D 'cn=admin,dc=example,dc=org' -b 'ou=people,dc=example,dc=org' '(uid=alice)'
Enter LDAP Password: 
dn: cn=Bob,ou=people,dc=example,dc=org
```

Now that we figured out the DN, we can bind with that DN and the user's password 
and obtain the attributes we want:

```bash
$ ldapsearch -LLL -W -x -H ldap://ldap.example.org -D 'cn=Bob,ou=people,dc=example,dc=org' -b 'cn=Bob,ou=people,dc=example,dc=org' uid memberOf
Enter LDAP Password: 
cn=Bob,ou=people,dc=example,dc=org
uid: alice
memberOf: cn=employees,ou=groups,dc=example,dc=org
```

The full LDAP configuration will look like this:

```php
'LdapAuthModule' => [
    'ldapUri' => 'ldap://ldap.example.org',
    'baseDn' => 'ou=people,dc=example,dc=org',
    'userFilterTemplate' => '(uid={{UID}})',
    'userIdAttribute' => 'uid',
    'permissionAttributeList' => ['memberOf'],
    
    // **only if** an account is needed because "anonymous bind" for search is 
    // not possible
    //'searchBindDn' => 'cn=admin,dc=example,dc=org',
    //'searchBindPass' => 's3cr3t',
],
```

### Active Directory

Configuring Active Directory is basically the same as 
[Username NOT in DN](#username-not-in-dn), but we'll go a bit more in detail
here.

When using Active Directory, you always need to set `baseDn` and 
`userFilterTempalate`, this is because when "binding" with AD the DN used is 
not a real DN, but has the format `EXAMPLE\user` or `user@example.org`. An 
example:

```php
'LdapAuthModule' => [
    'ldapUri' => 'ldap://ad.example.org',
    'bindDnTemplate' =>  'EXAMPLE\\{{UID}}',
    'baseDn' => 'dc=example,dc=org',
    'userFilterTemplate' => '(sAMAccountName={{UID}})',
    'userIdAttribute' => 'sAMAccountName',
    'permissionAttributeList' => ['memberOf'],
],
```

Alternatively, you can also _first_ search for the user, then you do not need
to set `bindDnTemplate`, but you MAY have to set `searchBindDn` and 
`searchBindPass` if the AD does not allow anonymous bind and search. For 
example:

```php
'LdapAuthModule' => [
    'ldapUri' => 'ldap://ad.example.org',
    'baseDn' => 'dc=example,dc=org',
    'userFilterTemplate' => '(sAMAccountName={{UID}})',
    'userIdAttribute' => 'sAMAccountName',
    'permissionAttributeList' => ['memberOf'],
    'searchBindDn' => 'EXAMPLE\admin',
    'searchBindPass' => 's3r3t',
],
```

Where `EXAMPLE\admin` is a user that has the option to search the AD, you 
obviously do NOT want this to be a privileged account!

If is recommended to use `bindDnTemplate` as in that case you do not need to
store any secrets in the LDAP configuration.

## Configuration Options

This is a full overview of all the configuration options.

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
will become `DOMAIN\alice` assuming the user entered `alice` as 
"User Name" in the portal.

**NOTE**: _*_ you MUST either specify `bindDnTemplate`, or `baseDn` together 
with `userFilterTemplate` to be able to find a DN for a particular user. If you 
are using a `bindDnTemplate` that is not a "real DN", e.g. when using 
`DOMAIN\{{UID}}` you MUST also specify `baseDn` and `userFilterTemplate` in 
order to search for the actual DN of the user account. See 
[Active Directory](#active-directory).

The `userIdAttribute` is used to _normalize_ the user identity. For LDAP both 
`alice` and `alice` are the same. By querying the `userIdAttribute` we take
the exact same format as used in the LDAP server. This avoids creating multiple
accounts in the VPN service with different case. You MUST specify the 
`userIdAttribute`.

You can restrict access to the VPN service to a subset of the users in the 
LDAP server by following the [ACL](ACL.md) documentation, or (not recommended) 
by using a filter that only returns results in case the user entry matches a 
specific filter.

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
