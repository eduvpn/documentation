---
title: PHP SAML SP
description: SAML Authentication using php-saml-sp
category: howto
---

**NOTE**: the php-saml-sp authenitcation method is **EXPERIMENTAL**. 

Do **NOT** use unless you know what you are doing. Use 
[mod_auth_mellon](MOD_AUTH_MELLON.md) if you are connecting to only 1 IdP or 
a "hub & spoke" federation, and [Shibboleth](SHIBBOLETH_SP.md) in all other 
cases.

### Why

The library was written to be (a lot) simpler to use and configure than 
simpleSAMLphp and only work as a SAML SP supporting only secure cryptographic 
algorithms, see the project 
[site](https://software.tuxed.net/fkooman/php-saml-sp) for more information.

### Installation

There's nothing to be done, it is part of Let's Connect! / eduVPN already.

### Configuration

There are a number of "special" configuration options available next to the 
"basic" ones that are similar to other SAML implementations. The configuration
is done through `/etc/vpn-user-portal/config.php`.

Set the `authMethod` option:

    'authMethod' => 'SamlAuthentication',

Now the `SamlAuthentication` specific options can be set as well:

    // SAML (php-saml-sp)
    'SamlAuthentication' => [
        // 'OID for eduPersonTargetedID
        'userIdAttribute' => 'urn:oid:1.3.6.1.4.1.5923.1.1.1.10',
        // OID for eduPersonPrincipalName
        //'userIdAttribute' => 'urn:oid:1.3.6.1.4.1.5923.1.1.1.6',

        // ** AUTHORIZATION | PERMISSIONS **
        // OID for eduPersonEntitlement
        //'permissionAttribute' => 'urn:oid:1.3.6.1.4.1.5923.1.1.1.7',
        // OID for eduPersonAffiliation
        //'permissionAttribute' => 'urn:oid:1.3.6.1.4.1.5923.1.1.1.1',

        // override the SP entityId, the default is:
        // https://vpn.example.org/vpn-user-portal/_saml/metadata
        //'spEntityId' => 'https://vpn.example.org/saml',

        // (Aggregate) SAML metadata file containing the IdP metadata of IdPs
        // that are allowed to access this service
        'idpMetadata' => '/path/to/idp/metadata.xml',

        // set a fixed IdP for use with this service, it MUST be available in
        // the IdP metadata file
        'idpEntityId' => 'https://idp.example.org/saml',

        // set a URL that performs IdP discovery, all IdPs listed in the
        // discovery service MUST also be available in the IdP metadata file,
        // NOTE: do NOT enable idpEntityId as it will take precedence over
        // using discovery...
        //'discoUrl' => 'http://vpn.example.org/php-saml-ds/index.php',

        // AuthnContext required for *all* users
        //'authnContext' => ['urn:oasis:names:tc:SAML:2.0:ac:classes:TimesyncToken'],

        // Users with certain permissions obtained through
        // "permissionAttribute" MUST also have ANY of the listed
        // AuthnContexts. If they currently don't, a new authentication is
        // triggered to obtain it
        //'permissionAuthnContext' => [
        //    'urn:example:LC-admin' => ['urn:oasis:names:tc:SAML:2.0:ac:classes:TimesyncToken'],
        //],

        // Allow for overriding global sessionExpiry based on SAML
        // "permissionAttribute" value(s)
        //'permissionSessionExpiry' => [
        //    'urn:example:LC-admin' => 'PT12H',
        //],
    ],

### Configuration Details

The `authnContext`, `permissionAuthnContext` and `permissionSessionExpiry` 
option require extra explanation as they are not typically configurable using
other SAML implementations. 

The `authnContext` will request the specified AuthnContext of the IdP, this is 
to trigger for example MFA/2FA. It integrates with 
[SURFsecureID](https://wiki.surfnet.nl/display/SsID/SURFsecureID) as well. 
Setting `authnContext` means this context will be required for ALL users.

The `permissionAuthnContext` is a mapping between "permission" and required 
`authnContext`. This can be used to e.g. force MFA/2FA only for a subset of
users that have the specified attribute values as obtained through the 
`permissionAttribute`. Indirectly this can be used to restrict certains VPN 
profiles to uses that have a certain "permission" and at the same time enforce
MFA/2FA for those users. Note that an AuthnContext is bound to a _user_, not a
VPN _profile_.

The `permissionSessionExpiry` is similar to `permissionAuthnContext` in the 
sense that it for certain `permissionAttribute` values it will shorten the 
user's session time. For example, "high risk" users can be required to 
authenticate/authorize every day, while "normal" users only have to do that 
once every 90 days. This setting will affect the time the OAuth token and 
issued client certificates are valid. The expity time is determined by taking
the _minimum_ between the "global" `sessionExpiry` option and the value of this
option. The server default for `sessionExpiry` is 90 days.

### Changes

Since `vpn-user-portal` 2.0.7 the `permissionAttribute` configuration option 
takes multiple values using the PHP array syntax, e.g.:

        'permissionAttribute' => [
            'urn:oid:1.3.6.1.4.1.5923.1.1.1.7', 
            'urn:oid:1.3.6.1.4.1.5923.1.1.1.1'
        ],

