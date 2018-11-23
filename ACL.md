# ACL

The VPN service supports group ACLs, i.e. require users to be a member of a 
certain group before allowing downloading configurations and to access to the 
VPN service for profiles that have ACLs enabled.

The ACLs need to be configured in `/etc/vpn-server-api/default/config.php` and 
the ACL methods, i.e. the way how to obtain the membership information, in 
`/etc/vpn-user-portal/default/config.php`.

## Enabling ACLs

Add

    enableAcl: true
    aclGroupList: ['all']

To `/etc/vpn-server-api/default/config.php` for the profile you want to 
enable the ACL for. Here, the group with identifier `all` is given access.

There are a number of backends available to fetch group membership 
information and they are also configured here.

### SAML 

We assume [SAML](SAML.md) is already configured and working.

You have to choose an SAML attribute you want to use that contains the values
you configured in `aclGroupList` mentioned above. Typically, that would be 
`eduPersonEntitlement` or `eduPersonAffiliation`, but any SAML attribute will 
work. You MAY need to specify the OID variant as shown in the example below.

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
        //'entitlementAttribute' => 'MELLON_urn:oid:1_3_6_1_4_1_5923_1_1_1_7',
    ],

### LDAP

We assume [LDAP](LDAP.md) is already configured and working. 

You have to choose an LDAP attribute you want to use that contains the values
you configured in `aclGroupList` mentioned above. Typically, that would be 
`memberOf`, `eduPersonEntitlement` or `eduPersonAffiliation`, but any LDAP 
attribute will work.

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
        //'entitlementAttribute' => 'memberOf',
    ],

### VOOT

**NOTE**: this method is DEPRECATED. Use SAML instead with e.g. 
`eduPersonEntitlement`.

We assume [SAML](SAML.md) is already configured and working.

The [VOOT protocol](http://openvoot.org/) is used to retrieve group 
memberships. The example below is for the 
[SURFteams](https://teams.surfconext.nl) component of 
[SURFconext](https://www.surf.nl/en/services-and-products/surfconext/index.html).

The `clientId` and `clientSecret` mentioned below need to be replaced with the 
actual secrets obtained when registering at SURFconext. The redirect URI 
that needs to be registered is `https://vpn.example/portal/_voot/callback` 
where `vpn.example` is replaced with your actual domain.

In order to configure this, modify `/etc/vpn-user-portal/default/config.php` 
and set the following:

    'enableVoot' => true,
    'Voot' => [
        'clientId' => 'my_client_id',
        'clientSecret' => 'my_client_secret',
        'authorizationEndpoint' => 'https://authz.surfconext.nl/oauth/authorize',
        'tokenEndpoint' => 'https://authz.surfconext.nl/oauth/token',
        'apiUrl' => 'https://voot.surfconext.nl/me/groups',
    ],

The group membership will be automatically obtained when the user logs in, and
can be verified on the "Account" tab in the user portal.
