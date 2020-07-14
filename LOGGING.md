---
title: VPN Server Logging
description: How to use/view VPN Server logging
category: documentation
---

# Logging

There are three places where you can have VPN server logging:

* OpenVPN logging
* VPN client connection logging
* Web server logging

## OpenVPN Logging

The OpenVPN logging can be enabled in the 
profile [configuration](PROFILE_CONFIG.md) with the `enableLog` option. This is 
mostly useful for debugging connection problems, i.e. figure out why a client 
connection is rejected. You can use `journalctl` to "follow" the log:

    $ sudo journalctl -f -t openvpn

## VPN Client Connection Logging

VPN Client connection logging is enabled by default. You can access the log 
(indirectly) through the portal given a VPN client IP address and timestamp. 

This only works if you are [admin](PORTAL_ADMIN.md).

## Web Server Logging

The Web server request logging you can enable as well by modifying the virtual 
host configuration, on CentOS in `/etc/httpd/conf.d/vpn.example.org.conf` where 
`vpn.example.org` is the hostname of your VPN server. In the 
`<VirtualHost *:443>` section you can uncomment this line:

    TransferLog logs/vpn.example.org_ssl_access_log

After that, restart Apache:

    $ sudo systemctl restart httpd

The web server log file will be written to 
`/var/log/httpd/vpn.example.org_ssl_access_log`.
