# Script Connection Hook

This page documents how to launch a (custom) script when a VPN client connects, 
and/or disconnects. This can for example be used to verify if a user still 
exists in the LDAP server, or trigger firewall modifications in a remote 
system.

**NOTE**: this describes a **PREVIEW** feature. We aim to fully support this 
feature starting from server version >= 3.1. Please test and provide us with 
feedback if you want to use this feature to make sure it satisfies your 
requirements! Be aware that you MAY need to update your configuration when 
using this feature before we consider this feature stable! The more feedback we 
get, the better!

## Configuration

You can enable running a script in `/etc/vpn-user-portal/config.php` by setting
the `connectScriptPath` configuration option, e.g.:

```php
    'connectScriptPath' => '/usr/local/bin/my_script.sh',
```

Make sure the script is available under that path and is set to be 
"executable", e.g.: `sudo chmod +x /usr/local/bin/my_script.sh`.

## Variables

A number of variables will be exposed to the script through 
_environment variables_:

| Variable             | Description                                          | Event    | 
| -------------------- | ---------------------------------------------------- | -------- |
| `VPN_EVENT`          | `C`: Connect, `D`: Disconnect                        | `C`, `D` |
| `VPN_USER_ID`        | User ID                                              | `C`, `D` |
| `VPN_PROFILE_ID`     | Profile ID                                           | `C`, `D` |
| `VPN_CONNECTION_ID`  | OpenVPN: X.509 certificate CN, WireGuard: Public Key | `C`, `D` |
| `VPN_IP_FOUR`        | IPv4 address assigned to VPN client                  | `C`, `D` |
| `VPN_IP_SIX`         | IPv6 address assigned to VPN client                  | `C`, `D` |
| `VPN_ORIGINATING_IP` | OpenVPN only: original IP address of VPN client      | `C`      |
| `VPN_PROTO`          | `wireguard` or `openvpn`                             | `C`, `D` |
| `VPN_BYTES_IN`       | Bytes received from VPN client                       | `D`      |
| `VPN_BYTES_OUT`      | Bytes sent to VPN client                             | `D`      |

`VPN_PROTO`, `VPN_BYTES_IN` and `VPN_BYTES_OUT` are available in 
vpn-user-portal >= 3.2.0.

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
    --fail \
    --data-urlencode "ip_four=${VPN_IP_FOUR}" \
    --data-urlencode "ip_six=${VPN_IP_SIX}" \
    --data-urlencode "user_id=${VPN_USER_ID}" \
    ${REMOTE_URL}
```

**NOTE**: The _return value_ of the script MUST be `0`, otherwise the VPN 
client connection will be _rejected_!

## Considerations

The script will be triggered for both OpenVPN and WireGuard connections. Due to 
the nature of how we implement WireGuard, this will be at slightly different
moments: for WireGuard the script is called when the client configuration is
_created_, for OpenVPN the script is called when the client actually connects.

This is most obvious when users are using the VPN Portal: on configuration 
download for WireGuard the "connect" event is triggered and on deletion the 
"disconnect" event. For OpenVPN it remains on actual VPN connect/disconnect. 
When using the eduVPN/Let's Connect! applications through the API there is 
functionally no difference.

## TODO

Items we MUST investigate/test before we can declare this feature stable:

* Make sure when "housekeeping" scripts are running to clean up expired 
  configurations that also the disconnect event is triggered for WireGuard!
* Should we make a 'generic' way to reject connections? i.e. have the 
  `ConnectionHookInterface` methods return `bool` so we can show a "nice" error 
  to the user instead of a `HTTP 500`?
