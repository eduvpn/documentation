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

**NOTE**: the analysis below might be incomplete, or incorrect at points, it is
a very complex topic! Suggestions for improvements and corrections are very 
welcome!

We noticed some VPN *client* connection issues in the field when PPPoE and/or 
DS-Lite is used. This manifests itself as connections hanging (indefinitely) 
when trying to browse the web, start an SSH session, or try to open your IMAP
mailbox. For once it is _not_ DNS, but MTUs!

This problem appears most prevalent on Linux. It is unclear why Windows and 
macOS do not suffer, or suffer less, from connection hangs. We suspect it is 
because they implemented some mitigation for Path MTU Discovery (PMTUD) 
[issues](https://en.wikipedia.org/wiki/Path_MTU_Discovery#Problems), e.g. they
may have implemented [RFC 4821](https://www.rfc-editor.org/rfc/rfc4821).

There is an easy mitigation you can [apply](#mitigation-on-linux-client) on
a Linux VPN client as well that solves the most immediate problem. The rest of 
this section will explain how it can be fixed in a, what we hope, more 
sustainable way.

### When?

We observed that connection hanging occurs reliably when the following holds:

1. The network connection of the VPN client has MTU of 1500;
2. Somewhere on the path, to the VPN server, the MTU is reduced;
3. The MTU becomes low enough to not fit a WireGuard packet anymore.

The following table shows when there will be issues expected with the default 
WireGuard MTU (which will be 1420 when the network connection has an MTU of 
1500):

| Type            | PMTU | Connection | Works? | Max WireGuard MTU |
| --------------- | ---- | ---------- | ------ | ----------------- |
| Ethernet        | 1500 | IPv4       | Yes    | 1440              |
|                 | 1500 | IPv6       | Yes    | 1420              |
| PPPoE           | 1492 | IPv4       | Yes    | 1432              |
|                 | 1492 | IPv6       | No     | 1412              |
| DS-Lite         | 1460 | IPv4       | No     | 1400              |
|                 | 1500 | IPv6       | Yes    | 1420              |
| DS-Lite + PPPoE | 1452 | IPv4       | No     | 1392              |
|                 | 1492 | IPv6       | No     | 1412              |

* The "PMTU" column indicates the maximum MTU on the path between VPN client 
  and server;
* The "Connection" column indicates whether the VPN connection was established 
  over IPv4 or IPv6;
* The "Works?" column indicates whether the default WireGuard MTU of 1420 works 
  with this type of connection;
* The "Max WireGuard MTU" column is the highest WireGuard MTU setting that 
  still works without expecting MTU issues.

### Determine PMTU

If you have access to a VPN client that shows issues when connecting to 
WireGuard you can test the Path MTU (PMTU) using `tracepath`. For example the 
PMTU without VPN connection could be like this:

```bash
$ tracepath -4 -n dns.quad9.net
 1?: [LOCALHOST]                      pmtu 1500
 1:  192.168.178.1                                         1.272ms 
 1:  192.168.178.1                                         2.525ms 
 2:  192.0.0.2                                             2.580ms pmtu 1460

...

 7:  9.9.9.9                                              26.348ms !H
     Resume: pmtu 1460 
```

Note, that for IPv6 the PMTU does not need to be the same:

```bash
$ tracepath -6 -n dns.quad9.net
 1?: [LOCALHOST]                        0.010ms pmtu 1500

...

 8:  2620:fe::9                                           12.946ms !A
     Resume: pmtu 1500 
```

Here we see the PMTU for IPv4 is 1460, and for IPv6 1500. If the VPN client 
would always connect over IPv6, there would not be a problem, but unfortunately 
that can't always be guaranteed. This connection uses DS-Lite to wrap IPv4 in 
IPv6 packets. This has a 40 byte overhead, and thus reduces the effective MTU 
to 1460.

In the table above we see that WireGuard's MTU can be 1400 at most in the 
scenario where the VPN connection is established over IPv4, which is not 
enough to fit WireGuard's default MTU of 1420.

### Setting the MTU

**NOTE**: setting the MTU only works in vpn-user-portal >= 3.3.7.

**NOTE**: this is **EXPERIMENTAL**, we MAY decide to make this the default at
some point and remove (or rename) the configuration toggle! Please provide 
feedback if you have ideas about this.

Based on the table above, we can set the MTU to the maximum value that still is 
expected to work on the networks used by the VPN clients. If you don't know 
what to choose, take 1392.

You can set the option `setMtu` like this in `/etc/vpn-user-portal/config.php`:

```php
'WireGuard' => [

    // ... other WireGuard options
    
    'setMtu' => 1392,
],
```

The MTU configuration flag will be used by both on the server and the client. 

If the client is still using a configuration file with MTU configuration, the 
firewall's "TCP MSS Clamping" will take care of making that client work.

Once you set the `setMtu` option, the changes need to be applied:

```bash
$ sudo vpn-maint-apply-changes
```

By default the firewall that is installed when you deployed your VPN server is
already configured to enable TCP MSS Clamping, so nothing needs to be done 
here.

### Mitigation on Linux Client

If a server solution is currently not possible, one can also create a file 
_on_ the VPN client, e.g. `/etc/sysctl.d/70-vpn-mtu.conf`, should work on 
at least Debian / Ubuntu and Fedora / EL:

```
net.ipv4.tcp_mtu_probing = 1
net.ipv4.tcp_base_mss = 1024
```

Then run the below command and reconnect to the (WireGuard) VPN:

```bash
$ sudo sysctl --system
```

### References

We found the following resources very useful for understanding MTU, TCP MSS 
Clamping and PMTUD.

* [Header / MTU sizes for Wireguard](https://lists.zx2c4.com/pipermail/wireguard/2017-December/002201.html)
* [What is MTU?](https://www.cloudflare.com/learning/network-layer/what-is-mtu/)
* [Path MTU discovery in practice](https://blog.cloudflare.com/path-mtu-discovery-in-practice/)
* [What is MSS (maximum segment size)?](https://www.cloudflare.com/learning/network-layer/what-is-mss/)
