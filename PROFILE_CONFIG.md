---
title: Profile Configuration
description: List of all VPN Server Configuration Options
category: configuration
---

For this document we assume you used the included `deploy_${DIST}.sh` script.

Profiles, are configured in `/etc/vpn-user-portal/config.php` and
can contain many options to support various deployment scenarios. These are 
described in the table below.

The configuration file itself also contains explanations of all options and 
their (default) value. This document has some additional explanation and 
discusses some considerations.

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

Every profile has an identifier (`profileId`) in this case `default`. It must 
be unique.

On Fedora you may also need to take a look at the [SELinux](SELINUX.md) 
instructions.

## Options

This table describes all available profile configuration options. The 
"Default" column indicates what the value is if the option is _missing_ from 
the configuration.

| Option               | Type                   | Default                                             | Protocol  |
| -------------------- | ---------------------- | --------------------------------------------------- | --------- |
| [protoList](#protocol-list)          | `string[]`             | `['openvpn', 'wireguard']`                          | *         |
| [preferredProto](#preferred-protocol)     | `string`               | `openvpn` (or `wireguard`)                          | *         |
| [displayName](#display-name)       | `string`               | _N/A_                                               | *         |
| [hostName](#host-name)           | `string[]` or `string` | _N/A_                                               | *         |
| [defaultGateway](#default-gateway)     | `bool`                 | `true`                                              | *         |
| [routeList](#route-list)         | `string[]`             | `[]`                                                | *         |
| [excludeRouteList](#exclude-route-list)   | `string[]`             | `[]`                                                | *         |
| `dnsServerList`      | `string[]`             | `[]`                                                | *         |
| `nodeUrl`            | `string[]` or `string` | `http://localhost:41194`                            | *         |
| `aclPermissionList`  | `string[]`             | `null`                                              | *         |
| `dnsDomain`          | `string`               | `null`                                              | *         |
| `dnsDomainSearch`    | `string[]`             | `[]`                                                | *         |
| `wRangeFour`         | `string[]` or `string` | _N/A_                                               | WireGuard |
| `wRangeSix`          | `string[]` or `string` | _N/A_                                               | WireGuard |
| `oRangeFour`         | `string[]` or `string` | _N/A_                                               | OpenVPN   |
| `oRangeSix`          | `string[]` or `string` | _N/A_                                               | OpenVPN   |
| `blockLan`           | `bool`                 | `false`                                             | OpenVPN   |
| `clientToClient`     | `bool`                 | `false`                                             | OpenVPN   |
| `enableLog`          | `bool`                 | `false`                                             | OpenVPN   |
| `udpPortList`        | `int[]`                | `[1194]`                                            | OpenVPN   |
| `tcpPortList`        | `int[]`                | `[1194]`                                            | OpenVPN   |
| `exposedUdpPortList` | `int[]`                | `[]`                                                | OpenVPN   |
| `exposedTcpPortList` | `int[]`                | `[]`                                                | OpenVPN   |

The following options _MAY_ break the client when insuffient care is taken, 
unless the eduVPN/Let's Connect! applications are used:

* `hostName`: unless you point the currently used hostName to the new host 
  (using DNS);
* `udpPortList`, `tcpPortList`: if you change to ports not currently used by 
  the client(s);
* `exposedUdpPortList`, `exposedTcpPortList`: if you change to ports not 
  currently used by the client(s).

### Profile ID

The profile ID is used to uniquely identify a profile. It can only contain 
letters, `[a-z]`, numbers `[0-9]` and the dash (`-`). Examples of valid profile 
IDs identifiers are `employees`, `students`, `admin`.

### Protocol List

This option decides which VPN protocols are enabled for this profile. The 
option is a array of VPN protocols, e.g. only enable OpenVPN:

```
    'protoList' => ['openvpn'],
```

### Preferred Protocol

When your profile supports multiple protocols, this option can be used to set
the preferred protocol. This allows for example to transitioning (the majority 
of users) from OpenVPN to WireGuard without breaking existing configurations.

The preferred protocol only makes sense when both OpenVPN and WireGuard are
enabled, see [Protocol List](#protocol-list). If only one protocol is enabled,
that is automatically the preferred protocol.

### Display Name

Specify the name you want to give this profile. This will be visible to the
users and allows them to determine which protocol to select if more than one
is available.

### Host Name

This is the DNS name that VPN clients will use to connect to the VPN 
server. It is _highly recommended_ that you make the profile ID part of the 
DNS name to allow for effective load balancing, or moving profiles to different
servers. As an example, if your profile has the name `employees`, your DNS name
could be `employees.vpn.example.org`. Obviously, you can make this a `CNAME` to
`vpn.example.org` as long as you have only one server.

### Default Gateway

This option allows you to indicate to the VPN client that all their traffic
needs to be sent over the VPN.

### Route List

If you are _not_ using the VPN as a [Default Gateway](#default-gateway) you can
specify the _routes_ for which the VPN client needs to use the VPN. You use 
this in the scenario that some internal services need to be reachable by your
VPN clients, but you do not want all of the client's traffic over the VPN.

Example:

```
    `routeList` => ['10.223.140.0/24', 'fc5b:7c64:3001:a95f::/64'],
```

### Exclude Route List

TBD.


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
