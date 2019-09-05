---
title: Use Common Ports
description: Use common ports for your VPN server that enable its use in many restricted networks
---

This document describes how to configure your VPN server in such a way as to
make it most likely people can connect to it. This is done by making it 
possible to connect to the VPN service using both `udp/443` and `tcp/443`. A
complication here is that the web server claims `tcp/443`, so we need to share 
`tcp/443` between the web server and OpenVPN. We'll use 
[sslh](https://github.com/yrutschle/sslh) for this task.

In larger deployments you'll want to use multiple machines where the portal(s) 
and API run on a different machine from the OpenVPN backend server(s) so port
sharing is not needed, i.e. OpenVPN can claim `tcp/443` directly.

## VPN

We need to modify `/etc/vpn-server-api/config.php` and modify 
`vpnProtoPorts` and set `exposedVpnProtoPorts` to announce to VPN clients that 
we want them to use `udp/443` and `tcp/443` and not any of the normal OpenVPN 
ports:

    'vpnProtoPorts' => [
        'udp/443',
        'tcp/1194',
    ],

    ...

    'exposedVpnProtoPorts' => [
        'udp/443',
        'tcp/443',
    ],

In `vpnProtoPorts` we make OpenVPN listen on `tcp/1194` and NOT on `tcp/443` 
as the sslh will listen there later and forward connections to `tcp/443` to 
this port internally.

## Web Server

### CentOS / Fedora

Modify `/etc/httpd/conf.d/ssl.conf` and modify `Listen 443 https` to 
`Listen 8443 https`.

In `/etc/httpd/conf.d/vpn.example.conf`, where `vpn.example` is your actual 
VPN hostname, you modify `<VirtualHost *:443>` to `<VirtualHost *:8443>`.

### Debian

Modify `/etc/apache2/ports.conf` and change the `Listen` lines to `Listen 8443` 
from `Listen 443`.

In `/etc/apache2/sites-available/vpn.example.conf`, where `vpn.example` is your 
actual VPN hostname, you modify `<VirtualHost *:443>` to 
`<VirtualHost *:8443>`.

## Proxy

### CentOS/Fedora

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
        { host: "0.0.0.0"; port: "443"; },
        { host: "::"; port: "443"; }
    );
    protocols:
    (
         { name: "openvpn"; host: "localhost"; port: "1194"; },
         { name: "ssl"; host: "localhost"; port: "8443"; log_level: 0; }
    );

### Debian

Install sslh:

    $ sudo apt -y install sslh

Modify `/etc/default/sslh`. Set `RUN=no` to `RUN=yes` and change `DAEMON_OPTS`:

    DAEMON_OPTS="--user sslh --listen [::]:443 --ssl 127.0.0.1:8443 --openvpn 127.0.0.1:1194 --pidfile /var/run/sslh/sslh.pid"

## Let's Encrypt

TODO: this is only for CentOS/Fedora and not for Debian...

If you are using Let's Encrypt with automatic certificate renewal you should 
modify your `/etc/sysconfig/certbot` and set the `PRE_HOOK` and `POST_HOOK` to 
stop/start `sslh` instead of `httpd`:

```
PRE_HOOK="--pre-hook 'systemctl stop sslh'"
POST_HOOK="--post-hook 'systemctl start sslh'"
```

## SELinux

On CentOS/Fedora you need to modify SELinux to allow OpenVPN to listen on 
`udp/443`:

    $ sudo semanage port -a -t openvpn_port_t -p udp 443

## Firewall

By default the firewall only allows connections to `udp/1194` and `tcp/1194` 
for OpenVPN, we need to modify this in `/etc/vpn-server-node/firewall.php`:

The `inputRules` section should look something like this:

    'inputRules' => [
        [
            'proto' => ['tcp'],
            'dst_port' => [
                22,     // SSH
                80,     // HTTP
                443,    // HTTPS / OPENVPN
            ],
        ],
        [
            'proto' => ['udp'],
            'dst_port' => [
                443,    // OPENVPN
            ],
        ],
    ],

## Applying

### CentOS/Fedora

    $ sudo systemctl restart httpd
    $ sudo systemctl enable --now sslh
    $ sudo vpn-server-node-server-config
    $ sudo vpn-server-node-generate-firewall --install
    $ sudo systemctl restart "openvpn-server@*"
    $ sudo systemctl restart iptables
    $ sudo systemctl restart ip6tables
    
### Debian

    $ sudo systemctl restart apache2
    $ sudo systemctl restart sslh
    $ sudo vpn-server-node-server-config
    $ sudo vpn-server-node-generate-firewall --install
    $ sudo systemctl restart "openvpn-server@*"
    $ sudo systemctl restart netfilter-persistent
