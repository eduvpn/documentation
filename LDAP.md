---
title: LDAP
description: Enable LDAP Authentication
category: howto
---

This document describes how to configure LDAP. We assume you used the 
`deploy_${DIST}.sh` script to deploy the software.

The LDAP integration can be used both for user authentication and for 
authorization, i.e. who will be considered an _administrator_ and which 
profiles will be available for a particular user.

For more information about authorization, after getting authentication to work, 
you can look [here](PORTAL_ADMIN.md) for determining admin portal access, and 
[here](ACL.md) for determining who can access which profiles.

# Introduction

It is a good idea to try with `ldapsearch` if you are not absolutely sure what
to configure. Once `ldapsearch` works, it becomes easier to configure the LDAP
module.

First, install `ldapsearch`:

    $ sudo yum -y install openldap-clients

You need a couple of details first, you can obtain those from your LDAP 
administrator, you need _at least_:

* LDAP host;
* How to _bind_ to the LDAP server, i.e. which DN to use to bind;

For simple [FreeIPA](https://www.freeipa.org/page/Main_Page) setups these are
sufficient:

    $ ldapsearch \
        -W \
        -H ldap://ipa.tuxed.example \
        -D "uid=fkooman,cn=users,cn=accounts,dc=tuxed,dc=example" \
        -b "uid=fkooman,cn=users,cn=accounts,dc=tuxed,dc=example"

After providing the user's password, you should see all the LDAP attributes 
associated with that user account, e.g. `memberOf`, `mail`, `uid`.

If you are using 
[Active Directory](https://en.wikipedia.org/wiki/Active_Directory), it is 
slightly different:

    $ ldapsearch \
            -W \
            -H ldap://ad.example.org \
            -D "DOMAIN\fkooman" \
            -b "dc=example,dc=org" \
            "(sAMAccountName=fkooman)"

You can use the old "NetBIOS domain name" as in the example above, _or_ some 
other 
[options](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-adts/6a5891b8-928e-4b75-a4a5-0e3b77eaca52), 
e.g. `userPrincipalName`:

    $ ldapsearch \
            -W \
            -H ldap://ad.example.org \
            -D "fkooman@example.org" \
            -b "dc=example,dc=org" \
            "(userPrincipalName=fkooman@example.org)"

# Configuration

You can configure the portal to use LDAP. This is configured in the file 
`/etc/vpn-user-portal/config.php`.

You have to set `authMethod` first:

    'authMethod' => 'FormLdapAuthentication',

Next is configuring the LDAP server in the `FormLdapAuthentication` section. 
Note that in the examples below, `{{UID}}` is replaced by what the user 
specifies in the "User Name" box when logging in to the portal. The 
`userIdAttribute` is used to _normalize_ the user identity. For LDAP both 
`fkooman` and `FKOOMAN` are the same. By querying the `userIdAttribute` we take
the exact same format as used in the LDAP server.

    'FormLdapAuthentication' => [
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
    ],

This should be all to configure your LDAP!

# CA

If you use LDAPS and your LDAP server has a self signed certificate you may
need to make the CA certificate available on the VPN machine.

On the IPA server the CA certificate is stored in `/etc/ipa/ca.crt`. Copy this 
to the machine running the VPN software. If you don't have direct access to the
IPA server you can also use OpenSSL to obtain the CA certificate:

    $ openssl s_client -showcerts -connect ipa.example.org:ldaps

You can copy/paste the CA certificate from the certificates shown. 

**NOTE**: make sure you validate this CA out of band! You MUST be sure this 
is the actual CA!

## CentOS / Fedora

If you use a self signed certificate for your LDAP server perform these steps. 
If your certificate is signed by a trusted CA you do not need to do this, it
will work out of the box.

Put the self signed certificate file in `/etc/pki/ca-trust/source/anchors`. 
After this:

    $ sudo update-ca-trust

This will add the CA certificate  to the system wide database in such a way
that it will remain there, even when the `ca-certificates` package updates.

You **MUST** restart `php-fpm` to pick up the changes:

    $ sudo systemctl restart php-fpm

## Debian

If you use a self signed certificate for your LDAP server perform these steps. 
If your certificate is signed by a trusted CA you do not need to do this, it
will work out of the box.

Put the self signed certificate file in 
`/usr/local/share/ca-certificates/ipa.example.org.crt`. After this:
 
    $ sudo update-ca-certificates

This will add the CA certificate  to the system wide database in such a way
that it will remain there, even when the `ca-certificate` package updates.

You **MUST** restart `php-fpm` to pick up the changes:

    $ sudo systemctl restart php7.0-fpm
