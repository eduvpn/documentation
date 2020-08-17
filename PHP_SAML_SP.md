---
title: PHP-SAML-SP
description: SAML Authentication using php-saml-sp
category: authentication
---

## Introduction

**NOTE**: the php-saml-sp authentication method is **EXPERIMENTAL**. It is 
**NOT** supported!

Do **NOT** use unless you know what you are doing. Use 
[mod_auth_mellon](MOD_AUTH_MELLON.md) if you are connecting to only 1 IdP or 
a "hub & spoke" federation, and [Shibboleth](SHIBBOLETH_SP.md) in all other 
cases.

## Why

This application was written to be (a lot) simpler to use and configure than 
simpleSAMLphp and only work as a SAML SP supporting only secure cryptographic 
algorithms, see the project 
[site](https://software.tuxed.net/php-saml-sp/) for more information.

## Installation

It is easy to install and enable php-saml-sp.

### CentOS

    $ sudo yum -y install php-saml-sp
    $ sudo systemctl restart httpd
    
### Fedora

    $ sudo dnf -y install php-saml-sp
    $ sudo systemctl restart httpd

### Debian

    $ sudo apt -y install php-saml-sp
    $ sudo a2enconf php-saml-sp
    $ sudo systemctl restart apache2

## Configuring the SP

See `/etc/php-saml-sp/config.php`. 

The metadata URL is `https://vpn.example.org/php-saml-sp/metadata`. The 
entityID is the same (by default). You can override this by setting `entityId` 
to a value of your choice, e.g. `https://vpn.example.org/saml` to be vendor 
neutral in case you want to switch later. Choosing something stable here is 
important when you use for example `eduPersonTargetedID` as that identifier
is typically bound to the SP entityID.

Copy the IdP(s) metadata to `/etc/php-saml-sp/metadata`.

Make sure you at least configure `idpList` in `/etc/php-saml-sp/config.php` 
with the list of IdPs that have access to this SP.

To test your SP/IdP configuration, go to `https://vpn.example.org/php-saml-sp/` 
and use the "Test" button.

## Configuring the VPN Service

The configuration is done through `/etc/vpn-user-portal/config.php`.

Set the `authMethod` option:

    'authMethod' => 'PhpSamlSpAuthentication',

Now the `PhpSamlSpAuthentication` specific options can be set as well:

    'PhpSamlSpAuthentication' => [
        'userIdAttribute' => 'eduPersonTargetedID',
        //'userIdAttribute' => 'eduPersonPrincipalName',

        // ** AUTHORIZATION | PERMISSIONS **
        //'permissionAttribute' => [
        //      'eduPersonEntitlement',
        //      //'eduPersonAffiliation',
        //],

        // AuthnContext required for *all* users
        //'authnContext' => ['urn:oasis:names:tc:SAML:2.0:ac:classes:TimesyncToken'],

        // Users with certain permissions obtained through
        // "permissionAttribute" MUST also have ANY of the listed
        // AuthnContexts. If they currently don't, a new authentication is
        // triggered to obtain it
        //'permissionAuthnContext' => [
        //    'urn:example:LC-admin' => ['urn:oasis:names:tc:SAML:2.0:ac:classes:TimesyncToken'],
        //],
    ],

### AuthnContext

The `authnContext` will request the specified AuthnContext of the IdP, this is 
to trigger for example MFA/2FA. It integrates with 
[SURFsecureID](https://wiki.surfnet.nl/display/SsID/SURFsecureID) as well. 
Setting `authnContext` means this context will be required for ALL users.

### AuthnContext for Permissions

The `permissionAuthnContext` is a mapping between "permission" and required 
`authnContext`. This can be used to e.g. force MFA/2FA only for a subset of
users that have the specified attribute values as obtained through the 
`permissionAttribute`. Indirectly this can be used to restrict certain VPN 
profiles to uses that have a certain "permission" and at the same time enforce
MFA/2FA for those users. Note that an AuthnContext is bound to a _user_, not a
VPN _profile_.
