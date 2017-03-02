# Fedora VPN Server

This document describes how to install a VPN server on Fedora >= 25. 

We will assume you will run on `vpn.example.org`, change this to your host 
name.

Make sure you have all updates installed, and rebooted the machine before 
continuing: 

    $ sudo dnf -y --refresh update

# Installation

Enable the VPN repository:

    $ sudo dnf -y copr enable fkooman/eduvpn-testing

Remove firewalld, we do not support it:

    $ sudo dnf -y remove firewalld

Install the required packages:

    $ sudo dnf -y install \
        vpn-server-api vpn-server-node vpn-user-portal vpn-admin-portal \
        httpd php iptables iptables-services

# Configuration

## sysctl

Add the following to `/etc/sysctl.conf` to allow IPv4 and IPv6 forwarding:

    net.ipv4.ip_forward = 1
    net.ipv6.conf.all.forwarding = 1

If IPv6 is configured on your host, and uses router advertisements (RA), you
also need to add this:

    net.ipv6.conf.eth0.accept_ra = 2

Where `eth0` is your network interface connecting to the Internet.

Activate the changes:

    $ sudo sysctl --system

## SELinux

Apache needs to connect to OpenVPN using a socket, so we need to allow that 
here.

    $ sudo setsebool -P httpd_can_network_connect=1

Allow the OpenVPN process to listen on its management port, `tcp/11940`:

    $ sudo semanage port -a -t openvpn_port_t -p tcp 11940

## Apache

If you want to accept connections to the user and admin portal from everywhere 
and not just `localhost`, modify `/etc/httpd/conf.d/vpn-user-portal.conf` and
`/etc/httpd/conf.d/vpn-admin-portal.conf` and remove the `#` in front of 
`Require all granted` and add one in front of `Require local`.

Enable Apache on boot, but do not yet start it:

    $ sudo systemctl enable httpd

## PHP

Modify `/etc/php.ini` and set `date.timezone` to e.g. `UTC` or `Europe/Berlin`
depending on your system.

## Server

Modify `/etc/vpn-server-api/default/config.php` and set `hostName` to the 
host name you want your VPN clients to connect to. It is a good idea to add
the profile identifier to the host name to make it easier to support multiple 
nodes in the future. So, in this case we would set the `hostName` field to 
`internet.vpn.example.org`.

You can also modify other options there to suit your requirements.

Initialize the certificate authority (CA):

    $ sudo -u apache vpn-server-api-init

## User Portal

Generate and configure an OAuth keyPair in 
`/etc/vpn-user-portal/default/config.php`:

    $ sudo vpn-user-portal-init

Add a user:

    $ sudo vpn-user-portal-add-user --user foo --pass bar

## Admin Portal

Add a user:

    $ sudo vpn-admin-portal-add-user --user foo --pass bar

## OpenVPN Config

Before we can generate an OpenVPN configuration, we need to start Apache to 
make the API available:

    $ sudo systemctl start httpd

Generate a configuration, including certificates:

    $ sudo vpn-server-node-server-config --profile internet --generate

Enable OpenVPN on boot, and start it:

    $ sudo systemctl enable openvpn@default-internet-0
    $ sudo systemctl start openvpn@default-internet-0

## Firewall

Modify `/etc/vpn-server-node/firewall.php` if you want.

Generate the firewall:

    $ sudo vpn-server-node-generate-firewall --install

Enable and start the firewall:

    $ sudo systemctl enable iptables
    $ sudo systemctl enable ip6tables
    $ sudo systemctl restart iptables
    $ sudo systemctl restart ip6tables

# Using

The user and admin portals should now be available at 
`http://vpn.example.org/vpn-user-portal` and 
`http://vpn.example.org/vpn-admin-portal`.

In the user portal you can create a VPN client configuration and download it. 
You can easily import it in NetworkManager. The OpenVPN configuration file is
fully supported in NetworkManager on Fedora >= 24. It also works on Android, 
iOS, macOS and Windows.

# Security

## TLS

After getting things to work, you SHOULD configure TLS, make sure DNS is 
working properly first.

    $ sudo dnf -y install mod_ssl certbot

