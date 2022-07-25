This document describes how to configure LDAP. We assume you used the 
`deploy_${DIST}.sh` script to deploy the software.

The LDAP integration can be used both for _authentication_ and \
_authorization_.

This document talks about _authentication_. See [ACL](ACL.md) for more on 
_authorization_.

# Introduction

It is a good idea to try with `ldapsearch` if you are not absolutely sure what
to configure. Once `ldapsearch` works, it becomes easier to configure the LDAP
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

## FreeIPA

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

## Active Directory

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

## Search First

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

# Configuration

You can configure the portal to use LDAP. This is configured in the file 
`/etc/vpn-user-portal/config.php`.

You have to set `authMethod` first:

```php
'authMethod' => 'LdapAuthModule',
```

Next is configuring the LDAP server in the `LdapAuthModule` section. 

**NOTE**: `{{UID}}` is a special template variable that is replaced by what the 
user specifies in the "User Name" box at login in the portal. If you specify 
`DOMAIN\{{UID}}` as `bindDnTemplate` in the configuration, the actual "bind DN" 
will become `DOMAIN\fkooman` assuming the user entered `fkooman` as 
"User Name" in the portal.

The `userIdAttribute` is used to _normalize_ the user identity. For LDAP both 
`fkooman` and `FKOOMAN` are the same. By querying the `userIdAttribute` we take
the exact same format as used in the LDAP server. This avoids creating multiple
accounts in the VPN service with different case. You SHOULD specify the 
`userIdAttribute`! A future version of the VPN server will make this a MUST.

You can restrict access to the VPN service to a subset of the users in the 
LDAP server by following the [ACL](ACL.md) documentation, or (not recommended) 
by using a filter that only returns results in case the user entry matches a 
specific filter. If you use a filter you MUST specific the `userIdAttribute` as 
the decision whether or not the account is allowed to login is based on whether 
or not results are returned.

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

# LDAPS

In order to use LDAPS, you can use the LDAPS scheme in the `baseUri`
configuration option, e.g.:

```php
'ldapUri' => 'ldaps://ldap.example.org',
```

If you use LDAPS and your LDAP server has a self signed certificate you may
need to make the CA certificate available on the VPN machine.

On the IPA server the CA certificate is stored in `/etc/ipa/ca.crt`. Copy this 
to the machine running the VPN software. If you don't have direct access to the
IPA server you can also use OpenSSL to obtain the CA certificate:

```bash
$ openssl s_client -showcerts -connect ipa.example.org:ldaps
```

You can copy/paste the CA certificate from the certificates shown. 

**NOTE**: make sure you validate this CA out of band! You MUST be sure this 
is the actual CA!

## Fedora / EL

If you use a self signed certificate for your LDAP server perform these steps. 
If your certificate is signed by a trusted CA you do not need to do this, it
will work out of the box.

Put the self signed certificate file in `/etc/pki/ca-trust/source/anchors`. 
After this:

```bash
$ sudo update-ca-trust
```

This will add the CA certificate  to the system wide database in such a way
that it will remain there, even when the `ca-certificates` package updates.

You **MUST** restart `php-fpm` to pick up the changes:

```bash
$ sudo systemctl restart php-fpm
```

## Debian / Ubuntu

If you use a self signed certificate for your LDAP server perform these steps. 
If your certificate is signed by a trusted CA you do not need to do this, it
will work out of the box.

Put the self signed certificate file in 
`/usr/local/share/ca-certificates/ipa.example.org.crt`. After this:
 
 ```bash
$ sudo update-ca-certificates
```

This will add the CA certificate  to the system wide database in such a way
that it will remain there, even when the `ca-certificate` package updates.

You **MUST** restart `php-fpm` to pick up the changes:

```bash
$ sudo systemctl restart php$(/usr/sbin/phpquery -V)-fpm
```
