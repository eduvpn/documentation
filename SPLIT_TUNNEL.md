# Split Tunnel

Configuring "split tunnel", i.e. only routing _certain_ traffic over the VPN 
can be configured. It consists of three parts, although some may not be 
required for your particular setup:

1. Configuring the "routes" to the client to inform them which IP ranges need 
   to be routed over the VPN and make sure the VPN is not used as a "default 
   gateway";
2. Configure and (internal) DNS server to be used by the clients that possibly
   resolves "local" names only;
3. Restrict other traffic from being sent over the VPN to other locations than
   the pushed routes, the clients should not be able to override the "route" 
   configuration, e.g. by forcing "default gateway".

**NOTE**: if there are no internal-only DNS entries to resolve, you SHOULD NOT 
push DNS servers to the client. If there are, then make sure to also specify 
`dnsSearchDomainList`. In addition, make sure the IP address(es) of the DNS 
server(s) are also included in the `routeList`.

# Example

We have an organization `example.local` that has two IP ranges, `10.42.42.0/24` 
and `10.43.43.0/24` that clients need access to from home. The internal DNS 
server, on `10.1.1.1/32` is responsible for resolving the `example.local` 
domain for internal servers. Only traffic to these IP ranges and the DNS server
should be allowed from the VPN server.

# Profile Configuration

Configure an `office` profile in `/etc/vpn-user-portal/config.php`, e.g.:

```
'ProfileList' => [
    [
        'profileId' => 'office',
        'displayName' => 'Office',
       // issued to VPN clients
        'oRangeFour' => '10.0.0.0/24',
        'oRangeSix' => 'fd00::/64',
        // hostname VPN clients will connect to
        'hostName' => 'office.example.org',

        ...
        ...

        // push the routes to the client, *including* the DNS IP
        'routeList' => ['10.42.42.0/24', '10.43.43.0/24', '10.1.1.1/32'],

        // push the local DNS to the clients as well
        'dnsServerList' => ['10.1.1.1'],
        
        // Connection-specific DNS Suffix Search List
        'dnsSearchDomainList' => ['example.local', 'foo.example.local', 'bar.example.local'],
    ],
],
```

Take special note of the `routeList`, `dnsServerList` and `dnsSearchDomainList` 
options. See [Profile Config](PROFILE_CONFIG.md) for other configuration 
options that may be relevant for your situation.

To apply the configuration changes:

```
$ sudo vpn-maint-apply-changes
```

# Firewall Configuration

Restricting network access for VPN clients is already documented in 
[FIREWALL.md](FIREWALL.md#reject-forwarding-traffic), but just to be complete,
the (FORWARD) configuration of the firewall would be like this, assuming `eth0` 
is the interface connecting to your local network from your VPN server:

```
-A FORWARD -i tun+ -o eth0 -d 10.42.42.0/24 -j ACCEPT
-A FORWARD -i tun+ -o eth0 -d 10.43.43.0/24 -j ACCEPT
-A FORWARD -i tun+ -o eth0 -d 10.1.1.1/32 -j ACCEPT
-A FORWARD -i eth0 -o tun+ -j ACCEPT
-A FORWARD -j REJECT --reject-with icmp-host-prohibited
```

**NOTE**: restart the firewall after making modifications!

**NOTE**: for IPv6 routes it works exactly the same.
