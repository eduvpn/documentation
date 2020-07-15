---
title: Shibboleth SP (Debian)
description: SAML Authentication using Shibboleth
category: authentication
---

This document describes installing Shibboleth on Debian 9.

## Requirements

1. Apache

        Apache webserver is required for Shibboleth SP.

2. Root Access

        It should be possible to execute commands as a root user. Please ensure you have root privileges on the system.

### Shibboleth

    $ sudo apt-get install libapache2-mod-shib2
    $ sudo shib-keygen

The service provider should now be installed. Here are some important files and directories that may help in debugging and configuring shibboleth.

    /etc/shibboleth Configuration directory. The main configuration file is shibboleth.xml
    /var/log/shibboleth Log directory. The main log file is shibd.log
    /run/shibboleth Run time directory where process ID and socket files are stored.
    /var/cache/shibboleth Cache directory where metadata backup and CRL files are stored.

Modify `/etc/shibboleth/shibboleth2.xml`:

* Set entityID to `https://vpn.example.org/shibboleth` in the
  `<ApplicationDefaults>` element.
* Set `handlerSSL` to `true` and `cookieProps` to `https` in the `<Sessions>`
  element
* Set the `entityID` to the entity ID of your IdP, or configure the
  `discoveryURL` in the `<SSO>` element
* Remove `SAML1` from the `<SSO>` attribute content as we no longer need SAML
  1.0 support
* Set the `file` in the `<MetadataProvider>` element for a simple static
  metadata file

Configuring automatic metadata refresh is outside the scope of this document,
refer to your identity federation documentation.


Verify the Shibboleth configuration:

    $ sudo shibd -t
    overall configuration is loadable, check console for non-fatal problems

Restart Shibboleth:

    $ sudo systemctl restart shibd


### Apache

In `/etc/apache2/sites-available/vpn.example.org.conf` add the following:

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

Make sure you restart Apache after changing the configuration:

    $ sudo systemctl restart apache2

### Portal

In order to configure the VPN portal, modify `/etc/vpn-user-portal/config.php`
and set the `authMethod` and `ShibAuthentication` options:

    ...

    'authMethod' => 'ShibAuthentication',

    ...

    'ShibAuthentication' => [
        'userIdAttribute' => 'persistent-id',
        'permissionAttribute' => 'entitlement',
    ],

    ...

## Attributes

The mentioned attributes `persistent-id` and `entitlement` are configured in
the Shibboleth configuration. Modify/add others as required in
`/etc/shibboleth/attribute-map.xml`. Do not forget to restart Shibboleth if
you make any changes to its configuration.

## Service Provider Registration in Identity Federation

Register your SP in your identity federation, or in your IdP. The
metadata URL is typically `https://yourdomain/Shibboleth.sso/Metadata`.
