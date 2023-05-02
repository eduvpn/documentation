# IPv6

The VPN server software supports both IPv4 and IPv6. We've reached a point 
in the "evolution" of the Internet that IPv4 NAT is unavoidable, but for IPv6
there is no excuse to not issue proper public IPv6 addresses to the VPN 
clients.

By default the VPN server installation will *also* perform NAT for IPv6 
traffic and set some less than optimal configuration parameters. This is only 
meant for *testing*. For production you SHOULD switch to public IPv6 addresses 
for your VPN clients!

As already mentioned in other places in the documentation, your VPN server 
MUST have static IPv4 and IPv6 address configurations!

## IPv6 Routing

IPv6 routing can be, and is, by default enabled in `/etc/sysctl.d/70-vpn.conf` 
where `eth0` is the external interface of your VPN server:

```
# **ONLY** needed for IPv6 configuration through auto configuration. Do **NOT**
# use this in production, you SHOULD be using STATIC addresses!
net.ipv6.conf.eth0.accept_ra = 2

# enable IPv4 and IPv6 forwarding
net.ipv4.ip_forward = 1
net.ipv6.conf.all.forwarding = 1
```

For production you MUST remove the `net.ipv6.conf.eth0.accept_ra = 2` line as 
you'll be using static IPv6 addresses and thus not need this, so the only 
contents SHOULD be:

```
net.ipv4.ip_forward = 1
net.ipv6.conf.all.forwarding = 1
```

When making changes here, reboot your server to make sure the changes are
properly propagated. Test your IPv6 connectivity after reboot.

**NOTE**: do NOT remove the `net.ipv6.conf.all.forwarding = 1` in an attempt
to try and disable IPv6. This will lead to (long) timeouts when clients attempt
to connect to services that support native IPv6.

## Routed IPv6 Prefix

The easiest, and best way is to have a public IPv6 prefix routed to the public
IPv6 address of your VPN server. 

See [Public Addresses](PUBLIC_ADDR.md) on how to configure public IPv6 
addresses in your VPN server as well as the 
[firewall](FIREWALL.md#public-ip-addresses-for-vpn-clients) configuration when 
using public IP addresses.

## Disabling IPv6

If you want to disable IPv6, because your VPN server does not have an IPv6 
connection, you can do so as documented 
[here](FIREWALL.md#reject-ipv6-client-traffic). Technically this does not 
disable IPv6, but drop the IPv6 packets as soon as possible as to not result in
any delays when attempting to services that have native IPv6 support.

IPv6 can currently NOT be fully disabled in the VPN service!
