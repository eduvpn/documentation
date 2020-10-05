---
title: Access Control
description: Configure ACL (Access Control Lists) to manage access to VPN profiles
category: configuration
---

The VPN service supports access control. This allows configuring that users 
require certain "permissions" to access a particular VPN profile. This is 
useful if you have multiple types of users. For example, only employees get 
access to the "Employees" profile, but students do not. You can also require 
certain permissions to be able to use the Portal/API at all.

Currently, the following access control mechanisms are supported:

- SAML (via SAML attribute, e.g. `eduPersonAffiliation` or 
  `eduPersonEntitlement`)
- LDAP (via LDAP attribute, e.g. `memberOf`)
- Static (supported by `FormPdoAuthentication` (default), 
  `FormLdapAuthentication` and `FormRadiusAuthentication`)

The permissions are _cached_ for up to a configurable period. By default this 
is 3 months, but can easily be modified. This cache is required, because not
all authentication backends have a way to validate the permissions 
"out of band", i.e. when the user is not actively authenticating.

# Configuration

The configuration is done in two locations:

- `/etc/vpn-user-portal/config.php`: configure which access control
  mechanism is used and the period for which to _cache_ the permissions;
- `/etc/vpn-server-api/config.php`: configure which profiles are 
  restricted by access control.

## Cache

The permission cache is configured in `/etc/vpn-user-portal/config.php`
using the `sessionExpiry` option. The default is 90 days, `P90D`. The following
is a list of common values you can use:

- `PT8H` (8 hours)
- `PT12H` (12 hours)
- `P1D` (1 day)
- `P7D` (7 days)
- `P1Y` (1 year)

If you modify this value, it will only take effect the next time the user is 
forced to authenticate/authorize.

## SAML

We assume [SAML](SAML.md) is already configured and working.

You have to choose a SAML attribute you want to use for determining the 
membership. Typically, that would be `eduPersonEntitlement` or 
`eduPersonAffiliation`, but any SAML attribute will do. You MAY need to specify 
the OID variant as shown in the example below depending on your IdP / identity
federation.

In order to configure this, modify `/etc/vpn-user-portal/config.php` 
and set the `permissionAttribute` to the name of the attribute:

    'MellonAuthentication' => [
        // OID for eduPersonTargetedId
        'userIdAttribute' => 'MELLON_urn:oid:1_3_6_1_4_1_5923_1_1_1_10',
        // OID for eduPersonPrincipalName
        //'userIdAttribute' => 'MELLON_urn:oid:1_3_6_1_4_1_5923_1_1_1_6',

        // ** AUTHORIZATION | PERMISSIONS **
        // OID for eduPersonEntitlement
        //'permissionAttribute' => 'MELLON_urn:oid:1_3_6_1_4_1_5923_1_1_1_7',
        // OID for eduPersonAffiliation
        //'permissionAttribute' => 'MELLON_urn:oid:1_3_6_1_4_1_5923_1_1_1_1',
    ],

Once you authenticate to the portal, on the "Account" page, i.e. 
`https://vpn.example/vpn-user-portal/account`, you should see the 
"Group Membership(s)" listed there.

## LDAP

We assume [LDAP](LDAP.md) is already configured and working. 

You have to choose an LDAP attribute you want to use for determining the 
membership. Typically, that would be `memberOf`, but any LDAP attribute will work.

In order to configure this, modify `/etc/vpn-user-portal/config.php` 
and set the `permissionAttribute` to the name of the attribute:

    // LDAP
    'FormLdapAuthentication' => [
        // LDAP configuration

        // ...

        // ...

        'permissionAttribute' => 'memberOf',
    ],

Once you authenticate to the portal, on the "Account" page, i.e. 
`https://vpn.example/vpn-user-portal/account`, you should see the 
"Group Membership(s)" listed there.

## Static

The authentication backends `FormPdoAuthentication` (default), 
`FormLdapAuthentication` and `FormRadiusAuthentication` support "static" 
permissions. This means that you can use a (JSON) file where the mapping 
between permissions and users are stored.

Thie file is stored in `/etc/vpn-user-portal/static_permissions.json` and has
the following format:

    {
        "administrators": [
            "foobar",
            "foobaz"
        ],
        "employees": [
            "foobar",
            "foo",
            "bar",
            "baz"
        ]
    }

This means that the users `foobar` and `foobaz` get the `administrators` 
permission and the users `foobar`, `foo`, `bar` and `baz` get the `employees`
permission. Note that the user `foobar` has two permissions.

**NOTE**: if you are using the `FormLdapAuthentication` authentication backend, 
the static permissions are _added_ to the ones that may have been retrieved 
through LDAP.

## Admin/Portal/API Access

You can restrict access to the Portal/API to certain permissions. For example,
if you only went `employees` to be able to access the VPN service and not 
`students`, you can. in addition to profile restrictions (see next section) 
prevent them from accessing the service at all.

In `/etc/vpn-user-portal/config.php` you can configure it like this:

    'accessPermissionList' => ['employees'],

This requires everyone to have the permission `employees`. If you specify more
than one "permission", the user needs to be member of only one. The permissions
are thus "OR".

In order to provide access to the "Admin" part of the portal, see 
[PORTAL_ADMIN](PORTAL_ADMIN.md).

## Profile Mapping

Modify `/etc/vpn-server-api/config.php`, and set the `enableAcl` to 
`true` and add the authorized attribute values to `aclPermissionList` for each 
of the profiles where you want to restrict access, for example:

    // Whether or not to enable ACLs for controlling who can connect
    // DEFAULT = false
    'enableAcl' => true,

    // The list of groups to allow access, requires enableAcl to be 
    // true
    // DEFAULT  = []
    'aclPermissionList' => [
        'http://eduvpn.org/role/admin',
    ],
