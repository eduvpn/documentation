---
title: Portal Administrators
description: How to configure admin users for the portal
category: howto
---

Certain users can be "promoted" to admin in the VPN portal. This can be done in
two ways, based on either

1. User ID
2. Permission

The User ID based "admin" authorization is the simplest. However, if the 
admins regularly change, or are already based on a certain role exposed through 
the identity management system, using permissions may make more sense.

### User ID

The default deploy, using `deploy_${DIST}.sh` sets the `admin` user as an
admin in `/etc/vpn-user-portal/config.php` using the `adminUserIdList` 
configuration array:

    'adminUserIdList' => ['admin'],

You can mark additional users as admins:

    'adminUserIdList' => ['admin', 'john', 'jane'],

This is the simplest solution. To view the user ID of your account, you can use 
the "Account" page when logged into the portal. For SAML deployments using the 
`eduPersonTargetedID` attribute, it would look like this:

    'adminUserIdList' => [
        'https://idp.tuxed.net/metadata!https://vpn.tuxed.net/vpn-user-portal/_saml/metadata!g1Bd2dM7ugdEVZlpKBoWUCL3GWc4LdewUW1YkgUnVEg',
        'https://engine.test.surfconext.nl/authentication/idp/metadata!https://vpn.tuxed.net/vpn-user-portal/_saml/metadata!87e996c1735dec301cf67788f22c978f7fd9868d',
    ],

In case the used user ID attribute is a pseudonym as above, you'd have to ask
the other future admins to go to their "Account" page and tell you the user ID.

### Permission

When the "admins" are already decided on through the identity management 
system, e.g. LDAP or SAML, it makes sense to use that "permission" / "role" to 
identify users.

**NOTE**: if multiple (SAML) IdPs are linked to the VPN service, there is no 
way to "scope" the permission to a particular IdP at the moment. So be careful
when using a permission based "admin" as IdPs can potentially set the "admin"
permission for users not allowed to access the admin part of the portal! In 
that case you SHOULD use the User ID admin configuration mentioned above 
instead!

In order to configure the permissions, first the attribute has to be selected 
for this. This can be for example the `eduPersonEntitlement` attribute where 
the administrators get the "admin" entitlement. 

One can set the `permissionAttribute` under the various authentication 
mechanisms, see the configuration [template](https://github.com/eduvpn/vpn-user-portal/blob/v2/config/config.php.example). 

For example on [Shibboleth](SHIBBOLETH_SP.md):

    'permissionAttribute' => 'entitlement',

**NOTE** since version 2.0.7 of vpn-user-portal, the value of 
`permissionAttribute` can also be an array, so it can list multiple attributes.

Then you have to configure _which_ entitlement will grant administrator access
using the `adminPermissionList` option, for example:

    'adminPermissionList' => ['http://eduvpn.org/permission/admin'],

This should make all users that have that particular entitlement value an 
administrator in the portal.
