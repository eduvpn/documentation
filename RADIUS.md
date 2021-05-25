---
title: RADIUS
description: Enable RADIUS Authentication
category: authentication
---

This document describes how to configure RADIUS for deployed systems. We assume 
you used the `deploy_${DIST}.sh` script to deploy the software. Below we assume 
you use `vpn.example`, but modify this domain to your own domain name!

RADIUS integration can currently only be used to _authenticate_ users, not for 
authorization/ACL purposes.

In order to make a particular user an "administrator" in the portal, see 
[PORTAL_ADMIN](PORTAL_ADMIN.md).

**NOTE**: RADIUS integration does NOT support PEAP/TTLS, plain text 
authentication ONLY!, RADIUS servers used for _eduroam_ authentication will 
typically be configured with PEAP/TTLS, as plain text authentication is not 
supported for 802.1X.

**NOTE**: If you have the choice between LDAP and RADIUS, always choose LDAP! 
LDAP is supported by all common IdMs, even Active Directory. Go [here](LDAP.md)
for instructions on how to configure LDAP.

# Configuration

First install the PHP module for RADIUS:

    $ sudo yum install php-pecl-radius # CentOS/Fedora
    $ sudo apt install php-radius      # Debian

Restart PHP to activate the RADIUS module:

    $ sudo systemctl restart php-fpm                            # CentOS/Fedora
    $ sudo systemctl restart php$(/usr/sbin/phpquery -V)-fpm    # Debian

You can configure the portal to use RADIUS. This is configured in the file 
`/etc/vpn-user-portal/config.php`.

You have to set `authMethod` first:

    'authMethod' => 'FormRadiusAuthentication',

Then you can configure the RADIUS server:

    // RADIUS
    'FormRadiusAuthentication' => [
        'serverList' => [
            [
                'host' => 'radius.example.org',
                'secret' => 'testing123',
                //'port' => 1812,
            ],
        ],
        //'addRealm' => 'example.org',
        //'nasIdentifier' => 'vpn.example.org',
    ],

Here `serverList` is an array of server configurations where you can add 
multiple RADIUS servers to be used for user authentication. Set the `host` to 
the host of your RADIUS server. You can optionally also specify the `port` 
(defaults to `1812`).

You can also configure whether or not to add a "realm" to the identifier the 
user provides. If for example the user provides `foo` as a user ID, the 
`addRealm` option when set to `example.org` modifies the user ID to 
`foo@example.org` and uses that to authenticate to the RADIUS server.

The `host` and `secret` options are REQUIRED, the others are optional.
