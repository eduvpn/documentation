# Profile Configuration

For this document we assume your _instance_ is `vpn.example`, change the domain 
name accordingly in the examples below.

Profiles, are configured in `/etc/vpn-server-api/vpn.example/config.yaml` and
can contain many options to support various deployment scenarios. These are 
described in the table below.

To modify any of the options, modify the file mentioned above and look for the
`vpnProfiles` section under the profile identifier, e.g.:

    vpnProfiles:
        internet:
            displayName: Internet Access
            hostName: vpn.example
            ...
            ...

Here `internet` is the profile identifier. The identifier is used internally to
keep track of the various profiles you may have.

If you modify any of these values as described below, you need to regenerate 
the server configuration, see the [Apply Changes](#applychanges) section below.

## Options

| Option | Description | Required | Default Value |
| ------ |------------ | -------- | ------------- |
| `profileNumber`       | The number of this profile, every profile per instance has a unique number | yes | _N/A_ |
| `displayName`      | The name of the profile as shown in the user and admin portals | yes | _N/A_ |
| `extIf`            | The external interface which connects to the Internet or to the network you want to reach through the VPN | yes | _N/A_ |
| `range`            | The IPv4 range of the network that will be assigned to clients | yes | _N/A_ |
| `range6`           | The IPv6 range of the network that will be assigned to clients | yes | _N/A_ | 
| `hostName`         | The hostname the VPN client(s) will connect to | yes | _N/A_ |
| `listen`           | The *IPv4* address the OpenVPN process will listen on, **MUST** be unique between any profile and instance, the default can only be used if there is only one profile and one instance | no | `0.0.0.0` |
| `managementIp`     | Override the assigned `managementIp` based on `instanceNumber` and `profileNumber` with a chosen IP | no | _N/A_ |
| `dedicatedNode`    | Whether or not the node is dedicated to only run OpenVPN instances, it will listen on `::` supporting IPv6 as well | no | `false` |
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

## Apply Changes

Assuming you made changes in the instance `vpn.example` in the profile 
`internet`, you would regenerate the configuration like this:

    $ sudo vpn-server-node-server-config --instance vpn.example --profile internet

To restart all OpenVPN processes belonging to the profile `internet` for the 
instance `vpn.example` do this:

    $ sudo systemctl restart openvpn@server-vpn.example-internet-{0,3}

To regenerate and install the new firewall rules, run this:

    $ sudo vpn-server-node-generate-firewall --install

To activate the firewall, do this:

    $ sudo systemctl restart iptables
    $ sudo systemctl restart ip6tables
