# Monitoring

We have very minimal monitoring capability in the VPN software as of now. This 
will most likely be improved in the future if there is a need for it.

**NOTE**: this format is NOT "stable". If you depend on this in your scripting
be ready to update when new releases appear!

## CSV

A simple CSV format:

```bash
$ sudo vpn-user-portal-status
profile_id,active_connection_count,max_connection_count,percentage_in_use,wireguard_allocated_ip_count,wireguard_free_ip_count
ams,139,997,13,5,504
```

If you want to see an aggregate of the number of connected clients over all 
profiles, you can use this:

```bash
$ sudo vpn-user-portal-status | tail -n +2 | cut -d ',' -f 2 | awk '{sum+=$1}END{print sum}'
```

## JSON

You can also get the output as JSON:

```bash
$ sudo vpn-user-portal-status --json
[
    {
        "profile_id": "ams",
        "active_connection_count": 137,
        "max_connection_count": 997,
        "percentage_in_use": 13,
        "wireguard_allocated_ip_count": 5,
        "wireguard_free_ip_count": 504
    }
]
```

Show also connected VPN client information:

```bash
[
    {
        "profile_id": "ams",
        "active_connection_count": 136,
        "max_connection_count": 997,
        "percentage_in_use": 13,
        "wireguard_allocated_ip_count": 5,
        "wireguard_free_ip_count": 504,
        "connection_list": [
            {
                "user_id": "Nqw0fn/4jeS06cq/r2lnxm4l6mGY2F2SKiYu/98Aowo=",
                "ip_list": [
                    "192.168.62.2",
                    "fd75:2e3b:af59:8c76::2"
                ],
                "vpn_proto": "openvpn"
            },

            ...
            
        ]
    }
]
```
    
To show all users connected to the profile `ams` you can use something
like this using the [jq](https://stedolan.github.io/jq/) tool:

```bash
$ sudo vpn-user-portal-status --json --connections | jq '.[] | select(.profile_id | contains("ams")) | .connection_list | .[] .user_id' -r
```

To show the number of WireGuard and OpenVPN connections:

```bash
$ sudo vpn-user-portal-status --json --connections | jq '.[] | select(.profile_id | contains("ams")) | .connection_list | .[] .vpn_proto' -r | sort | uniq -c
```

## Alerting

There is an `--alert` flag, with optional percentage parameter, which only
lists entries for which the IP space has higher usage than the parameter. The 
default is `90` indicating `90%`. It considers both the number of currently 
connected clients, and the number of allocated IP addresses for WireGuard.

**NOTE**: the WireGuard IP allocation is only considered in 
vpn-user-portal >= 3.3.6.

You can use the status command from `cron` to send out alerts when the IP space 
is about to be depleted, for example:

```cron
MAILTO=admin@example.org
*/5 * * * * /usr/bin/vpn-user-portal-status --alert 75
```

Assuming `cron` is able to mail reports this should work!

**NOTE**: on Debian/Ubuntu the `vpn-user-portal-status` tool is located in 
`/usr/bin` and not `/usr/sbin` which is an oversight. On Fedora/EL the tool IS 
located in `/usr/sbin`.
