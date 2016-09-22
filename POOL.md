# Pool Configuration

For this document we assume your _instance_ is running as 
`https://vpn.example/`, change the domain name accordingly.

Pools, as configured in `/etc/vpn-server-api/vpn.example/config.yaml` can 
contain many options. These are described in this document, together with their
default values.

| Option | Description | Required | Default Value |
| ------ |------------ | -------- | ------------- |
| `displayName`      | The name of the pool as shown to the user | yes | _N/A_ |
| `extIf`            | The external interface which connects to the Internet or to the network you want to reach through the VPN | yes | _N/A_ |
| `range`            | The IPv4 range of the network that will be assigned to clients | yes | _N/A_ |
| `range6`           | The IPv6 range of the network that will be assigned to clients | yes | _N/A_ | 
| `hostName`         | The hostname the VPN client will connect to | yes | _N/A_ |
| `listen`           | The *IPv4* address the OpenVPN process will listen on | no | `0.0.0.0` |
| `useNat`           | Whether or not to NAT the `range` and `range6` network to the `extIf` | no | `true` |
| `forward6`         | Whether or not to forward IPv6 traffic, useful when your VPN server does not have IPv6 connectivity | no | `false` | 
| `defaultGateway`   | Whether or not to route all traffic from the client over the VPN | no | `true` | 
| `routes`           | IPv4 and IPv6 routes to push to the client, only used when `defaultGateway` is `false` | no | `[]` |
| `dns`              | IPv4 and IPv6 address of DNS server(s) to push to the client, only used when `defaultGateway` is `true` | no | `[]` |
| `twoFactor`        | Whether or not to enable two-factor authentication, see [Two-factor](2FA.md) documentation | no | `false` |
| `clientToClient`   | Whether or not to allow client-to-client traffic | no | `false` |
| `enableLog`        | Whether or not to enable OpenVPN logging | no | `false` |
| `enableAcl`        | Whether or not to enable ACLs for controlling who can connect | no | `false` |
| `aclGroupList`     | The list of groups to allow access, requires `enableAcl` to be `true` | no | `[]` |
| `aclGroupProvider` | The provider to use for retrieving group membership, see [ACL](ACL.md) documentation | no | _N/A_ |
| `blockSmb`         | Whether or not to block Samba/CIFS traffic to the Internet | no | `false` |
