# Statistics

Some very basic anonymous statistics are recorded regarding VPN usage. The 
files are stored in e.g. `/var/lib/vpn-server-api/stats.json`.

The statistics only store information about the last 30 days, information older
than that is automatically removed.

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
