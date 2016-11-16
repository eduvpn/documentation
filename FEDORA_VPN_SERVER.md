# VPN on Fedora

This document describes how to install a VPN server on Fedora >= 24. This is a 
very simple configuration for a couple of users, not for big deployments. We 
will assume you will run on `vpn.example.org`, change this to your host name.

## Install

    $ sudo dnf -y copr enable fkooman/eduvpn-dev
    $ sudo dnf -y install vpn-server-api vpn-ca-api vpn-server-node \
        vpn-user-portal vpn-admin-portal php iptables-services

## Configuration

### Sysctl

Add the following to `/etc/sysctl.conf` to allow IPv4 and IPv6 forwarding:

    net.ipv4.ip_forward = 1
    net.ipv6.conf.all.forwarding = 1

If IPv6 is configured on your host, and uses router advertisements (RA), you
also need to add this:

    net.ipv6.conf.eth0.accept_ra = 2

Where `eth0` is your network interface connecting to the Internet.

Activate the changes:

    $ sudo sysctl --system

### SELinux

Apache needs to connect to OpenVPN using a socket, so we need to allow that 
here.

    $ sudo setsebool -P httpd_can_network_connect=1

Allow the OpenVPN process to listen on its management port, `tcp/11940`:

    $ sudo semanage port -a -t openvpn_port_t -p tcp 11940

### Apache

If you want to accept connections to the user and admin portal from everywhere 
and not just `localhost`, modify `/etc/httpd/conf.d/vpn-user-portal.conf` and
`/etc/httpd/conf.d/vpn-admin-portal.conf` and enable `Require all granted`.

Enable Apache on boot, but do not yet start it:

    $ sudo systemctl enable httpd

### PHP

Modify `/etc/php.ini` and set `date.timezone` to e.g. `UTC` or `Europe/Berlin`
depending on your system.

### CA 

Initialize the certificate authority (CA):

    $ sudo -u apache vpn-ca-api-init --instance default

### Server

Modify `/etc/vpn-server-api/default/config.yaml` and set `hostName` to your 
server's host name, here `vpn.example.org`.

You can also modify other options there to suit your requirements.

### User Portal

Add a user:

    $ sudo vpn-user-portal-add-user --instance default --user foo --pass bar

### Admin Portal

Add a user:

    $ sudo vpn-admin-portal-add-user --instance default --user foo --pass bar

### OpenVPN Config

Before we can generate an OpenVPN configuration, we need to start Apache to 
make the API available:

    $ sudo systemctl start httpd

Generate a configuration, including certificates:

    $ sudo vpn-server-node-server-config --instance default --profile internet --generate --cn vpn01.example.org

Enable OpenVPN on boot, and start it:

    $ sudo systemctl enable openvpn@server-default-internet-0
    $ sudo systemctl start openvpn@server-default-internet-0

### Firewall

Modify `/etc/vpn-server-node/firewall.yaml` if you want.

Generate the firewall:

    $ sudo vpn-server-node-generate-firewall --install

Enable and start the firewall:

    $ sudo systemctl enable iptables
    $ sudo systemctl enable ip6tables
    $ sudo systemctl restart iptables
    $ sudo systemctl restart ip6tables

## Using

The user and admin portals should now be available at 
`http://vpn.example.org/vpn-user-portal` and 
`http://vpn.example.org/vpn-admin-portal`.

In the user portal you can create a VPN client configuration and download it. 
You can easily import it in NetworkManager. The OpenVPN configuration file is
fully supported in NetworkManager on Fedora >= 24. It also works on Android, 
iOS, macOS and Windows.

## Security

### TLS

After getting things to work, you SHOULD configure TLS, make sure DNS is 
working properly first.

    $ sudo dnf -y install mod_ssl certbot

Currently, certbot can only obtain a certificate for you, not automatically 
configure it. 

    $ sudo systemctl stop httpd
    $ sudo certbot certonly

Follow the certbot instructions. After obtaining the certificate, copy the
files in the correct location:

    $ sudo cp /etc/letsencrypt/live/vpn.example.org/cert.pem /etc/pki/tls/certs/vpn.example.org.crt
    $ sudo cp /etc/letsencrypt/live/vpn.example.org/chain.pem /etc/pki/tls/certs/vpn.example.org-chain.crt
    $ sudo cp /etc/letsencrypt/live/vpn.example.org/privkey.pem /etc/pki/tls/private/vpn.example.org.key

Open `/etc/httpd/conf.d/ssl.conf` and modify these lines:

    SSLCertificateFile /etc/pki/tls/certs/vpn.example.org.crt
    SSLCertificateKeyFile /etc/pki/tls/private/vpn.example.org.key
    SSLCertificateChainFile /etc/pki/tls/certs/vpn.example.org-chain.crt

Restart Apache:

    $ sudo systemctl start httpd

Make sure you test your configuration by doing a 
[SSL Server Test](https://www.ssllabs.com/ssltest/) and updating the 
configuration in `ssl.conf` as required. A good resource is the 
[Mozilla SSL Configuration Generator](https://mozilla.github.io/server-side-tls/ssl-config-generator/) 
to further tighten the security.

### Secure Cookies

In order to force cookies to be only sent over HTTPS, you need to modify the 
files `/etc/vpn-user-portal/default/config.yaml` and 
`/etc/vpn-admin-portal/default/config.yaml` and set the `secureCookie` option
to `true`.

## Advanced

### Port Share

By default, OpenVPN will only listen on `udp/1194`, the default port of 
OpenVPN. In order to avoid most firewalls it makes sense to also listen on 
`tcp/443`, the HTTPS port. Because Apache is already listening there, we need
a way to share the port between Apache and OpenVPN.

First, we create an additional OpenVPN process. Modify 
`/etc/vpn-server-api/default/config.yaml` and change `processCount` from `1` to 
`2`.

We need an additional management port that OpenVPN can use:

    $ sudo semanage port -a -t openvpn_port_t -p tcp 11941

Regenerate the server configuration, and enable it:

    $ sudo vpn-server-node-server-config --instance default --profile internet
    $ sudo systemctl enable openvpn@server-default-internet-1
    $ sudo systemctl start openvpn@server-default-internet-1

Install SNI Proxy:

    $ sudo dnf -y install sniproxy

Modify `/etc/httpd/conf.d/ssl.conf` and change the following:

| Before | After |
| ------ | ----- |
| `Listen 443 https`                | `Listen 8443 https` |
| `<VirtualHost _default_:443>`     | `<VirtualHost _default_:8443>` |
| `#ServerName www.example.com:443` | `ServerName https://vpn.example.org:443` |

Then, restart Apache:
    
    $ sudo systemctl restart httpd

Add the following snippet to `/etc/sniproxy.conf`:

    listen 443 {
        proto tls
        fallback localhost:1194
        table https_hosts
    }

    table https_hosts {
        vpn.example.org localhost:8443
    }

Start and enable SNI Proxy:

    $ sudo systemctl enable sniproxy
    $ sudo systemctl start sniproxy

That's it!
