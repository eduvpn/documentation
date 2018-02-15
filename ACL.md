# ACL

The VPN service supports group ACLs, i.e. require users to be a member of a 
certain group before allowing downloading configurations and to access to the 
VPN service for profiles that have ACLs enabled.

The ACLs need to be configured in `/etc/vpn-server-api/default/config.php`, and
possibly `/etc/vpn-user-portal/default/config.php`

## Enabling ACLs

Add

    enableAcl: true
    aclGroupList: ['all']

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

For [FreeIPA](https://www.freeipa.org/):

    'LdapProvider' => [
        // FreeIPA
        'ldapUri' => 'ldaps://ipa.example.org',
        'groupBaseDn' => 'cn=groups,cn=accounts,dc=example,dc=org',
        // {{UID}} will be replaced by the actual user ID
        'memberFilterTemplate' => 'member=uid={{UID}},cn=users,cn=accounts,dc=example,dc=org',
        'bindDn' => 'uid=vpn,cn=sysaccounts,cn=etc,dc=example,dc=org',
        'bindPass' => 's3cr3t',
    ],

Set the `ldapUri` to the URI of your LDAP server. If you are using LDAPS, you 
may need to obtain the CA certificate of the LDAP server and store it 
locally so it can be used to verify the LDAP server certificate. See the
CA section below.

The `groupBaseDn` is the DN where the groups you want to retrieve are located. 
The `memberFilterTemplate` is used to only return the groups the user is a 
member of.

On FreeIPA, creating a system account, as used in the `bindDn`, is described 
[here](https://www.freeipa.org/page/HowTo/LDAP).

For Active Directory: 

    'LdapProvider' => [
        // Active Directory
        'ldapUri' => 'ldap://ad.example.org',
        'groupBaseDn' => 'cn=Users,dc=example,dc=org',
        // {{DN}} will be replaced by the actual user DN obtained using
        // the userIdFilter configured below
        'memberFilterTemplate' => 'member={{DN}}',
        'userBaseDn' => 'cn=Users,dc=example,dc=org',
        // {{UID}} will be replaced by the actual user ID
        'userIdFilterTemplate' => 'sAMAccountName={{UID}}',
        'bindDn' => 'cn=Administrator,cn=Users,dc=example,dc=org',
        'bindPass' => 's3cr3t',
    ],

The same as for FreeIPA regarding LDAP URI and certificates, but there are some 
extra options here for AD as it is required to first figure out the DN of the 
user based on their user ID (`sAMAccountName`) before we can retrieve the list 
of groups the user is a member of.

Do **NOT** use the Administrator account as mentioned in the example for 
production deploys! Create a system or service account instead that can only 
be used to "bind" to the LDAP server and query it, with no additional 
permissions!

`userBaseDn` contains the users, typically this is the same as `groupBaseDn` 
on simple deployments. The `userIdFilterTemplate` is used to determine which 
LDAP attribute is used to determine the DN of the user.

#### CA

See [LDAP.md](LDAP.md#ca) for information on how to configure your LDAP's CA 
for use on CentOS and LDAP.

### VootProvider

This method uses the [VOOT protocol](http://openvoot.org/) to retrieve group 
memberships. The example below is for the 
[SURFteams](https://teams.surfconext.nl) component of 
[SURFconext](https://www.surf.nl/en/services-and-products/surfconext/index.html).

Add `VootProvider` to the `groupProviders` section in 
`/etc/vpn-server-api/default/config.php`:
    
    'groupProviders' => [
        'VootProvider' => [
            'clientId' => 'my_client_id',
            'clientSecret' => 'my_client_secret',
            'authorizationEndpoint' => 'https://authz.surfconext.nl/oauth/authorize',
            'tokenEndpoint' => 'https://authz.surfconext.nl/oauth/token',
            'apiUrl' => 'https://voot.surfconext.nl/me/groups',
        ],
    ],

The `clientId` and `clientSecret` need to be replaced with the actual 
secrets obtained when registering the portal for SURFconext. The redirect URI 
that needs to be registered is `https://vpn.example/portal/_voot/callback`.

The group identifiers as returned by the VOOT API calls need to be specified
in the `aclGroupList` in your profile configuration. You also need set set
`enableAcl` to `true`.

This module works together with the user portal to obtain an access token per 
user that will be used to retrieve the group membership. The portal also needs 
to be configured to enable Voot in `/etc/vpn-user-portal/default/config.php`: 

    'enableVoot' => true,
    'Voot' => [
        'clientId' => 'my_client_id',
        'clientSecret' => 'my_client_secret',
        'authorizationEndpoint' => 'https://authz.surfconext.nl/oauth/authorize',
        'tokenEndpoint' => 'https://authz.surfconext.nl/oauth/token',
    ],

The group membership will be automatically obtained when the user logs in, and
can be verified on the "Account" tab in the user portal.
