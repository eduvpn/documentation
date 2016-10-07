# Pool Configuration

For this document we assume your _instance_ is running as 
`https://vpn.example/`, change the domain name accordingly.

Pools, as configured in `/etc/vpn-server-api/vpn.example/config.yaml` can 
contain many options to support various deployment scenarios. These are 
described in this document, together with their default values. Read more 
about multi-pool configurations [here](MULTI_POOL.md).

The VPN pools are configured in the `vpnPools` section, e.g.:

    vpnPools:
        internet:
            displayName: Internet Access
            hostName: vpn.example
            ...
            ...

Here `internet` is the internal identifier that will be used to keep track 
of the various pools you may define here.

If you modify any of these values as described below, you need to regenerate 
the server configuration and the firewall:

    $ sudo vpn-server-api-server-config --instance vpn.example
    $ sudo vpn-server-api-generate-firewall --install

**TODO**: write a tool that automatically enables the OpenVPN units and 
restarts the processes, or at least give a copy/paste solution.

| Option | Description | Required | Default Value |
| ------ |------------ | -------- | ------------- |
| `displayName`      | The name of the pool as shown in the user and admin portals | yes | _N/A_ |
| `extIf`            | The external interface which connects to the Internet or to the network you want to reach through the VPN | yes | _N/A_ |
| `range`            | The IPv4 range of the network that will be assigned to clients | yes | _N/A_ |
| `range6`           | The IPv6 range of the network that will be assigned to clients | yes | _N/A_ | 
| `hostName`         | The hostname the VPN client will connect to | yes | _N/A_ |
| `listen`           | The *IPv4* address the OpenVPN process will listen on, **MUST** be unique between any pool and instance, the default can only be used if there is only one pool and one instance | no | `0.0.0.0` |
| `useNat`           | Whether or not to NAT the `range` and `range6` network to the `extIf` | no | `false` |
| `forward6`         | Whether or not to forward IPv6 traffic, useful when your VPN server does not have IPv6 connectivity | no | `false` | 
| `defaultGateway`   | Whether or not to route all traffic from the client over the VPN | no | `false` | 
| `routes`           | IPv4 and IPv6 routes to push to the client, only used when `defaultGateway` is `false` | no | `[]` |
| `dns`              | IPv4 and IPv6 address of DNS server(s) to push to the client, only used when `defaultGateway` is `true` | no | `[]` |
| `twoFactor`        | Whether or not to enable two-factor authentication, see [Two-factor](2FA.md) documentation | no | `false` |
| `clientToClient`   | Whether or not to allow client-to-client traffic | no | `false` |
| `enableLog`        | Whether or not to enable OpenVPN logging | no | `false` |
| `enableAcl`        | Whether or not to enable ACLs for controlling who can connect | no | `false` |
| `aclGroupList`     | The list of groups to allow access, requires `enableAcl` to be `true` | no | `[]` |
| `aclGroupProvider` | The provider to use for retrieving group membership, see [ACL](ACL.md) documentation | no | _N/A_ |
| `blockSmb`         | Whether or not to block Samba/CIFS traffic to the Internet | no | `false` |
| `processCount`     | The number of OpenVPN processes to use for this range, MUST be 1, 2, 4 or 8. In case `processCount` is 2, 4 or 8 the last OpenVPN process will use TCP | no | `4` |
