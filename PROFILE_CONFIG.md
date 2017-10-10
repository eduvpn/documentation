# Profile Configuration

For this document we assume you used the included `deploy.sh` script.

Profiles, are configured in `/etc/vpn-server-api/default/config.php` and
can contain many options to support various deployment scenarios. These are 
described in the table below.

To modify any of the options, modify the file mentioned above and look for the
`vpnProfiles` section, e.g:

    'vpnProfiles' => [
        'internet' => [
            'profileNumber' => 1,
            'displayName' => 'Internet Access',
            ...
            ...
        ],
    ],

Every profile has an identifier (`profileId`) in this case `internet` and a 
number (`profileNumber`), in this case `1`. They must be unique. The counting 
starts at `1`.

If you modify any of these values as described below, you need to regenerate 
the server configuration and possibly the firewall, see the 
[Apply Changes](#apply-changes) section below.

You may also need to take a look at the [SELinux](SELINUX.md) instructions, 
CentOS only.

## Options

| Option | Description | Required | Default Value |
| ------ |------------ | -------- | ------------- |
| `profileNumber`    | The number of this profile, every profile per instance has a unique number | yes | _N/A_ |
| `displayName`      | The name of the profile as shown in the user and admin portals | yes | _N/A_ |
| `extIf`            | The external interface which connects to the Internet or to the network you want to reach through the VPN | yes | _N/A_ |
| `range`            | The IPv4 range of the network that will be assigned to clients | yes | _N/A_ |
| `range6`           | The IPv6 range of the network that will be assigned to clients, the prefix MUST be <= 124 and divisible by 4 | yes | _N/A_ | 
| `hostName`         | The hostname the VPN client(s) will connect to | yes | _N/A_ |
| `listen`           | The address the OpenVPN processes will listen on, see [OpenVPN Processes](#openvpn-processes) | no | `::` |
| `managementIp`     | The IP address to use for connecting to OpenVPN processes | no | `127.0.0.1` |
| `useNat`           | Whether or not to NAT the `range` and `range6` network to the `extIf` | no | `false` |
| `reject4`          | Do not forward IPv4 traffic, useful for creating an IPv6 only VPN | no | `false` |
| `reject6`          | Do not forward IPv6 traffic, useful when the VPN server does not have IPv6 connectivity | no | `false` |
| `defaultGateway`   | Whether or not to route all traffic from the client over the VPN | no | `false` | 
| `routes`           | IPv4 and IPv6 routes to push to the client, only used when `defaultGateway` is `false` | no | `[]` |
| `dns`              | IPv4 and IPv6 address of DNS server(s) to push to the client, only used when `defaultGateway` is `true` | no | `[]` |
| `twoFactor`        | Whether or not to enable two-factor authentication for connecting to the VPN server, see [Two-factor](2FA.md) documentation | no | `false` |
| `clientToClient`   | Whether or not to allow client-to-client traffic | no | `false` |
| `enableLog`        | Whether or not to enable OpenVPN logging | no | `false` |
| `enableAcl`        | Whether or not to enable ACLs for controlling who can connect | no | `false` |
| `aclGroupList`     | The list of groups to allow access, requires `enableAcl` to be `true` | no | `[]` |
| `blockSmb`         | Whether or not to block Samba/CIFS traffic to the Internet | no | `false` |
| `vpnProtoPorts`    | The protocol and port to listen on. Must contain 1, 2, 4 or 8 entries. See [OpenVPN Processes](#openvpn-processes) | no | `['udp/1194', 'tcp/1194']` |
| `hideProfile`      | Hide the profile from the user portal, i.e. do not allow the user to choose it | no | `false` |
| `tlsCrypt`         | Use `--tls-crypt` instead of `--tls-auth` for better security (OpenVPN >= 2.4). As of this moment (2017-06-14) this does NOT work on OpenVPN Connect (iOS, Android) | no | `false` |

### OpenVPN Processes

You can configure OpenVPN processes using the `listen` and `vpnProtoPorts` 
configuration fields. 

By default, `listen` is `::` which is a special address that allows OpenVPN to
receive connections both on IPv4 and IPv6. If you manually set `listen`, it 
will only listen on the specified address, which will be either IPv4 or IPv6,
but not both.

By default 2 OpenVPN processes will be started, one listening on `udp/1194` and
one on `tcp/1194`. You can modify these ports and protocols as you see fit, but
the total number of them must be either 1, 2, 4 or 8. This is because the 
total available IP range will be split among them. Depending on your address
space the ideal number of simultaneous clients per process is at most 64. So 
if you have a `/24` network, you'd probably want to run 4 OpenVPN processes, 
e.g.: `['udp/1194', 'udp/1195', 'udp/1196', 'tcp/1194']`.

You can also specify ports like `udp/53` and `tcp/443`, but then those ports
need to be available to be claimed by OpenVPN and can't be shared by a DNS 
server or web server.

If you run [Multi Profile](MULTI_PROFILE.md) you MUST either choose a unique 
`listen` address per profile if you want to use the same ports, which means you 
cannot use the special address `::` and thus lose the IPv4+IPv6 connectivity 
option, or use different ports. 

The first profile can use `udp/1194` and `tcp/1194`, the second one can use 
`udp/1195` and `tcp/1195` for example.

You can manually work around providing both IPv4+IPv6 for profiles where you 
specify a `listen` address by using a proxy like 
[socat](http://www.dest-unreach.org/socat/).

## Apply Changes

Assuming you made changes in the profile `internet`, you would regenerate the 
configuration like this:

    $ sudo vpn-server-node-server-config --profile internet

To restart all OpenVPN processes belonging to the profile `internet`, do this:

    $ sudo systemctl restart "openvpn-server@default-internet-*"

If you changed the entry `vpnProtoPorts`, to say 
`['udp/1194', 'udp/1195', 'tcp/1194', 'tcp/1195']` you now have two more 
OpenVPN processes to deal with:

Enable the two extra processes on boot:

    $ sudo systemctl enable openvpn-server@default-internet-{2,3}

(Re)start them all:

    $ sudo systemctl restart "openvpn-server@default-internet-*"

If you changed any of the port configuration(s), you also need to update the
firewall to allow the UDP/TCP ports through, in that case modify 
`/etc/vpn-server-node/firewall.php`.

### CentOS 

To regenerate and install the new firewall rules, run this:

    $ sudo vpn-server-node-generate-firewall --install

To activate the updated firewall, do this:

    $ sudo systemctl restart iptables
    $ sudo systemctl restart ip6tables

### Debian

To regenerate and install the new firewall rules, run this:

    $ sudo vpn-server-node-generate-firewall --install --debian

To activate the updated firewall, do this:

    $ sudo systemctl restart netfilter-persistent
