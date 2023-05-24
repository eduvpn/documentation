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
    // we prefer to listen on UDP/443 as it is more likely these days that
    // firewalls do not block it because of HTTP/3 (QUIC) (default = 51820)
    'listenPort' => 443,
],

// we do not allow users to download VPN configuration files themselves through
// the portal (default = 3)
'maxActiveConfigurations' => 0,

'Api' => [
    // we allow users to connect with 2 VPN clients simultaneously 
    // (default = 3)
    'maxActiveConfigurations' => 2,
    
    // we consider a VPN client "gone" after 96 hours surviving also long 
    // weekends (default = 72 hours)
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

The tooling for [monitoring](MONITORING.md) and optionally out 
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
