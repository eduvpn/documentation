# Port Sharing

This document describes how to configure your VPN server in such a way as to
make it most likely people can connect to it. 

This is done by making it possible to connect to the VPN service using 
`tcp/443` in addition to `udp/1194` and `tcp/1194`. 

Because the web server claims `tcp/443` we need to share `tcp/443` between the 
web server and OpenVPN we'll use [sslh](https://github.com/yrutschle/sslh).

This document is written for deployments on CentOS. But should also work on 
Fedora and Debian with minor modifications in the commands used.

## VPN

We need to modify `/etc/vpn-server-api/default/config.php` and modify 
`exposedVpnProtoPorts` to announce to VPN clients that we also want to 
advertise `tcp/443` to clients:

    'exposedVpnProtoPorts' => [
        'udp/1194',
        'tcp/1194',
        'tcp/443',
    ],

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
