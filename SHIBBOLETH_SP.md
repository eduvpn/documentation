---
title: Shibboleth SP
description: Configuration instructions for using the Shibboleth SP
---

This document only describes installing Shibboleth on Debian 9 as there it is
part of the default package repository. On CentOS you'd have to install it 
for example using the 
[packages](https://www.switch.ch/aai/guides/sp/installation/) provided by 
SWITCH. The configuration will be mostly the same.

### Shibboleth

    $ sudo apt-get install libapache2-mod-shib2
    $ sudo shib-keygen

Modify `/etc/shibboleth/shibboleth2.xml`:

* Set entityID to `https://vpn.example.org/shibboleth` in the 
  `<ApplicationDefaults>` element.
* Set `handlerSSL` to `true` and `cookieProps` to `https` in the `<Sessions>` 
  element
* Set the `entityID` to the entity ID of your IdP, or configure the 
  `discoveryURL` in the `<SSO>` element
* Set the `file` in the `<MetadataProvider>` element for a simple static 
  metadata file

Configuring automatic metadata refresh is outside the scope of this document,
refer to your identity federation documentation.

Verify the Shibboleth configuration:

    $ sudo shibd -t
    overall configuration is loadable, check console for non-fatal problems

Next: register your SP in your identity federation, or in your IdP.

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

The mentioned attributes `persistent-id` and `entitlement` are configured in 
the Shibboleth configuration. Modify as required. These are the defaults.
