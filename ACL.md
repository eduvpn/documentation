# ACL

The VPN service supports group ACLs, i.e. require users to be a member of a 
certain group before allowing downloading configurations and to access to the 
VPN service for pools that have ACLs enabled. Below we assume you are deploying 
for the instance with domain `vpn.example`.

The ACLs need to be configured in `/etc/vpn-server-api/vpn.example/config.yaml`.

## Enabling ACLs

Add

    enableAcl: true
    aclGroupProvider: StaticProvider
    aclGroupList: [all]

To `/etc/vpn-server-api/vpn.example/config.yaml` for the pool you want to 
enable the ACL for. Here, the group with identifier `all` is given access.

There are a number of backends available to fetch group membership 
information and they are also configured here.

### StaticProvider

    groupProviders:
        StaticProvider:
            all:
                displayName: All
                members: [foo, bar]
            students:
                displayName: Students
                members: [foo]
            employees:
                displayName: Employees
                members: [bar]

Here you can add the various user IDs to the group ID to give them access to
the pool. Make sure the group ID, here `all`, `students` and `employees` 
matches with the ID as specified in `aclGroupList` in your pool configuration.

### VootProvider

This method uses the [VOOT protocol](http://openvoot.org/) to retrieve group 
memberships. The example below is for the 
[SURFteams](https://teams.surfconext.nl) component of 
[SURFconext](https://www.surf.nl/en/services-and-products/surfconext/index.html).

Set `aclGroupProvider` in your pool configuration to `VootProvider` and 
add `VootProvider` to the `groupProviders` section:

    groupProviders:
        VootProvider:
            apiUrl: 'https://voot.surfconext.nl/me/groups'

The group identifiers as returned by the VOOT API calls need to be specified
in the `aclGroupList` in your pool configuration.

This module works together with the portal to obtain an access token per user
that will be used to retrieve the group membership. The portal also needs to
be configured to enable Voot in `/etc/vpn-user-portal/vpn.example/config.yaml`: 

    enableVoot: true
    Voot:
        clientId: my_client_id
        clientSecret: my_client_secret
        authorizationEndpoint: 'https://authz.surfconext.nl/oauth/authorize'
        tokenEndpoint: 'https://authz.surfconext.nl/oauth/token'

Here the `clientId` and `clientSecret` need to be replaced with the actual 
secrets obtained when registering the portal for SURFconext. The redirect URI 
that needs to be registered is 
`https://vpn.example/portal/_voot/callback`.

The group membership will be automatically obtained when the user logs in.
