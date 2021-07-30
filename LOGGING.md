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

**NOTE**: this is only available in vpn-server-api >= 2.2.11

In addition to writing connection information to the database, this information
is also written to _syslog_. 

An example of these log entries:

```
Jul 12 16:48:43 vpn.tuxed.net vpn-server-api[8643]: CONNECT fkooman (default) [10.202.56.2,fd5e:eccc:d4b:783f::1000]
Jul 12 16:48:46 vpn.tuxed.net vpn-server-api[8642]: DISCONNECT fkooman (default) [10.202.56.2,fd5e:eccc:d4b:783f::1000]
```

The default format is:

```
{{EVENT_TYPE}} {{USER_ID}} ({{PROFILE_ID}}) [{{IP_FOUR}},{{IP_SIX}}]
```

**NOTE**: starting from vpn-server-api >= 2.2.12 there is flexibility in the 
way the log is written. A template can be configured. The default is the format 
shown above. This version also adds the ability to log the "originating IP" of
the VPN client.

You can set the `connectionLogFormat` in `/etc/vpn-server-api/config.php` to 
a string that is used as a template for generating the log lines. You can 
customize this and use the following "variables" that are replaced before 
writing the log line:

* `{{EVENT_TYPE}}`: either `CONNECT` or `DISCONNECT`;
* `{{USER_ID}}`: the user ID;
* `{{PROFILE_ID}}`: the profile that is being connected to;
* `{{IP_FOUR}}`: the IPv4 addresses provided to the VPN client;
* `{{IP_SIX}}`: the IPv6 addresses provided to the VPN client;
* `{{ORIGINATING_IP}}`: the IP address (either IPv4 or IPv6) the VPN client is 
  connecting _from_.

Another example, where the originating IP is also logged could be:

```
{{EVENT_TYPE}} {{USER_ID}} ({{PROFILE_ID}}) [{{ORIGINATING_IP}} => {{IP_FOUR}},{{IP_SIX}}]
```

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
