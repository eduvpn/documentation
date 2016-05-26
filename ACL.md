# ACL

The VPN service supports group ACLs, i.e. require users to be a member of a 
certain group before allowing access to the VPN service.

The ACLs need to be configured in `/etc/vpn-server-api/acl.yaml` and 
`/etc/vpn-server-api/pools.yaml`. 

## Enabling ACLs

Add

    enableAcl: true

To `/etc/vpn-server-api/pools.yaml` for the pool you want to enable the ACL 
for.

There are a number of backends available to fetch group membership 
information and they are configured in `/etc/vpn-server-api/acl.yaml`.

## StaticAcl

    aclMethod: StaticAcl

    StaticAcl:
        default: [me]

Here you can add the various user IDs to the pool ID to give them access to
the pool. Make sure the pool ID, here `default` matches with the ID as 
specified in `/etc/vpn-server-api/pools.yaml`.

## RemoteAcl

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

The shows that the user `me` is a member of the group `default` and the user
`you` a member of both `office` and `default`.

If there is any error with the HTTP request, or the data is malformed will 
be the same as the user not being a member of any groups.

## VootAcl

**WIP**
