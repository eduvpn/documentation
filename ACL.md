# ACL

The VPN service supports ACLs, i.e. determine if a particular user is 
authorized / entitled / member before allowing access a certain VPN profile. 
This is useful if you have different "user groups" where not everyone should 
have access to all VPN profiles. E.g.: only employees get access to the 
"Employees" profile, but students do not.

The following ACL mechanisms are supported:

- SAML (via SAML attribute)
- LDAP (via LDAP attribute)
- VOOT (via [OpenVOOT](https://openvoot.org/) REST API in combination with
  SAML authentication) **DEPRECATED**

## Configuration

The ACL mechanisms, from the list above, are configured in 
`/etc/vpn-user-portal/default/config.php`. Mapping the ACL values, e.g. which 
"entitlement" or "group" is required to access a certain profile, is configured 
in `/etc/vpn-server-api/default/config.php`.

The authorization / entitlement / membership is valid for the duration of the
session, as configured with the `sessionExpiry` configuration option in 
`/etc/vpn-user-portal/default/config.php`. The default is 90 days (`P90D`). For 
some organizations this SHOULD be reduced, to e.g. 12 hours (`PT12H`). Changes
in the authorization / entitlement / membership are only picked up *after* 
the session expiry.

### Mechanisms 

#### SAML 

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

#### LDAP

We assume [LDAP](LDAP.md) is already configured and working. 

You have to choose an LDAP attribute you want to use for determining the 
membership. ypically, that would be `memberOf`, `eduPersonEntitlement` or 
`eduPersonAffiliation`, but any LDAP attribute will work.

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

#### VOOT

**NOTE**: this method is DEPRECATED and **NOT** supported! Use SAML with 
attributes instead with e.g. `eduPersonEntitlement`.

You need to register the "redirect URI" at the VOOT provider, the URL has the
format `https://vpn.example/portal/_voot/callback`.

Modify `/etc/vpn-user-portal/default/config.php`:

    'enableVoot' => true,
    'Voot' => [
        'clientId' => 'my_client_id',
        'clientSecret' => 'my_client_secret',
        'authorizationEndpoint' => 'https://authz.surfconext.nl/oauth/authorize',
        'tokenEndpoint' => 'https://authz.surfconext.nl/oauth/token',
        'apiUrl' => 'https://voot.surfconext.nl/me/groups',
    ],

Once you authenticate to the portal, on the "Account" page, i.e. 
`https://vpn.example/vpn-user-portal/account`, you should see the 
"Group Membership(s)" listed there.

### Mapping

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
