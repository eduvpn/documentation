---
title: OpenID
description: OpenID Connect Authentication using mod_auth_openidc
category: authentication
---

This module enables an Apache 2.x web server to operate as an OpenID Connect Relying Party (RP) towards an OpenID Connect Provider (OP)
https://github.com/zmartzone/mod_auth_openidc

### Install and restart apache

on fedora:

    $ dnf install mod_auth_openidc

    $ sudo systemctl restart httpd

or on Debian:

    $ apt install libapache2-mod-auth-openidc

    $ sudo systemctl restart apache2

### Configure mod_auth_openidc in Apache

Register your RP in your OpenID Provider (OP). You will need to provide the following information:

* The redirect URL you want to receive ID tokens on

You will receive:

* A Client Secret for your Client ID (for authenticating your client to the OP).

* MetaData (either file or URL)

Modify `auth_openidc.conf` 
(fedora):  `/etc/httpd/conf.d/auth_openidc.conf` 
(debian): `/etc/apache2/mods-enabled/auth_openidc.conf` 

```
    # Your OpenID Connect Provider (OP):
    # if metadata URL is provided, configure  OIDCProviderMetadataURL <url>
    # if metadata file is provided, use detailed configuration for single OP
    # https://github.com/zmartzone/mod_auth_openidc/blob/master/auth_openidc.conf
    OIDCProviderMetadataURL https://accounts.google.com/.well-known/openid-configuration

    # The Client ID your received when registering at your OP:
    OIDCClientID <client_ID_from_OP>
    # The Client Secret your received when registering at your OP:
    OIDCClientSecret <client_secret_from_OP>


    # The redirect uri you registered at your OP:
    # RediectURI is predeined int VPN PORTAL as https://domainvpn.example.com/${VPN_USER_PORTAL}/openid
    # it must be the same here in order for the sign in / logout to property work
    OIDCRedirectURI https://vpn.example.cog/vpn-user-portal/openid
    OIDCCryptoPassphrase <randum_generated_secret>


    # Pass the user's claim as http headers (SUB, EMAIL, ROLES)
    OIDCPassClaimsAs "headers"
    OIDCPassUserInfoAs "claims"
    OIDCPassRefreshToken "Off"
    OIDCRemoteUserClaim sub
    OIDCClaimPrefix openid-


    ########################################
    #   VPN-USER-PORTAL openid auth
    ########################################

    <Location /vpn-user-portal>
       AuthType openid-connect
       Require valid-user
    </Location>

    # disable OIDC for the API
    <Location /vpn-user-portal/api.php>
        AuthType None
        Require all granted
    </Location>

    # disable OIDC for the OAuth Token Endpoint
    <Location /vpn-user-portal/oauth.php>
        AuthType None
        Require all granted
    </Location>
```



### Portal


Edit `/etc/vpn-user-portal/config.php` and set:

    'authModule' => 'OpenIdAuthModule',

You can change the `userIdAttribute` value under the `OpenIdAuthModule` 
section.
By default the `REMOTE_USER` attribute will be used to identify users.

If you also want to use authorization based on an attribute, 
you can set the `permissionAttribute`.
By default the `HTTP_OIDC_ROLES` attribute will be used to identify permissions.



In order to configure the VPN portal, modify `/etc/vpn-user-portal/config.php`
and set the `authMethod` and `OpenIdAuthModule` options:

    ...

    'authMethod' => 'OpenIdAuthModule',

    ...

    'OpenIdAuthModule' => [
        'userIdAttribute' => 'REMOTE_USER',
        'permissionAttributeList' => ['HTTP_OPENID_ROLES'],
    ],

    ...


Make sure you restart Apache after changing the configuration:

    $ sudo systemctl restart httpd

or (on debian)

    $ sudo systemctl restart apache2