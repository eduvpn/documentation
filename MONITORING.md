# Monitoring

**NOTE**: this applies only for vpn-server-api >= 2.1.5 (2020-03-29).

We have very minimal monitoring capability in the VPN software as of now. This 
will most likely be improved in the future if there is a need for it.

## Status

We have a command you can use to query the current usage of the VPN server. It
will show you the profile identifiers, the number of connected clients, the 
maximum number of clients that can connect given the existing IP space 
available for clients and the percentage of that space that is currently being 
used.

### CSV

    $ sudo vpn-server-api-status
    profile_id,active_connection_count,max_connection_count,percentage_in_use
    internet,1,10,10
    institute,0,10,0
    internet-utrecht,0,122,0
    dns-only,0,122,0

**NOTE** this format is NOT stable and SHOULD NOT be relied on for further 
scripting!

If you want to see an aggregate of the number of connected clients, you can use
this:

    $ sudo vpn-server-api-status | tail -n +2 | cut -d ',' -f 2 | awk '{sum+=$1}END{print sum}'

### JSON

    $ sudo vpn-server-api-status --json
    [
        {
            "profile_id": "internet",
            "active_connection_count": 1,
            "max_connection_count": 10,
            "percentage_in_use": 10
        },
        {
            "profile_id": "institute",
            "active_connection_count": 0,
            "max_connection_count": 10,
            "percentage_in_use": 0
        },
        {
            "profile_id": "internet-utrecht",
            "active_connection_count": 0,
            "max_connection_count": 122,
            "percentage_in_use": 0
        },
        {
            "profile_id": "dns-only",
            "active_connection_count": 0,
            "max_connection_count": 122,
            "percentage_in_use": 0
        }
    ]

When using the [vpn-daemon](VPN_DAEMON.md) you can also list the currently 
connected clients:

    $ sudo vpn-server-api-status --json --connections
    [
        {
            "profile_id": "internet",
            "active_connection_count": 1,
            "max_connection_count": 10,
            "percentage_in_use": 10,
            "connection_list": [
                {
                    "user_id": "https://idp.tuxed.net/metadata!https://vpn.tuxed.net/php-saml-sp/metadata!f9FpwLtJ0orFQdKvwOjwaH6DBjpN0n_5FGuJSE2iHnI",
                    "virtual_address": [
                        "10.132.193.4",
                        "fd0b:7113:df63:d03c::1002"
                    ]
                }
            ]
        },
        {
            "profile_id": "institute",
            "active_connection_count": 0,
            "max_connection_count": 10,
            "percentage_in_use": 0,
            "connection_list": [

            ]
        },
        {
            "profile_id": "internet-utrecht",
            "active_connection_count": 0,
            "max_connection_count": 122,
            "percentage_in_use": 0,
            "connection_list": [

            ]
        },
        {
            "profile_id": "dns-only",
            "active_connection_count": 0,
            "max_connection_count": 122,
            "percentage_in_use": 0,
            "connection_list": [

            ]
        }
    ]

## Alerting

There is an `--alert` flag, with optional percentage parameter, which only
lists entries for which the IP space has higher usage than the parameter. The 
default is `90` indicating `90%`. 

You can use the status command from `cron` to send out alerts when the IP space 
is about to be depleted, e.g.:

    MAILTO=admin@example.org
    */5 * * * * /usr/bin/vpn-server-api-status --alert 75

Assuming `cron` is able to mail reports this should work!
