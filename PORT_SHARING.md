# Port Sharing

This document describes how to configure your VPN server in such a way as to
make it most likely people can connect to it. 

This is done by modifying the ports the OpenVPN processes listen on to 
`udp/443` and `tcp/443`.

In order to share `tcp/443` between the web server and OpenVPN we'll use 
[sslh](https://github.com/yrutschle/sslh).

This document is written for deployments on CentOS. But should also work on 
Fedora and Debian with minor modifications in the commands used.

## SELinux

First, we must allow OpenVPN to bind to the port `udp/443`. For this
to work we review the existing OpenVPN port configurations:

    $ sudo semanage port -l | grep openvpn_port_t
    openvpn_port_t                 tcp      1195-1263, 11940-12195, 1194
    openvpn_port_t                 udp      1195-1263, 1194

We can add `udp/443` easily to `openvpn_port_t`:

    $ sudo semanage port -a -t openvpn_port_t -p udp 443

As we'll use sslh to listen on `tcp/443` and forward to `tcp/1194`, the default
TCP port, we won't need to modify anything for `tcp/443`.

## VPN

We need to modify `/etc/vpn-server-api/default/config.php` and modify 
`vpnProtoPorts` to the following:

    'vpnProtoPorts' => [
        'udp/443',
        'tcp/1194',
    ],

Also start using `exposedVpnProtoPorts` to announce to VPN clients that we only
want to use `udp/443` and `tcp/443`, and no longer `tcp/1194`:

    'exposedVpnProtoPorts' => [
        'udp/443',
        'tcp/443'
    ],

Also modify the firewall in `/etc/vpn-server-node/firewall.php`. Under `tcp` 
you can remove `1194` and under `udp` you can add `443` and remove 
`1194`.

## Web Server

Modify `/etc/httpd/conf.d/ssl.conf` and modify `Listen 443 https` to 
`Listen 8443 https`.

In `/etc/httpd/conf.d/vpn.example.conf`, where `vpn.example` is your actual 
VPN hostname, you modify `<VirtualHost *:443>` to `<VirtualHost *:8443>`.

## Proxy

Install sslh:

    $ sudo yum -y install sslh

Configure sslh, we use the following configuration file in `/etc/sslh.cfg`:

    verbose: false;
    foreground: true;
    inetd: false;
    numeric: false;
    transparent: false;
    timeout: 5;
    user: "sslh";
    listen:
    (
        { host: "::"; port: "443"; }
    );
    protocols:
    (
         { name: "openvpn"; host: "localhost"; port: "1194"; },
         { name: "ssl"; host: "localhost"; port: "8443"; log_level: 0; }
    );

## Applying

### Web and Proxy

    $ sudo systemctl restart httpd
    $ sudo systemctl enable --now sslh

### OpenVPN 

    $ sudo vpn-server-node-server-config
    $ sudo systemctl restart "openvpn-server@*"

### Firewall

    $ sudo vpn-server-node-generate-firewall --install
    $ sudo systemctl restart iptables
    $ sudo systemctl restart ip6tables
