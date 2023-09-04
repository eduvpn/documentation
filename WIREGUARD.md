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

We noticed some *VPN client* issues in the field when PPPoE and/or DS-Lite is 
used by ISPs. This manifests itself as connections _hanging_ (indefinitely). 
For example, connecting to the VPN goes fine, using `ping` works and perhaps
visiting some (small) web sites also functions. However, starting an SSH 
session, visiting a "big" web page, or perhaps accessing mail through IMAP does 
not.

We noticed this problem mostly on Linux VPN clients. We suspect that the reason 
for this is that 
[Packetization Layer Path MTU Discovery](https://www.rfc-editor.org/rfc/rfc4821) 
is implemented, but not activated by default. We assume it _is_ on macOS and 
Windows, and thus mitigates these MTU issues, but we can not find any source 
confirming or denying that. 

Even though there _is_ a mitigation one can 
[enable](#mitigation-on-linux-client) on Linux, it is probably better to fix 
this on the server for all clients at once.

### Background

If the (Path) MTU of the VPN connection between client and server is 1500, 
there is no issue, whether the connection is done over IPv4 or IPv6. The 
default MTU of WireGuard, which is 
[1420](https://lists.zx2c4.com/pipermail/wireguard/2017-December/002201.html) 
fits perfectly fine. The WireGuard packet overhead is 80 bytes when connecting 
over IPv6 and 60 bytes when connecting over IPv4. So, if PPPoE is used, which 
"eats" 8 bytes of the MTU, together with a WireGuard connection over IPv6, the 
default MTU is too high. The WireGuard MTU would need to 1412 and not 1420.

Some common MTUs in the field:

| Type            | MTU  | Connection | Works? | Max WireGuard MTU |
| --------------- | ---- | ---------- | ------ | ----------------- |
| Ethernet        | 1500 | IPv4       | Yes    | 1440              |
|                 | 1500 | IPv6       | Yes    | 1420              |
| PPPoE           | 1492 | IPv4       | Yes    | 1432              |
|                 | 1492 | IPv6       | No     | 1412              |
| DS-Lite         | 1460 | IPv4       | No     | 1400              |
|                 | 1500 | IPv6       | Yes    | 1420              |
| DS-Lite + PPPoE | 1452 | IPv4       | No     | 1392              |
|                 | 1492 | IPv6       | No     | 1412              |

The "Connection" column indicates whether the VPN connection was established 
over IPv4 or IPv6.

The "Works?" column indicates whether the default WireGuard MTU of 1420 works 
with this type of connection. 

The "Max WireGuard MTU" column is the highest WireGuard MTU setting that still 
works without expecting MTU issues.

### Setting the MTU

**NOTE**: setting the MTU only works in vpn-user-portal >= 3.3.7.

Based on the table above, we can simply set the MTU to the maximum value that 
still is expected to work on the networks used by the VPN clients. To be safe,
that value should probably be `1392`.

The best approach is to set the MTU both in the client and server. We created
an option for this you can add to `/etc/vpn-user-portal/config.php`:

```php
'WireGuard' => [

    // ... other WireGuard options
    
    'setMtu' => 1392,
],
```

For new VPN client configuration downloads, the MTU will be used, as well as 
for the eduVPN / Let's Connect! clients once it reconnects to the VPN server.

For VPN client configurations "in the field" that do not yet set their MTU, we 
can use TCP MSS Clamping. This has already been enabled (by default) in the 
firewall of the VPN servers, so that should work transparently.

**TODO**: point to firewall docs on how to set this for iptables and nftables.

### Mitigation on Linux Client

You can create a file _on_ the VPN client, e.g. 
`/etc/sysctl.d/70-vpn-mtu.conf`:

```
net.ipv4.tcp_mtu_probing = 1
net.ipv4.tcp_base_mss = 1024
```

Then run the below command and reconnect to the (WireGuard) VPN:

```bash
$ sudo sysctl --system
```

### Resources

We found the following resources very useful for understanding MTU, TCP MSS 
Clamping and PMTUD.

* [What is MTU?](https://www.cloudflare.com/learning/network-layer/what-is-mtu/)
* [Path MTU discovery in practice](https://blog.cloudflare.com/path-mtu-discovery-in-practice/)
* [What is MSS (maximum segment size)?](https://www.cloudflare.com/learning/network-layer/what-is-mss/)
