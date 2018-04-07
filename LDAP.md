# Introduction

This document describes how to configure LDAP for deployed systems. We assume 
you used the `deploy_${DIST}.sh` script to deploy the software. Below we assume 
you use `vpn.example`, but modify this domain to your own domain name!

LDAP integration is used for two aspects:

1. LDAP user authentication
2. LDAP group membership retrieval

The first one is what we focus on here, the second one is documented in the 
[ACL](ACL.md) document.

# Configuration

You can configure both `vpn-user-portal` and `vpn-admin-portal` to use LDAP. 
This is configured in the files `/etc/vpn-user-portal/default/config.php` and
`/etc/vpn-admin-portal/default/config.php`. We will only show how to configure
`vpn-user-portal` as `vpn-admin-portal` is exactly the same.

You have to set `authMethod` first:

    'authMethod' => 'FormLdapAuthentication',

Then you can configure the LDAP server:

    'FormLdapAuthentication' => [
        'ldapUri' => 'ldaps://ipa.example.org',
        'userDnTemplate' => 'uid={{UID}},cn=users,cn=accounts,dc=example,dc=org',
    ],

Set the `ldapUri` to the URI of your LDAP server. If you are using LDAPS, you 
may need to obtain the CA certificate of the LDAP server and store it 
locally so it can be used to verify the LDAP server certificate. See the
CA section below.

The `userDnTemplate` will be used to "generate" a DN to use to bind to the 
LDAP server. This example is for [FreeIPA](https://www.freeipa.org/).

For your LDAP server it may be different. The `{{UID}}` is replaced by what the 
user provides in the `Username` field when trying to authenticate to the 
portal(s).

For Active Directory you can use the following `userDnTemplate`, where `DOMAIN`
is the name of your domain:

    'userDnTemplate' => 'DOMAIN\{{UID}}'

Repeat this for `vpn-admin-portal` and you're all set.

# CA

If you use LDAPS and your LDAP server has a self signed certificate you may
need to make the CA certificate available on the VPN machine.

On the IPA server the CA is stored in `/etc/ipa/ca.crt`. Copy this to the 
machine running the VPN software.

## CentOS / Fedora

If you use a self signed certificate for your LDAP server perform these steps. 
If your certificate is signed by a trusted CA you do not need to do this, it
will work out of the box.

Put the self signed certificate file in `/etc/pki/ca-trust/source/anchors`. 
After this:

    $ sudo update-ca-trust

This will add the CA certificate  to the system wide database in such a way
that it will remain there, even when the `ca-certificates` package updates.

You will have to restart `php-fpm` to pick up the changes:

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

You will have to restart `php-fpm` to pick up the changes:

    $ sudo systemctl restart php7.0-fpm

