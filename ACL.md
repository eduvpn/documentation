# ACL

The VPN service supports group ACLs, i.e. require users to be a member of a 
certain group before allowing downloading configurations and to access to the 
VPN service for pools that have ACLs enabled.

The ACLs need to be configured in `/etc/vpn-server-api/acl.yaml` and 
`/etc/vpn-server-api/pools.yaml`. 

## Enabling ACLs

Add

    enableAcl: true

To `/etc/vpn-server-api/pools.yaml` for the pool you want to enable the ACL 
for.

There are a number of backends available to fetch group membership 
information and they are configured in `/etc/vpn-server-api/acl.yaml`.

### StaticAcl

    aclMethod: StaticAcl

    StaticAcl:
        default: [me]

Here you can add the various user IDs to the pool ID to give them access to
the pool. Make sure the pool ID, here `default` matches with the ID as 
specified in `/etc/vpn-server-api/pools.yaml`.

### RemoteAcl

    aclMethod: RemoteAcl

    RemoteAcl:
        apiUrl: https://example.org/groups

This backend will fetch the URL and expecting a JSON document. The result 
should be of this format:

    {
        "data": {
            "groups": {
                "me": [
                    "default"
                ],
                "you": [
                    "office",
                    "default"
                ]
            }
        }
    }

As with StaticAcl, the name of the group must match the Pool ID. This 
shows that the user `me` is a member of the group `default` and the user `you` 
a member of both `office` and `default`.

If there is any error with the HTTP request, or the data is malformed will 
be the same as the user not being a member of any groups.

### VootAcl

This method uses the [VOOT protocol](http://openvoot.org/) to retrieve group 
memberships. The example below is for the 
[SURFteams](https://teams.surfconext.nl) component of 
[SURFconext](https://www.surf.nl/en/services-and-products/surfconext/index.html).

    aclMethod: VootAcl

    VootAcl:
        apiUrl: https://voot.surfconext.nl/me/groups

        # the directory where VOOT tokens are stored per user
        tokenDir: /var/lib/vpn-server-api/users/voot_tokens

        # the key is the VOOT group ID, the value is an array with pool IDs
        aclMapping:
            'urn:voot:group:one': [default]
            'urn:voot:group:two': [default, other]

The mapping between pools and group identifiers is specified in `aclMapping`. 
So in the example above, if the user is a member of the group with identifier 
`urn:voot:group:two` they have access to both the `default` pool and the 
`other` pool.

This module works together with the portal to obtain an access token per user
that will be used to retrieve the group membership. The portal also needs to
be configured for the VootAcl, in `/etc/vpn-user-portal/config.yaml`: 

    enableVoot: false
    Voot:
        clientId: my_client_id
        clientSecret: my_client_secret
        authorizationEndpoint: https://authz.surfconext.nl/oauth/authorize
        tokenEndpoint: https://authz.surfconext.nl/oauth/token

Here the `clientId` and `clientSecret` need to be replaced with the actual 
secrets obtained when registering the portal. The `redirect_uri` that needs to
be registered is `https://DOMAIN.TLD/portal/_voot/callback`.

Currently, the user needs to manually trigger the process of obtaining the 
groups from the VOOT provider on the "Account" page.
