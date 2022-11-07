This document describes how to add the Let's Connect! or eduVPN branding to 
your server installation. By default a simple "plain" branding is used.

# Installation

## Fedora / Enterprise Linux

    $ sudo dnf -y install vpn-portal-artwork-LC
    $ sudo dnf -y install vpn-portal-artwork-eduVPN

## Debian / Ubuntu

    $ sudo apt -y install vpn-portal-artwork-lc
    $ sudo apt -y install vpn-portal-artwork-eduvpn

# Configuration

Now you can enable the `styleName` in `/etc/vpn-user-portal/config.php`. Set it 
to `LC` (or `eduVPN`).
