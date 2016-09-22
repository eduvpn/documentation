# Pool Configuration

For this document we assume your _instance_ is running as 
`https://vpn.example/`, change the domain name accordingly.

Pools, as configured in `/etc/vpn-server-api/vpn.example/config.yaml` can 
contain many options. These are described in this document, together with their
default values.

| Option | Description | Default Value |
| ------ |------------ | ------------- |
| `displayName`      | The name of the pool as shown to the user | _N/A_ |
| `extIf`            | The external interface which connects to the Internet or to the network you want to reach through the VPN | _N/A_ |
| `range`            | The IPv4 range of the network that will be assigned to clients | _N/A_ |
| `range6`           | The IPv6 range of the network that will be assigned to clients | _N/A_ | 
| `hostName`         | The hostname the VPN client will connect to | _N/A_ |
| `listen`           | The *IPv4* address the OpenVPN process will listen on | `0.0.0.0` |
| `useNat`           | Whether or not to NAT the `range` and `range6` network to the `extIf` | `true` |
| `forward6`         | Whether or not to forward IPv6 traffic, useful when your VPN server does not have IPv6 connectivity | `false` | 
| `defaultGateway`   | Whether or not to route all traffic from the client over the VPN | `true` | 
| `routes`           | IPv4 and IPv6 routes to push to the client, only used when `defaultGateway` is `false` | `[]` |
| `dns`              | IPv4 and IPv6 address of DNS server(s) to push to the client, only used when `defaultGateway` is `true` | `[]` |
| `twoFactor`        | Whether or not to enable two-factor authentication | `false` |
| `clientToClient`   | Whether or not to allow client-to-client traffic | `false` |
| `enableLog`        | Whether or not to enable OpenVPN logging | `false` |
| `enableAcl`        | Whether or not to enable ACLs for controlling who can connect | `false` |
| `aclGroupList`     | The list of groups to allow access, requires `enableAcl` to be `true` | `[]` |
| `aclGroupProvider` | The provider to use for retrieving group membership, see [ACL](ACL.md) documentation | _N/A_ |
| `blockSmb`         | Whether or not to block Samba/CIFS traffic to the Internet | `false` |
