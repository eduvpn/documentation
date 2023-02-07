# VPN Client Compatibility

This document contains a list VPN clients that can be used to connect to the 
VPN service.

## Offical Applications

Official applications are available on most platforms. These are optimized for
working with the VPN software. The official applications are made available 
with two brand names:

* [eduVPN](https://eduvpn.org/): if you are part of the 
  research and education community and your institution is running the eduVPN 
  service;
* [Let's Connect!](https://letsconnect-vpn.org/) everyone else outside this 
  community, or when you run your own server, or someone else runs it for you.

The eduVPN applications only allow you to choose your organization from a 
curated list. The Let's Connect! applications allow you to specify a domain of
the VPN server to connect to.

The benefit of the official applications is that they will make it much easier 
for the end user to configure the VPN, and will make sure the VPN keeps 
working in case configuration updates are required for connecting to the VPN. 
The other applications may require manual configuration downloads through the 
user portal to be able to keep using the VPN.

A full list of official applications is available, including their changelogs: 

* [eduVPN](https://app.eduvpn.org/)
* [Let's Connect!](https://app.letsconnect-vpn.org/)

## Other Applications

In addition to the official applications, you can also use any 
[OpenVPN](https://openvpn.net/) or 
[WireGuard](https://www.wireguard.com/) compatible client on the platform of 
your choice.

You need to know the URL of your organization's server to be able to visit the
"portal" to download an OpenVPN or WireGuard configuration file that you can
then important in your VPN client.

In case you are using eduVPN, you can find your organization in 
[this](https://status.eduvpn.org/) list. It will link to the server URL where
you need to authenticate before being able to download a configuration file.
