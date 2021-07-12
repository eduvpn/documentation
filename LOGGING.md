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

## OpenVPN Log

The OpenVPN logging can be enabled in the 
profile [configuration](PROFILE_CONFIG.md) with the `enableLog` option. This is 
mostly useful for debugging connection problems, i.e. figure out why a client 
connection is rejected. You can use `journalctl` to "follow" the log:

    $ sudo journalctl -f -t openvpn

## VPN Connection Log

### Portal

Finding out which user had a particular IP address at a specified moment can
be done through the portal as an [admin](PORTAL_ADMIN.md). 

### Syslog

**NOTE**: this is only available in vpn-server-api >= 2.2.11.

In addition to writing connection information to the database, this information
is also written to _syslog_. 

An example of these log entries:

```
Jul 12 16:48:43 vpn.tuxed.net vpn-server-api[8643]: CONNECT fkooman (default) [10.202.56.2,fd5e:eccc:d4b:783f::1000]
Jul 12 16:48:46 vpn.tuxed.net vpn-server-api[8642]: DISCONNECT fkooman (default) [10.202.56.2,fd5e:eccc:d4b:783f::1000]
```

The format is 
`{CONNECT,DISCONNECT} ${USER_ID} (${PROFILE_ID}) [${IPv4},${IPv6}]`.

## Web Server Log

The Web server request logging you can enable as well by modifying the virtual 
host configuration, on CentOS in `/etc/httpd/conf.d/vpn.example.org.conf` where 
`vpn.example.org` is the hostname of your VPN server. In the 
`<VirtualHost *:443>` section you can uncomment this line:

    TransferLog logs/vpn.example.org_ssl_access_log

After that, restart Apache:

    $ sudo systemctl restart httpd

The web server log file will be written to 
`/var/log/httpd/vpn.example.org_ssl_access_log`.
