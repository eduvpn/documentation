---
title: Stats
description: Statistics Notes
category: documentation
---

Some very basic anonymous statistics are recorded regarding VPN usage. The 
files are stored in e.g. `/var/lib/vpn-server-api/stats.json`.

The statistics only store information about the last 30 days, information older
than that is automatically removed.

**NOTE**: if you have many users (connections) it may be that PHP runs out of 
memory when running the stats script. You can manually update the available 
memory in `/etc/php.ini`, by increasing `memory_limit = 128M` to something 
higher, e.g. `512M`. To see whether this is fixed already, follow 
[this](https://github.com/eduvpn/vpn-server-api/issues/73) issue.

## Format

This is the format of the statistics file. This data can be used for further
processing.

    {
        "active_user_count": 0,
        "days": [
            {
                "bytes_transferred": 446155708,
                "date": "2017-06-30",
                "number_of_connections": 3,
                "unique_user_count": 1
            },
            {
                ...
            },
            {
                "bytes_transferred": 32027,
                "date": "2017-08-02",
                "number_of_connections": 1,
                "unique_user_count": 1
            }
        ],
        "generated_at": 1501632481,
        "max_concurrent_connections": 19,
        "max_concurrent_connections_time": "2017-07-31 11:44:07",
        "total_traffic": 407896290730,
        "unique_user_count": 70
    }
    
## Detailed Usage Analysis

By directly querying the SQLite database in `/var/lib/vpn-server-api/db.sqlite` 
you can obtain more detailed information about the connections, not available
through the "Stats" page in the (Admin) Portal.

If you connected your VPN server to an identity federation where multiple IdPs
have access and want to see which organizations use the VPN you can do that,
presuming you use the `eduPersonTargetedID` attribute and configured the 
"Shibboleth Style" serialization of the Name ID, `IdP!SP!User ID`, e.g. 
`https://idp.surfnet.nl!https://nl.eduvpn.org/saml!7e17a47e96c28d65d18164ec2e03f3d1c5aabc5e`.

    $ sqlite3 db.sqlite "SELECT DISTINCT(user_id) FROM connection_log" | grep -v '!!' | cut -d '!' -f 1 | sort | uniq -c | sort -n -r

The `grep -v '!!'` is to filter out any record of "Guest Usage" users. See 
below for more on this.

## "Guest Usage" Analysis

In order to check how many users you have originating from other VPN servers, 
you can use a very similar query:

    $ sqlite3 db.sqlite "SELECT DISTINCT(user_id) FROM connection_log" | grep '!!' | cut -d '!' -f 1 | sort | uniq -c | sort -n -r
