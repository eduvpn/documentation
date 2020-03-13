---
title: OpenID Connext Relying Party
description: OpenID Connect Authentication using OpenID Connect
---

### mod_auth_openidc

on Centos:

    $ yum install mod_auth_openidc

or on Debian:

    $ apt install libapache2-mod-auth-openidc

Restart apache:

    $ sudo systemctl restart httpd

or

    $ sudo systemctl restart apache2

### Apache

Register your RP in your OpenID Provider (OP). You will need to provide the following information:

* Your Client ID and Secret (for authenticatiign your client to the OP.

* The redirect URL you want to receive ID tokens on

You will typically receive:

* A Client Secret for your Client ID (for authenticating your client to the OP.

Modify `/etc/httpd/conf.d/auth_openidc.conf` (centos) or `/etc/apache2/mods-enabled/auth_openidc.conf` (debian):

```
    # Your OpenID Connect Provider (OP):
    OIDCProviderMetadataURL https://connect.test.surfconext.nl/.well-known/openid-configuration
    # The Client ID your received when registering at your OP:
    OIDCClientID eduvpn.rp.tld
    # The Client Secret your received when registering at your OP:
    OIDCClientSecret somegobbledygookhere

    # The redirect uri you registered at your OP:
    OIDCRedirectURI https://eduvpn.rp.tld/vpn-user-portal/redirect_uri
    OIDCCryptoPassphrase somerandomsecret

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


Make sure you restart Apache after changing the configuration:

    $ sudo systemctl restart httpd

or (on debian)

    $ sudo systemctl restart apache2

### Portal

In order to configure the VPN portal, modify `/etc/vpn-user-portal/config.php`
and set the `authMethod` and `ShibAuthentication` options:

    ...

    'authMethod' => 'OpenidcAuthentication',

    ...

    'OpenidcAuthentication' => [
        'subjectClaim' => 'OIDC_CLAIM_sub-id',
        'permissionClaim' => 'OIDC_CLAIM_eduperson_entitlement',
    ],

    ...

