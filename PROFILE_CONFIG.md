---
title: Profile Configuration
description: List of all VPN Server Configuration Options
category: configuration
---

For this document we assume you used the included `deploy_${DIST}.sh` script.

Profiles, are configured in `/etc/vpn-user-portal/config.php` and
can contain many options to support various deployment scenarios. These are 
described in the table below.

To modify any of the options, modify the file mentioned above and look for the
`vpnProfiles` section, e.g:

```
'vpnProfiles' => [
    'default' => [
        'displayName' => 'Default',
        ...
        ...
    ],
],
```

Every profile has an identifier (`profileId`) in this case `internet`. It must 
be unique.

On Fedora you may also need to take a look at the [SELinux](SELINUX.md) 
instructions.

## Options

This table describes all available profile configuration options. The 
"Default Value" column indicates what the value is if the option is _missing_ 
from the configuration.

| Option                 | Description                                                                                                                                                                 | Required | Default Value              | Deploy Value               |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | -------------------------- | -------------------------- |
| `displayName`          | The name of the profile as shown in the user and admin portals                                                                                                              | yes      | _N/A_                      | `Default`          |
| `rangeFour`                | The IPv4 range of the network that will be assigned to clients                                                                                                              | yes      | _N/A_                      | Random `10.X.Y.0/25`       |
| `rangeSix`               | The IPv6 range of the network that will be assigned to clients, the prefix MUST be <= 112 and divisible by 4 (the "smallest" range an OpenVPN process supports is `::/112`) | yes      | _N/A_                      | Random `fdX:Y:Z:A::/64`    |
| `hostName`             | The hostname the VPN client(s) will connect to                                                                                                                              | yes      | _N/A_                      | from `deploy_${DIST}.sh`   |
| `defaultGateway`       | Whether or not to route all traffic from the client over the VPN                                                                                                            | no       | `false`                    | `true`                     |
| `blockLan`             | Block traffic to local LAN when VPN is active                                                                                                                               | no       | `false`                    | `true`                     |
| `routeList`               | IPv4 and IPv6 routes to push to the client. Use "prefix notation", e.g. `192.168.1.0/24`, `fd01:1:1:1::/64`                           | no       | `[]`                       | `[]`                       |
| `dnsList`                  | IPv4 and IPv6 address of DNS server(s) to push to the clients. See [DNS](#dns)                                                                                              | no       | `[]`                       | `['9.9.9.9', '2620:fe::fe']` (https://www.quad9.net/) |
| `dnsDomain`            | Specify the "Connection-specific DNS Suffix"                                                                                             | no       | `null`                     | `null`                     |
| `dnsDomainSearch`      | Specify the "Connection-specific DNS Suffix Search List"                                                                                 | no       | `[]`                       | `[]`                       |
| `clientToClient`       | Whether or not to allow client-to-client traffic                                                                                                                            | no       | `false`                    | `false`                    |
| `enableLog`            | Whether or not to enable OpenVPN [logging](#logging)                                                                                                                        | no       | `false`                    | `false`                    |
| `enableAcl`            | Whether or not to enable [ACL](ACL.md)s for controlling who can connect                                                                                                     | no       | `false`                    | `false`                    |
| `aclPermissionList`    | List of acceptable permissions (OR) for access to this profile. Requires `enableAcl` to be `true`, see [ACL](ACL.md)                                                        | no       | `[]`                       | `[]`                       |
| `vpnProtoPorts`        | The protocol and port to listen on. Must contain 1, 2, 4, 8, 16, 32 or 64 entries. See [OpenVPN Processes](#openvpn-processes)                                              | no       | `['udp/1194', 'tcp/1194']` | `['udp/1194', 'tcp/1194']` |
| `exposedVpnProtoPorts` | Modify the VPN protocols and ports exposed to VPN clients. By default `vpnProtoPorts` is used. Useful for VPN [Port Sharing](PORT_SHARING.md) with e.g. `tcp/443`           | no       | `[]`                       | `[]`                       |

The following options _MAY_ break the client when insuffient care is taken, 
unless the eduVPN/Let's Connect! applications are used:

* `hostName`: unless you point the currently used hostName to the new host 
  (using DNS);
* `vpnProtoPorts`: if you change to ports not currently used by the 
  client(s);
* `exposedVpnProtoPorts`: if you change to ports not currently used by the 
  client(s);

### DNS

To configure the DNS addresses that are pushed to the VPN clients you can use
the `dns` configuration field. It takes an array of IPv4 and/or IPv6 addresses. 
If the field is left empty, e.g. `[]` or missing, no DNS servers are pushed to 
the VPN clients.

Two "special" addresses, `@GW4@` and `@GW6@`, can be used as well that will be 
replaced by the IPv4 and IPv6 gateway addresses for use with 
[LOCAL_DNS](LOCAL_DNS.md).

When `defaultGateway` is set to `true`, an additional option is pushed to the
VPN clients: `block-outside-dns`. This option has, as of this moment, only 
effect on Windows. On Windows, DNS queries go out over all (configured) 
interfaces and the first response is used. This can create a 
[DNS leak](https://en.wikipedia.org/wiki/DNS_leak). By providing the 
`block-outside-dns` option, this is prevented.

You can specify the "Connection-specific DNS Suffix" and 
"Connection-specific DNS Suffix Search List" by using the `dnsDomain` and
`dnsDomainSearch` options. The first one takes a `string` the second an array 
of type `string`, for example:

```
'dnsDomain'       => 'clients.example.org',
'dnsDomainSearch' => ['example.org', 'example.com'],
```

The `dnsDomain` is NOT used for "searches", so you MAY need to provide it to 
`dnsDomainSearch` as well if you want that domain to be searched as well.

### OpenVPN Processes

You can configure OpenVPN processes using the `listen` and `vpnProtoPorts` 
configuration fields. 

By default, `listen` is `::` which is a special address that allows OpenVPN to
receive connections both on IPv4 and IPv6. If you manually set `listen`, it 
will only listen on the specified address, which will be either IPv4 or IPv6,
but not both.

By default 2 OpenVPN processes will be started, one listening on `udp/1194` and
one on `tcp/1194`. You can modify these ports and protocols as you see fit, but
the total number of them must be either 1, 2, 4, 8, 16, 32 or 64. This is 
because the total available IP range will be split among them. Depending on 
your address space the ideal number of simultaneous clients per process is 
around 64. So if you have a `/24` network, you'd probably want to run 4 
OpenVPN processes, e.g.: `['udp/1194', 'udp/1195', 'udp/1196', 'tcp/1194']`.

You can also specify ports like `udp/53` and `tcp/443`, but then those ports
need to be available to be claimed by OpenVPN and can't be shared by a DNS 
server or web server. If you want to use `tcp/443` also to receive OpenVPN 
connections, see [Port Sharing](PORT_SHARING.md).

If you run [Multi Profile](MULTI_PROFILE.md) you MUST either choose a unique 
`listen` address per profile if you want to use the same ports, which means you 
cannot use the special address `::` and thus lose the IPv4+IPv6 connectivity 
option, or use different ports. 

The first profile can use `udp/1194` and `tcp/1194`, the second one can use 
`udp/1195` and `tcp/1195` for example.

You can manually work around providing both IPv4+IPv6 for profiles where you 
specify a `listen` address by using a proxy like 
[socat](http://www.dest-unreach.org/socat/).

If you are planning to run many OpenVPN server processes, i.e. >= 10, make sure
to read [this](LIMIT_N_PROC.md) as you may need to increase the limit of the 
number of OpenVPN processes that can be started by the OpenVPN systemd service.

### Logging

Once logging is enabled and changes applied, you can follow the log like this:

```bash
$ sudo journalctl -f -t openvpn
```

## Apply Changes

To apply the configuration changes:

```bash
$ sudo vpn-maint-apply-changes
```

If the command is not available, install the `vpn-maint-scripts` package first.
