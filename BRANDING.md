This document describes how to add the Let's Connect! or eduVPN branding to 
your server installation. By default a simple "plain" branding is used.

# Installation

## CentOS 

    $ sudo yum -y install vpn-portal-artwork-LC
    $ sudo yum -y install vpn-portal-artwork-eduVPN

## Fedora

    $ sudo dnf -y install vpn-portal-artwork-LC
    $ sudo dnf -y install vpn-portal-artwork-eduVPN

## Debian

    $ sudo apt-get -y install vpn-portal-artwork-lc
    $ sudo apt-get -y install vpn-portal-artwork-eduvpn

# Configuration

Now you can enable the `styleName` in `/etc/vpn-user-portal/config.php`. Set it 
to `LC` (or `eduVPN`).

You can also configure the color of the bar graphs on the "Stats" page.

    'statsConfig' => [
        'barColor' => [0x11, 0x93, 0xf5], // Let's Connect Blue
        //'barColor' => [0xdf, 0x7f, 0x0c], // eduVPN orange
    ],
