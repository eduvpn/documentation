# Introduction

The VPN service supports access control. This allows configuring that users 
require certain "permissions" to access a particular VPN profile. This is 
useful if you have multiple types of users. For example, only employees get 
access to the "Employees" profile, but students do not.

Currently, the following access control mechanisms are supported:

- SAML (via SAML attribute, e.g. `eduPersonAffiliation` or 
  `eduPersonEntitlement`)
- LDAP (via LDAP attribute, e.g. `memberOf`)

The permissions are _cached_ for up to a configurable period. By default this 
is 3 months, but can easily be modified. This cache is required, because not
all authentication backends have a way to validate the permissions 
"out of band", i.e. when the user is not actively authenticating.

# Configuration

The configuration is done in two locations:

- `/etc/vpn-user-portal/default/config.php`: configure which access control
  mechanism is used and the period for which to _cache_ the permissions;
- `/etc/vpn-server-api/default/config.php`: configure which profiles are 
  restricted by access control.

## Cache

The permission cache is configured in `/etc/vpn-user-portal/default/config.php`
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

In order to configure this, modify `/etc/vpn-user-portal/default/config.php` 
and set the `entitlementAttribute` to the name of the attribute:

    // SAML
    'MellonAuthentication' => [
        'attribute' => 'MELLON_NAME_ID',
        // 'OID for eduPersonTargetedID
        //'attribute' => 'MELLON_urn:oid:1_3_6_1_4_1_5923_1_1_1_10',
        // OID for eduPersonPrincipalName
        //'attribute' => 'MELLON_urn:oid:1_3_6_1_4_1_5923_1_1_1_6',

        // add the entityID of the IdP to the user ID. This MUST be enabled
        // if multiple IdPs are used *and* the attribute used for the user ID
        // is not enforced to be unique among the different IdPs
        'addEntityID' => false,

        // ** AUTHORIZATION | ENTITLEMENT **
        // OID for eduPersonEntitlement
        'entitlementAttribute' => 'MELLON_urn:oid:1_3_6_1_4_1_5923_1_1_1_7',
    ],

Once you authenticate to the portal, on the "Account" page, i.e. 
`https://vpn.example/vpn-user-portal/account`, you should see the 
"Group Membership(s)" listed there.

## LDAP

We assume [LDAP](LDAP.md) is already configured and working. 

You have to choose an LDAP attribute you want to use for determining the 
membership. Typically, that would be `memberOf`, but any LDAP attribute will work.

In order to configure this, modify `/etc/vpn-user-portal/default/config.php` 
and set the `entitlementAttribute` to the name of the attribute:

    // LDAP
    'FormLdapAuthentication' => [
        'ldapUri' => 'ldaps://ipa.example.org',
        // "{{UID}}" will be replaced with the username the user provides
        // on the login page
        'userDnTemplate' => 'uid={{UID}},cn=users,cn=accounts,dc=example,dc=org',
        // Active Directory
        //'userDnTemplate' => 'DOMAIN\{{UID}}',

        // ** AUTHORIZATION | ENTITLEMENT **
        // use eduPerson "eduPersonEntitlement"
        //'entitlementAttribute' => 'eduPersonEntitlement',

        // use LDAP "memberOf"
        'entitlementAttribute' => 'memberOf',
    ],

Once you authenticate to the portal, on the "Account" page, i.e. 
`https://vpn.example/vpn-user-portal/account`, you should see the 
"Group Membership(s)" listed there.

## Profile Mapping

Modify `/etc/vpn-server-api/default/config.php`, and set the `enableAcl` to 
`true` and add the authorized attribute values to `aclGroupList` for each of 
the profiles where you want to restrict access, for example:

    // Whether or not to enable ACLs for controlling who can connect
    // DEFAULT = false
    'enableAcl' => true,

    // The list of groups to allow access, requires enableAcl to be 
    // true
    // DEFAULT  = []
    'aclGroupList' => [
        'urn:example:LC-admin',
    ],
