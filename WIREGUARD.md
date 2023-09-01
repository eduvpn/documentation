# WireGuard

As WireGuard is new in 3.x, this document will try to dive into some more 
detail regarding how it works.

## Configuration

WireGuard in eduVPN / Let's Connect! has a lot less toggles than OpenVPN so 
should be easier to configure. For all configuration options, see:

* [Portal Config](PORTAL_CONFIG.md#wireguard)
* [Profile Config](PROFILE_CONFIG.md#wireguard)

## Comparison with OpenVPN

There are a number of differences between OpenVPN and WireGuard. Most of them 
are summed up in 
[this](https://www.tuxed.net/fkooman/blog/taming_wireguard.html) blog post.

## What to Use?

It is possible to configure profiles to support both OpenVPN and WireGuard 
simultaneously. We recommend to use WireGuard whenever possible, and only 
provide OpenVPN support for legacy reasons, _or_ when connecting over TCP is a
MUST, for example on broken networks that e.g. block UDP, or have MTU issues.

For most production scenarios we recommend to have the bulk of the users use
WireGuard, but at the same time reserve a little space for OpenVPN connections.

An example _partial_ configuration showing some VPN configuration options 
relevant for deploying WireGuard can be seen in the example below. Note that 
the defaults are perfectly fine in most cases!

```php

// ...

'WireGuard' => [
    // listen on port 443 which is the HTTP/3 (QUIC) port, higher change it is 
    // not blocked/mangled by firewalls... (default = 51820)
    'listenPort' => 443,
],

// we do not allow users to download VPN configuration files themselves through
// the portal (default = 3)
'maxActiveConfigurations' => 0,

'Api' => [
    // we allow users to connect with 2 VPN clients simultaneously 
    // (default = 3)
    'maxActiveConfigurations' => 2,
    
    // we consider a VPN client "gone" after 96 hours of no activity 
    // whatsoever, outlives also long weekends of laptop being suspended 
    // (default = 72 hours, i.e. PT72H)
    'appGoneInterval' => 'PT96H',
],

// ...

'ProfileList' => [
    [
        'profileId' => 'office',
        'displayName' => 'Office',
        'hostName' => 'office.vpn.example.org',
        'routeList' => [
            '192.168.1.0/24',
            'fd11::/64',
        ],
        
        // Prefer that VPN clients connect using WireGuard
        'preferredProto' => 'wireguard',
        
        // WireGuard
        'wRangeFour' => '10.42.42.0/24',
        'wRangeSix' => 'fd42:0:0:1::/64',

        // OpenVPN
        'oRangeFour' => '10.42.43.0/25',
        'oRangeSix' => 'fd42:0:0:2::/64',
        
        // do not use OpenVPN with UDP
        'oUdpPortList' => [],
        'oTcpPortList' => [1194],
        
        // ...
    ],
    
    // ...
],
```

## IP Management

When using WireGuard, as opposed to using OpenVPN, the IP address the VPN 
client will use needs to be determined _before_ starting the VPN "connection". 
There is no in-protocol negotiation. WireGuard configuration files therefore 
contain the IP address that the client will use. This means that the IP address 
will be reserved for the duration of the [session](SESSION_EXPIRY.md), by 
default 90 days. This is the case for both configuration file downloads through
the portal and when using the [API](API.md).

If there is enough IPv4 space available to assign to clients this is not a 
problem. If a `/24` prefix is available for 10 clients, this will typically 
suffice. However, if you do not have so much IP space available, for example
when using [public IP addresses](PUBLIC_ADDR.md), additional measures need to
be taken to make sure the IP space does not get quickly depleted. 

A number of measures were taken to avoid that, and improved upon during the 3.x
release:

1. Limit the number of per user manual VPN configuration file 
   [downloads](PORTAL_CONFIG.md#maximum-number-of-active-configurations) 
   through the portal (default = 3);
2. Limit the number of per user 
   [VPN connections](PORTAL_CONFIG.md#maximum-number-of-active-api-configurations) 
   when using the eduVPN/Let's Connect! apps (default = 3);
3. [Reclaim IP allocations](PORTAL_CONFIG.md#app-gone-interval) by the 
   eduVPN/Let's Connect! apps after they are considered "gone" 
   (default = after 72 hours).

The tooling for [monitoring](MONITORING.md) and optionally 
[alerting](MONITORING.md#alerting) based on server utilization have also 
improved to show the WireGuard IP allocations.

The defaults should suffice for most deployments, however you can tweak them if
necessary, follow the links in the list above for more information about each
of them.

## IP Prefix Changes

Changing the client IP prefix used for WireGuard clients is a bit more tricky
than with OpenVPN. The main difference between OpenVPN and WireGuard is that 
with OpenVPN the IP address assigned to the client is decided on _connect_ 
time, but with WireGuard it is decided ahead of time, i.e. when downloading the
configuration through the portal, or when the VPN app calls the `/connect` API 
endpoint.

When (completely) changing the IP prefix for WireGuard, all current 
configurations will be deleted when applying the changes and clients will stop
working. When *extending* the prefix, existing clients will keep working.

| Current Prefix   | New Prefix       | Result                             |
| ---------------- | ---------------- | ---------------------------------- |
| `192.168.0.0/24` | `10.0.0.0/24`    | VPN configurations will be deleted |
| `192.168.0.0/24` | `192.168.0.0/23` | VPN configurations will remain     | 

In the first scenario. Users of the VPN client applications will need to 
manually disconnect and then connect again to restart the VPN connection as the
old one will be "dead". Users that manually downloaded a VPN configuration file
through the portal will need to download a new one, the old one will no longer
work.

## MTU

We noticed some issues in the field when PPPoE and/or DS-Lite is used by ISPs. 
If the (Path) MTU of the connection between client and server is 1500, there is 
no issue, whether the connection is done over IPv4 or IPv6. The default MTU of 
WireGuard, which is 
[1420](https://lists.zx2c4.com/pipermail/wireguard/2017-December/002201.html) 
fits perfectly fine then. The WireGuard packet overhead is 80 bytes when 
connecting over IPv6, and 60 bytes when connecting over IPv4. So, if PPPoE is
used, which eats 8 bytes of the MTU, together with a WireGuard connection over 
IPv6, the default MTU is too high. The WireGuard MTU would need to 1412 and not
1420.

Some common MTUs in the field, although to be fair, we haven't seen DS-Lite + 
PPPoE, but in theory it is possible:

| Type            | MTU  | Connection | Works? | Max WireGuard MTU |
| --------------- | ---- | ---------- | ------ | ----------------- |
| Ethernet        | 1500 | IPv4       | Yes    | 1440              |
| Ethernet        | 1500 | IPv6       | Yes    | 1420              |
| PPPoE           | 1492 | IPv4       | Yes    | 1432              |
| PPPoE           | 1492 | IPv6       | No     | 1412              |
| DS-Lite         | 1460 | IPv4       | No     | 1400              |
| DS-Lite         | 1500 | IPv6       | Yes    | 1420              |
| DS-Lite + PPPoE | 1452 | IPv4       | No     | 1392              |
| DS-Lite + PPPoE | 1492 | IPv6       | No     | 1412              |

The "Connection" column indicates whether the VPN connection was established 
over IPv4 or IPv6.

The "Works?" column indicates whether the default WireGuard MTU of 1420 works 
with this type of connection. 

The "Max WireGuard MTU" column is the highest WireGuard MTU setting that still 
works without issues.

### Approaches

Now with this out of the way, we have (at least) two possible solutions:

1. Set the MTU of the WireGuard device to the lowest value you expect VPN 
   clients to need;
2. Keep the default WireGuard MTU, but use TCP MSS clamping to make sure at 
   least TCP connections work properly over the VPN.

So, if you want to keep things simple, just set the MTU to 1392 and call it a 
day, see below on how to do this.

The slightly more complicated approach, if setting the MTU is not desirable, or
you already have VPN clients in the field that can't easily update their 
configuration, would be to use TCP MSS Clamping. This will make (most) TCP 
connections work properly over the VPN, no matter the MTU of the WireGuard 
tunnel.

Now, the 
[easy](https://wiki.nftables.org/wiki-nftables/index.php/Mangling_packet_headers) 
approach with TCP MSS Clamping does not seem to work, i.e. the one that is 
based on PMTUD:

```
nft add rule ip filter forward tcp flags syn tcp option maxseg size set rt mtu
```

This is probably because PMTUD does not work (at all) over the WireGuard 
tunnel when the MTU is too high, i.e. `tracepath` will not show anything useful
at all, e.g.:

```bash
$ tracepath -4 -n 9.9.9.9
 1?: [LOCALHOST]                      pmtu 1420
 1:  no reply
 2:  no reply
 3:  no reply
```

What *does* work, is setting the size manually. Now, the difficult part is 
figuring out what this size should be. So far, the logic escapes me.

On my home network the MTU (over IPv4) is 1460 as DS-Lite is used. So, if we
establish a VPN connection over IPv4, the maximum MTU that would work for
WireGuard is 1460 - 60 = 1400. Setting this MTU for WireGuard works like a 
charm. 

To determine the MSS we have to consider a TCP connection over the VPN, 
which would be (for IPv4) 20+20 = 40 bytes. So the MSS should be "clamped" to 
1400 - 40 = 1360. For IPv6 the IP header is 40 bytes, so here we'd have 40+20 
bytes. The MSS should thus be clamped to 1340.

```
nft add rule ip filter forward tcp flags syn tcp option maxseg size set 1340
```

Unfortunately, this does not seem to work! If we set it to 1332 it works super 
fine, we lost somewhere 8 bytes, but where?!

### Setting the MTU

If you want to modify the MTU of WireGuard, you can do so in 
`/etc/vpn-user-portal/config.php`:

```php
'WireGuard' => [

    // ... other WireGuard options
    
    'useMtu' => 1392,
],
```

Here we set the MTU to 1392. Do not forget to 
[Apply Changes](PROFILE_CONFIG.md#apply-changes).

### Client Support for Setting the MTU

In the table below you can see the eduVPN / Let's Connect! client support for 
the `MTU =` configuration line in the WireGuard configuration.

| Platform | Supports `MTU =` |
| -------- | ---------------- |
| Windows  | Yes              |
| macOS    | Yes              |
| Android  | ?                |
| iOS      | Yes              |
| Linux    | Yes              |

### Open Issues

- Why is (or seems?) PMTUD completely broken over WireGuard when WireGuard's 
  MTU is too high for the connection?
- Why do we need to set the `maxseg size` to `1332` and not `1340`?
- Can we lower the WireGuard server's MTU without breaking clients that do not
  have an `MTU =` configuration line?
- Can we handle WireGuard over WireGuard setups? Does this even work when the 
  initial MTU is 1500? 
- Can we add TCP MSS clamping for the purpose of "transitioning" clients that
  do not yet have an `MTU =` line in their config? 

See [#151](https://todo.sr.ht/~eduvpn/server/151) for more information and
status.
