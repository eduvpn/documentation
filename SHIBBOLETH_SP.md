---
title: Shibboleth SP
description: Configuration instructions for using the Shibboleth SP
---

This document only describes how to configure Apache and the VPN portal. The 
installation and configuration of Shibboleth itself is out of scope in this 
document. Instead, start 
[here](https://www.switch.ch/aai/guides/sp/installation/) and come back here 
when your Shibboleth SP works and is configured at your IdP.

In `/etc/apache2/sites-available/vpn.example.org.conf` on Debian or in 
`/etc/httpd/conf.d/vpn.example.org.conf` on CentOS add the following:

    <VirtualHost *:443>

        ...

        <Location /vpn-user-portal>
            AuthType shibboleth
            ShibRequestSetting requireSession true
            Require shibboleth
        </Location>

        # disable Shibboleth for the API
        <Location /vpn-user-portal/api.php>
            ShibRequireSession Off
        </Location>

        # disable Shibboleth for the OAuth Token Endpoint
        <Location /vpn-user-portal/oauth.php>
            ShibRequireSession Off
        </Location> 

        ...

    </VirtualHost>

Make sure you restart Apache after changing the configuration.

In order to configure the VPN portal, modify `/etc/vpn-user-portal/config.php`
and set the `authType` and `ShibAuthentication` options:

    ...

    'authMethod' => 'ShibAuthentication',

    ...

    'ShibAuthentication' => [
        'userIdAttribute' => 'persistent-id',
        'permissionAttribute' => 'entitlement',
    ],

    ...

The mentioned attributes `persistent-id` and `entitlement` are configured in 
the Shibboleth configuration. Modify as required. These are the defaults.
