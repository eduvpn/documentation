# Port Sharing

This document describes how to configure your VPN server in such a way as to
make it most likely people can connect to it. This is done by making it 
possible to connect to the VPN service using `tcp/443` in addition to 
`udp/1194` and `tcp/1194`. Because the web server claims `tcp/443` we need to 
share `tcp/443` between the web server and OpenVPN we'll use 
[sslh](https://github.com/yrutschle/sslh).

In larger deployments you'll want to use multiple machines where the portal(s) 
and API run on a different machine from the OpenVPN backend server(s) so port
sharing is not needed, i.e. OpenVPN can claim `tcp/443` directly.

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

## Applying

### CentOS/Fedora

    $ sudo systemctl restart httpd
    $ sudo systemctl enable --now sslh

### Debian

    $ sudo systemctl restart apache2
    $ sudo systemctl restart sslh
