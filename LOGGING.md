# Logging

There are three places where you can have VPN server logging:

* OpenVPN logging
* VPN client connection logging
* Web server logging

## OpenVPN Log

The OpenVPN logging can be enabled in the 
[Profile Configuration](PROFILE_CONFIG.md#openvpn-enable-log) with the 
`oEnableLog` option. 

This is mostly useful for debugging connection problems, i.e. figure out why a 
client connection was rejected. You can use `journalctl` to "follow" the log:

```
$ sudo journalctl -f -t openvpn
```

## VPN Connection Log

### Portal

Finding out which user had a particular IP address at a specified moment can
be done through the portal as an [admin](PORTAL_ADMIN.md). 

### Syslog

Connect and disconnect events can be written in [syslog](#X) as well.

Modify `/etc/vpn-user-portal/config.php` to enable it:

```
    'Log' => [
        // Write CONNECT/DISCONNECT events to syslog
        // OPTIONAL, DEFAULT = false
        'syslogConnectionEvents' => true,

        // Log the "originating IP", i.e. the IP the VPN client is connecting
        // from. Currently only available for OpenVPN connections.
        // OPTIONAL, DEFAULT = false
        //'originatingIp' => false,
    ],
```

#### Connect

Format:

```
CONNECT ${USER_ID} (${PROFILE_ID}:${CONNECTION_ID}) [${ORIGINATING_IP} => ${IP_FOUR},${IP_SIX}]
```

Example:

```
CONNECT fkooman (prefer-openvpn:FvrfxD1m0rvaxfWKZFY+kXAb3hn2yQjY7O37po1XDGM=) [* => 10.222.172.6,fde6:76bd:ad97:ac5e::6]
```

**NOTE**: the `${CONNECTION_ID}` field is replaced with the X.509 certificate 
_Common Name_ (CN) of the OpenVPN client certificate, or in case of WireGuard 
with the WireGuard Public Key.

If `originatingIp` was set to `true`, the IP address of the client establishing 
the connection is also logged and written instead of the `*`. This is currently
only available when clients connect using OpenVPN.

#### Disconnect

Format:

```
DISCONNECT ${USER_ID} (${PROFILE_ID}:${CONNECTION_ID})
```

Example:

```
DISCONNECT fkooman (prefer-openvpn:FvrfxD1m0rvaxfWKZFY+kXAb3hn2yQjY7O37po1XDGM=)
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
