# Monitoring

We have very minimal monitoring capability in the VPN software as of now. This 
will most likely be improved in the future if there is a need for it.

**NOTE**: this format is NOT "stable". If you depend on this in your scripting
be ready to update when new releases appear!

## CSV

A simple CSV format:

```bash
$ sudo vpn-user-portal-status
profile_id,active_connection_count,max_connection_count,percentage_in_use
ams,109,997,10
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
        "active_connection_count": 109,
        "max_connection_count": 997,
        "percentage_in_use": 10
    }
]
```

Show also connected VPN client information:

```bash
[
    {
        "profile_id": "ams",
        "active_connection_count": 110,
        "max_connection_count": 997,
        "percentage_in_use": 11,
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
default is `90` indicating `90%`. 

You can use the status command from `cron` to send out alerts when the IP space 
is about to be depleted, e.g.:

```cron
MAILTO=admin@example.org
*/5 * * * * /usr/bin/vpn-user-portal-status --alert 75
```

Assuming `cron` is able to mail reports this should work!
