# Introduction

This folder describes the specific documentation for `eduvpn.surfcloud.nl`.

# SAML

Following the generic SAML instructions works for this instance as SURFconext
is used as IdP.

# VPN Configuration

There are both public IPv4 and IPv6 addresses available:

- `195.169.120.0/23`
- `2001:610:450::/48`

These are configured in `/etc/openvpn/server.conf`:

    server 195.169.120.0 255.255.254.0
    server-ipv6 2001:610:450:4242::/64

The DNS servers are configured like this:

    push "dhcp-option DNS 195.169.124.124"
    push "dhcp-option DNS 192.87.36.36"
    push "dhcp-option DNS 2001:610:3:200a:192:87:36:36"
    push "dhcp-option DNS 2001:610:0:800b:195:169:124:124"

The IPv6 DNS addresses are not picked up by all OpenVPN clients, it seems 
[Viscosity](https://www.sparklabs.com/viscosity/) on Windows picks this up, 
but not OpenVPN on Windows. Other clients are untested as of now.

Currently, only one OpenVPN instance, listening on `udp/1194`, is available.

# User Portal

The User Portal has "eduVPN" branding, which includes a logo in the top right.

## Templates

Install the templates:

    $ sudo mkdir -p /etc/vpn-user-portal/views
    $ sudo cp *.twig /etc/vpn-user-portal/views

## CSS

Install the CSS files:

    $ sudo mkdir -p /var/www/html/css
    $ sudo cp *.css /var/www/html/css

## Images

Instal the images:

    $ sudo mkdir -p /var/www/html/img
    $ sudo cp *.png /var/www/html/img
