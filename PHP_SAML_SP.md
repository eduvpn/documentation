---
title: PHP-SAML-SP
description: SAML Authentication using php-saml-sp
category: howto
---

**NOTE**: the php-saml-sp authentication method is **EXPERIMENTAL**. It is 
**NOT** supported!

Do **NOT** use unless you know what you are doing. Use 
[mod_auth_mellon](MOD_AUTH_MELLON.md) if you are connecting to only 1 IdP or 
a "hub & spoke" federation, and [Shibboleth](SHIBBOLETH_SP.md) in all other 
cases.

### Why

The library was written to be (a lot) simpler to use and configure than 
simpleSAMLphp and only work as a SAML SP supporting only secure cryptographic 
algorithms, see the project 
[site](https://software.tuxed.net/php-saml-sp/) for more information.

### Installation

There's nothing to be done, it is part of Let's Connect! / eduVPN already.

### Configuration of the SP

There are a number of "special" configuration options available next to the 
"basic" ones that are similar to other SAML implementations. The configuration
is done through `/etc/vpn-user-portal/config.php`.

Set the `authMethod` option:

    'authMethod' => 'SamlAuthentication',

Now the `SamlAuthentication` specific options can be set as well:

    // SAML (php-saml-sp)
    'SamlAuthentication' => [
        'userIdAttribute' => 'eduPersonTargetedID',
        //'userIdAttribute' => 'eduPersonPrincipalName',

        // ** AUTHORIZATION | PERMISSIONS **
        //'permissionAttribute' => 'eduPersonEntitlement',
        //'permissionAttribute' => 'eduPersonAffiliation',

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
        //'discoUrl' => 'http://disco.example.org/',

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

#### Details

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
`permissionAttribute`. Indirectly this can be used to restrict certain VPN 
profiles to uses that have a certain "permission" and at the same time enforce
MFA/2FA for those users. Note that an AuthnContext is bound to a _user_, not a
VPN _profile_.

The `permissionSessionExpiry` is similar to `permissionAuthnContext` in the 
sense that it for certain `permissionAttribute` values it will shorten the 
user's session time. For example, "high risk" users can be required to 
authenticate/authorize every day, while "normal" users only have to do that 
once every 90 days. This setting will affect the time the OAuth token and 
issued client certificates are valid. The expiry time is determined by taking
the _minimum_ between the "global" `sessionExpiry` option and the value of this
option. The server default for `sessionExpiry` is 90 days.

### Configuration of the IdP

The metadata URL will be 
`https://vpn.example.org/vpn-user-portal/_saml/metadata` where 
`vpn.example.org` is the hostname of your VPN server.

Make sure:

- the IdP uses the HTTP-Redirect binding for receiving the `AuthnRequest`;
- the IdP uses the HTTP-POST binding to provide the `samlp:Response` to the SP;
- the IdP signs the `saml:Assertion` and/or the `samlp:Response`;
- the IdP verifies the signature on the `samlp:AuthnRequest`;
- the IdP verifies the signature on the `samlp:LogoutRequest`;
- the IdP signs the `samlp:LogoutResponse`.

### Changes

Since `vpn-user-portal` 
[2.0.7](https://github.com/eduvpn/vpn-user-portal/blob/v2/CHANGES.md#207-2019-07-20) 
the `permissionAttribute` configuration option _also_ takes multiple values 
using the PHP array syntax in addition to strings, e.g.:

    'permissionAttribute' => [
        'eduPersonEntitlement', 
        'eduPersonAffiliation'
    ],
