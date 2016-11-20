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
the server configuration, see the [Apply Changes](#apply-changes) section below.

## Options

| Option | Description | Required | Default Value |
| ------ |------------ | -------- | ------------- |
| `profileNumber`    | The number of this profile, every profile per instance has a unique number | yes | _N/A_ |
| `displayName`      | The name of the profile as shown in the user and admin portals | yes | _N/A_ |
| `extIf`            | The external interface which connects to the Internet or to the network you want to reach through the VPN | yes | _N/A_ |
| `range`            | The IPv4 range of the network that will be assigned to clients | yes | _N/A_ |
| `range6`           | The IPv6 range of the network that will be assigned to clients | yes | _N/A_ | 
| `hostName`         | The hostname the VPN client(s) will connect to | yes | _N/A_ |
| `listen`           | The address the OpenVPN processes will listen on, see [OpenVPN Processes](#openvpn-processes) | no | `::` |
| `managementIp`     | Override the auto assigned `managementIp` based on `instanceNumber` and `profileNumber` with a chosen IP | no | `auto` |
| `portShare`        | Indicate that the OpenVPN processes cannot take `tcp/443` but share it with a web server, see [OpenVPN Processes](#openvpn-processes) | no | `true` |
| `useNat`           | Whether or not to NAT the `range` and `range6` network to the `extIf` | no | `false` |
| `reject4`          | Do not forward IPv4 traffic, useful for creating an IPv6 only VPN | no | `false` |
| `reject6`          | Do not forward IPv6 traffic, useful when the VPN server does not have IPv6 connectivity | no | `false` |
| `defaultGateway`   | Whether or not to route all traffic from the client over the VPN | no | `false` | 
| `routes`           | IPv4 and IPv6 routes to push to the client, only used when `defaultGateway` is `false` | no | `[]` |
| `dns`              | IPv4 and IPv6 address of DNS server(s) to push to the client, only used when `defaultGateway` is `true` | no | `[]` |
| `twoFactor`        | Whether or not to enable two-factor authentication, see [Two-factor](2FA.md) documentation | no | `false` |
| `clientToClient`   | Whether or not to allow client-to-client traffic | no | `false` |
| `enableLog`        | Whether or not to enable OpenVPN logging | no | `false` |
| `enableAcl`        | Whether or not to enable ACLs for controlling who can connect | no | `false` |
| `aclGroupList`     | The list of groups to allow access, requires `enableAcl` to be `true` | no | `[]` |
| `aclGroupProvider` | The provider to use for retrieving group membership, see [ACL](ACL.md) documentation | no | `StaticProvider` |
| `blockSmb`         | Whether or not to block Samba/CIFS traffic to the Internet | no | `false` |
| `processCount`     | The number of OpenVPN processes to use for this range, MUST be 1, 2, 4 or 8. See [OpenVPN Processes](#openvpn-processes) | no | `4` |
| `hideProfile`      | Hide the profile from the user portal, i.e. do not allow the user to choose it | no | `false` |

### OpenVPN Processes

This number determines the number op OpenVPN processes that are being used for
this particular node. The table below is influenced by the `portShare` and 
`listen` configuration options, see below.

| `processCount` | Protocol/Port |
|----------------|---------------|
| 1              | `udp/1194`            |
| 2              | `udp/1194`, `tcp/443` |
| 4 (default)    | `udp/1194`, `udp/1195`, `tcp/1194`, `tcp/443` |
| 8              | `udp/1194`, `udp/1195`, `udp/1196`, `udp/1197`, `udp/1198`, `tcp/1194`, `tcp/1195`, `tcp/443` |

By default, `listen` is `::` which is a special address that allows OpenVPN to
receive connections both on IPv4 and IPv6. If you manually set `listen`, it 
will only listen on the specified address and family.

The `portShare` option indicates that you use SNI Proxy to share the `tcp/443` 
connection with the web server. In that case, OpenVPN will not listen on 
`tcp/443` but on the next consecutive port available, e.g. when `processCount` 
is 4, it will listen on `tcp/1195` and SNI Proxy will forward non-SNI traffic
to this port. 

If you run [Multi Instance](MULTI_INSTANCE.md) or 
[Multi Profile](MULTI_PROFILE.md) you MUST choose a unique `listen` address per
profile, which means you cannot use the special address `::` and thus lose the
IPv4+IPv6 connectivity option. You can manually work around this by using a 
proxy like [socat](http://www.dest-unreach.org/socat/) and configure SNI Proxy
to also forward IPv6 traffic.

## Apply Changes

Assuming you made changes in the instance `vpn.example` in the profile 
`internet`, you would regenerate the configuration like this:

    $ sudo vpn-server-node-server-config --instance vpn.example --profile internet

To restart all OpenVPN processes belonging to the profile `internet` for the 
instance `vpn.example` do this:

    $ sudo systemctl restart openvpn@server-vpn.example-internet-{0,1,2,3}

To regenerate and install the new firewall rules, run this:

    $ sudo vpn-server-node-generate-firewall --install

To activate the firewall, do this:

    $ sudo systemctl restart iptables
    $ sudo systemctl restart ip6tables
