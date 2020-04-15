---
title: Public Addresses
description: Use Public IP Addresses for VPN Clients
---

By default, NAT is used and [RFC 1918](https://tools.ietf.org/html/rfc1918) 
addresses are assigned to the clients for IPv4 and 
[RFC 4193](https://tools.ietf.org/html/rfc4193) addresses for IPv6.

In case you want to use routable IPv4 and/or IPv6 addresses you need to 
modify the configuration and make sure your upstream router routes the 
appropriate range(s) to your VPN server's IP address(es).

First edit `/etc/vpn-server-api/config.php` and set the `range` and/or `range6` 
addresses as appropriate.

Next, modify the firewall according to 
[these](FIREWALL.md#public-ip-addresses-for-vpn-clients) instructions.

To apply the changes run the `apply_changes.sh` script from this repository 
on your VPN server.
