# Introduction

This document describes how to configure LDAP for deployed systems. We assume 
you used the `deploy.sh` script to deploy the software. Below we assume you 
use `vpn.example`, but modify this domain to your own domain name!

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
        'ldapUri' => 'ldap://ldap.example.org',
        'userDnTemplate' => 'uid={{UID}},ou=People,dc=example,dc=org',
    ],

Set the `ldapUri` to the URI of your LDAP server. You can also use TLS by 
using an URI like `ldaps://ldap.example.org`, and also provide the TCP port 
explicitly, e.g. `ldaps://ldap.example.org:636`. 

The `userDnTemplate` will be used to "generate" a DN to use to bind to the 
LDAP server. This example is for 
[Red Hat Directory Server](https://www.redhat.com/en/technologies/cloud-computing/directory-server). 
For your LDAP server it may be different. The `{{UID}}` is replaced by what the user
provides in the `Username` field when trying to authenticate to the portal(s).

Repeat this for `vpn-admin-portal` and you're all set.
