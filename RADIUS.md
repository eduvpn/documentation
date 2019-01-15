# Introduction

This document describes how to configure RADIUS for deployed systems. We assume 
you used the `deploy_${DIST}.sh` script to deploy the software. Below we assume 
you use `vpn.example`, but modify this domain to your own domain name!

RADIUS integration can currently only be used to _authenticate_ users, not for 
authorization/ACL purposes.

# Configuration

You can configure both `vpn-user-portal` and `vpn-admin-portal` to use RADIUS. 
This is configured in the files `/etc/vpn-user-portal/config.php` and
`/etc/vpn-admin-portal/config.php`. We will only show how to configure
`vpn-user-portal` as `vpn-admin-portal` is exactly the same.

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

Repeat this for `vpn-admin-portal` if required you're all set.
