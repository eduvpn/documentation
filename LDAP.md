---
title: LDAP
description: Enable LDAP Authentication
category: howto
---

This document describes how to configure LDAP for deployed systems. We assume 
you used the `deploy_${DIST}.sh` script to deploy the software. Below we assume 
you use `vpn.example`, but modify this domain to your own domain name!

LDAP integration is used for two aspects:

1. LDAP user authentication
2. LDAP group membership retrieval to restrict access to the "Admin" and/or 
   profiles

The first one is what we focus on here, the second one is documented in the 
[ACL](ACL.md) document.

# Configuration

You can configure the portal to use LDAP. This is configured in the file 
`/etc/vpn-user-portal/config.php`.

You have to set `authMethod` first:

    'authMethod' => 'FormLdapAuthentication',

Then you can configure the LDAP server:

    'FormLdapAuthentication' => [
        // *** OpenLDAP / FreeIPA ***
        'ldapUri' => 'ldaps://ipa.example.org',
        'bindDnTemplate' => 'uid={{UID}},cn=users,cn=accounts,dc=example,dc=org',
        //'permissionAttribute' => 'eduPersonEntitlement',
        //'permissionAttribute' => 'memberOf',

        // *** Active Directory ***
        //'ldapUri' => 'ldap://ad.example.org',
        //'bindDnTemplate' => 'DOMAIN\{{UID}}',
        //'baseDn' => 'dc=example,dc=org',
        //'userFilterTemplate' => '(sAMAccountName={{UID}})',
        //'permissionAttribute' => 'memberOf',
    ],

Set the `ldapUri` to the URI of your LDAP server. If you are using LDAPS, you 
may need to obtain the CA certificate of the LDAP server and store it 
locally so it can be used to verify the LDAP server certificate. See the
CA section below.

The `bindDnTemplate` will be used to "generate" a DN to use to bind to the 
LDAP server. This example is for [FreeIPA](https://www.freeipa.org/).

For your LDAP server it may be different. The `{{UID}}` is replaced by what the 
user provides in the `Username` field when trying to authenticate to the 
portal(s).

For Active Directory you can use the following `bindDnTemplate`, where `DOMAIN`
is the name of your domain:

    'bindDnTemplate' => 'DOMAIN\{{UID}}'

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

# Testing

To make sure everything works as expected, install `ldapsearch`:

    $ sudo yum -y install openldap-clients

Try with your configured DN:

    $ ldapsearch -H ldaps://ipa.example.org -D 'uid=johndoe,cn=users,cn=accounts,dc=example,dc=org' -W

Replace `johndoe` with an user ID at your LDAP server and provide the password
for that account when it asks. This should return something like this, not an 
error:

    # extended LDIF
    #
    # LDAPv3
    # base <> (default) with scope subtree
    # filter: (objectclass=*)
    # requesting: ALL
    #

    # search result
    search: 2
    result: 32 No such object

    # numResponses: 1

Now you should be able to login to the VPN portal(s).
