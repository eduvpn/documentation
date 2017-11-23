# ACL

The VPN service supports group ACLs, i.e. require users to be a member of a 
certain group before allowing downloading configurations and to access to the 
VPN service for profiles that have ACLs enabled.

The ACLs need to be configured in `/etc/vpn-server-api/default/config.php`, and
possibly `/etc/vpn-user-portal/default/config.php`

## Enabling ACLs

Add

    enableAcl: true
    aclGroupList: [all]

To `/etc/vpn-server-api/default/config.php` for the profile you want to 
enable the ACL for. Here, the group with identifier `all` is given access.

There are a number of backends available to fetch group membership 
information and they are also configured here.

### StaticProvider

    'groupProviders' => [
        'StaticProvider' => [
            'all' => [
                'displayName' => 'All',
                'members' => ['foo', 'bar'],
            ],
            'students' => [
                'displayName' => 'Students',
                'members' => ['foo'],
            ],
            'employees' => [
                'displayName' => 'Employees',
                'members' => ['bar'],
            ],
        ],
    ],

Here you can add the various user IDs to the group ID to give them access to
the profile. Make sure the group ID, here `all`, `students` and `employees` 
matches with the ID as specified in `aclGroupList` in your profile 
configuration.

### LdapProvider

    'LdapProvider' => [
        'ldapUri' => 'ldap://ldap.example.org',
        'groupDn' => 'ou=Groups,dc=example,dc=org',
        'filterTemplate' => 'uniqueMember=uid={{UID}},ou=People,dc=example,dc=org',
    ],

Set the `ldapUri` to the URI of your LDAP server. You can also use TLS by 
using an URI like `ldaps://ldap.example.org`, and also provide the TCP port 
explicitly, e.g. `ldaps://ldap.example.org:636`. 

The `groupDn` is the DN where the groups you want to retrieve are located. The
`filterTemplate` is used to only return the groups the user is a member of. 
This example is for 
[Red Hat Directory Server](https://www.redhat.com/en/technologies/cloud-computing/directory-server).

### VootProvider

This method uses the [VOOT protocol](http://openvoot.org/) to retrieve group 
memberships. The example below is for the 
[SURFteams](https://teams.surfconext.nl) component of 
[SURFconext](https://www.surf.nl/en/services-and-products/surfconext/index.html).

Add `VootProvider` to the `groupProviders` section:
    
    'groupProviders' => [
        'VootProvider' => [
            'clientId' => 'my_client_id',
            'clientSecret' => 'my_client_secret',
            'authorizationEndpoint' => 'https://authz.surfconext.nl/oauth/authorize',
            'tokenEndpoint' => 'https://authz.surfconext.nl/oauth/token',
            'apiUrl' => 'https://voot.surfconext.nl/me/groups',
        ],
    ],

The group identifiers as returned by the VOOT API calls need to be specified
in the `aclGroupList` in your profile configuration.

This module works together with the portal to obtain an access token per user
that will be used to retrieve the group membership. The portal also needs to
be configured to enable Voot in `/etc/vpn-user-portal/default/config.php`: 

    'enableVoot' => true,
    'Voot' => [
        'clientId' => 'my_client_id',
        'clientSecret' => 'my_client_secret',
        'authorizationEndpoint' => 'https://authz.surfconext.nl/oauth/authorize',
        'tokenEndpoint' => 'https://authz.surfconext.nl/oauth/token',
    ],

Here the `clientId` and `clientSecret` need to be replaced with the actual 
secrets obtained when registering the portal for SURFconext. The redirect URI 
that needs to be registered is 
`https://vpn.example/portal/_voot/callback`.

The group membership will be automatically obtained when the user logs in.