Currently, [certbot](https://certbot.eff.org/) can only obtain a certificate 
for you, not automatically configure it. 

    $ sudo systemctl stop httpd
    $ sudo certbot certonly

Follow the certbot "wizard". Open `/etc/httpd/conf.d/ssl.conf` and modify 
these lines:

    SSLCertificateFile /etc/letsencrypt/live/vpn.example.org/cert.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/vpn.example.org/privkey.pem
    SSLCertificateChainFile /etc/letsencrypt/live/vpn.example.org/chain.pem

Start Apache again:

    $ sudo systemctl start httpd

Add the following to your `/etc/cron.daily/certbot`:

    #!/bin/sh
    /usr/bin/certbot renew --pre-hook "systemctl stop httpd" --post-hook "systemctl start httpd" -q

Then, make the file executable:

    $ chmod 0755 /etc/cron.daily/certbot

Make sure you test your configuration by doing a 
[SSL Server Test](https://www.ssllabs.com/ssltest/) and updating the 
configuration in `ssl.conf` as required. A good resource is the 
[Mozilla SSL Configuration Generator](https://mozilla.github.io/server-side-tls/ssl-config-generator/) 
to further tighten the security. Don't forget 
[securityheaders.io](https://securityheaders.io/) to make sure you also follow
their advice.

## Secure Cookies

In order to force cookies to be only sent over HTTPS, you SHOULD modify the 
files `/etc/vpn-user-portal/default/config.php` and 
`/etc/vpn-admin-portal/default/config.php` and set the `secureCookie` option
to `true`.

# Advanced

## Port Share

By default, OpenVPN will only listen on `udp/1194`, the default port of 
OpenVPN. In order to avoid most firewalls it makes sense to also listen on 
`tcp/443`, the HTTPS port. Because Apache is already listening there, we need
a way to share the port between Apache and OpenVPN.

We will be using SNI Proxy. This means that all HTTP traffic appears to come 
from `localhost`, so the filtering in Apache no longer works. This exposes the 
API to the web. To make this less of a problem, the default API secrets MUST be 
updated: 

    $ sudo vpn-server-api-update-api-secrets

Once that taken care of, we create an additional OpenVPN process. Modify 
`/etc/vpn-server-api/default/config.php` and change `processCount` from `1` to 
`2`.

We need an additional management port that OpenVPN can use:

    $ sudo semanage port -a -t openvpn_port_t -p tcp 11941

Regenerate the server configuration, and enable it:

    $ sudo vpn-server-node-server-config --profile internet
    $ sudo systemctl enable openvpn@default-internet-1
    $ sudo systemctl start openvpn@default-internet-1

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
        fallback 127.0.0.1:1194
        table https_hosts
    }

    table https_hosts {
        vpn.example.org 127.0.0.1:8443
    }

Start and enable SNI Proxy:

    $ sudo systemctl enable sniproxy
    $ sudo systemctl start sniproxy

If you now download a new configuration in the user portal, you'll notice that
there is an extra `remote` line specifying `tcp/443`.

## Two-Factor Authentication

Users can enroll themselves for two-factor authentication for the user and 
admin portal out of the box via the "Account" tab in the user portal. See the
documentation in the user portal for more information on supported two-factor
applications.

To enable it for connecting to the VPN server, modify 
`/etc/vpn-server-api/default/config.php` and set `twoFactor` to `true` under
the `internet` profile.

Regenerate the server configuration, and restart the OpenVPN process, if you 
enabled "Port Share" you also need to restart `openvpn@default-internet-1`.

    $ sudo vpn-server-node-server-config --profile internet
    $ sudo systemctl restart openvpn@default-internet-0
    $ #sudo systemctl restart openvpn@default-internet-1

After this, if users want to download a new configuration, they will be forced 
to enroll for two-factor authentication first before being allowed to download 
the configuration. Existing users will need to update their VPN configuration
or download a new configuration.

The two-factor authentication will require users to provide the user name 
`totp` and a 6 digit TOTP key generated with the OTP application.

## Using PHP-FPM

Switching to PHP-FPM will improve the performance substantially. First, 
install PHP-FPM:

    $ sudo dnf -y install php-fpm

Remove the package containing the Apache "mod_php" PHP module:

    $ sudo dnf remove php

Enable and start PHP-FPM:

    $ sudo systemctl enable php-fpm
    $ sudo systemctl start php-fpm

Restart Apache:

    $ sudo systemctl restart httpd

That's it!

## API / Applications

There is also an API available for (mobile) applications to integrate with the
VPN software.

The API needs to be enabled, by modifying 
`/etc/vpn-user-portal/default/config.php` and setting `enableOAuth` to `true`. 
By default, this will then allow the listed application(s) to use the API. 

A document for "API discovery" needs to be installed called `info.json` and 
placed in `/var/www/html/info.json`, change the host name accordingly:

    {
        "api": {
            "http://eduvpn.org/api#1": {
                "authorization_endpoint": "https://vpn.example/portal/_oauth/authorize",
                "create_config": "https://vpn.example/portal/api.php/create_config",
                "profile_list": "https://vpn.example/portal/api.php/profile_list",
                "system_messages": "https://vpn.example/portal/api.php/system_messages",
                "user_messages": "https://vpn.example/portal/api.php/user_messages"
            },
            "http://eduvpn.org/api#2": {
                "authorization_endpoint": "https://vpn.example/portal/_oauth/authorize",
                "create_certificate": "https://vpn.example/portal/api.php/create_certificate",
                "profile_config": "https://vpn.example/portal/api.php/profile_config",
                "profile_list": "https://vpn.example/portal/api.php/profile_list",
                "system_messages": "https://vpn.example/portal/api.php/system_messages",
                "token_endpoint": "https://vpn.example/portal/_oauth/token",
                "user_messages": "https://vpn.example/portal/api.php/user_messages"
            }
        }
    }

**Proof of Concept**: there is a PoC application available, eduVPN for Android, 
[here](https://eduvpn.surfcloud.nl/app/) that can use this API. After 
installing it, add an "Other" provider and use `https://vpn.example.org` as the
address.
