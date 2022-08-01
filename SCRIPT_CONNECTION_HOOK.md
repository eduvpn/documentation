This page documents how to launch a (custom) script when a VPN client connects, 
and/or disconnects. This can for example be used to verify if a user still 
exists in the LDAP server, or trigger firewall modifications in a remote 
system.

**NOTE**: this describes a FUTURE feature, and is not yet available in a 
released version. We aim to include this in 3.0.4 server.

## Configuration

You can enable running a script in `/etc/vpn-user-portal/config.php` by setting
the `connectScriptPath` configuration option, e.g.:

```php
    'connectScriptPath' => '/usr/local/bin/connect.sh',
```

Make sure the script is available under that path and is set to be 
"executable", i.e. `chmod +x /path/to/script`.

## Variables

A number of variables will be exposed to the script through 
_environment variables_:

| Variable         | Description                                          |
| ---------------- | ---------------------------------------------------- |
| `EVENT`          | `C`: Connect, `D`: Disconnect                        |
| `USER_ID`        | User ID                                              |
| `PROFILE_ID`     | Profile ID                                           |
| `CONNECTION_ID`  | OpenVPN: X.509 certificate CN, WireGuard: Public Key |
| `IP_FOUR`        | IPv4 address assigned to VPN client                  |
| `IP_SIX`         | IPv6 address assigned to VPN client                  |
| `ORIGINATING_IP` | OpenVPN only: original IP address of VPN client      |

## Example Script

This is an example script that calls a remote service on a specific URL, 
depending on whether it is a `CONNECT` or `DISCONNECT` event:

```bash
#!/bin/sh

if [ "C" == "${VPN_EVENT}" ]; then
        REMOTE_URL=https://www.example.org/connect
else
        REMOTE_URL=https://www.example.org/disconnect
fi

curl \
    ${REMOTE_URL} \
    --data-urlencode "ip_four=${VPN_IP_FOUR}" \
    --data-urlencode "ip_six=${VPN_IP_SIX}" \
    --data-urlencode "user_id=${VPN_USER_ID}"
```

**NOTE**: The _return value_ of the script MUST be `0`, otherwise the VPN 
client connection will be _rejected_!

## Considerations

The script will be triggered for both OpenVPN and WireGuard connections. Due to 
the nature of how we implement WireGuard, this will be at slightly different
moments: for WireGuard the script is called when the client configuration is
_created_, for OpenVPN the script is called when the client actually connects.

This is most obvious when users are using the VPN Portal: on configuration 
download for WireGuard the "connect" event is triggered and on deletion 

## TODO

Items we MUST investigate/test before we can declare this feature stable:

* Make sure when "housekeeping" scripts are running to clean up expired 
  configurations that also the disconnect event is triggered for WireGuard!
