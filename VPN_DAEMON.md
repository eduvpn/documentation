---
title: VPN Daemon
description: Use VPN Daemon for OpenVPN Management
category: advanced
---

**NOTE**: if you run on Debian, replace `yum` with `apt`.

This document describes how to switch to using the VPN daemon to control 
OpenVPN processes. 

We assume you setup your current VPN server using `deploy_${DIST}.sh` and have 
everything on one machine.

Enabling the daemon is rather simple:

    $ sudo yum -y install vpn-daemon
    $ sudo systemctl enable --now vpn-daemon

Modify `/etc/vpn-server-api/config.php` and add the configuration key 
`useVpnDaemon` and set its value to `true` in the "root", i.e. on the same 
level as `vpnProfiles`, e.g.:

    <?php

    return [

        'useVpnDaemon' => true,

        // List of VPN profiles
        'vpnProfiles' => [
            'internet' => [
                // The number of this profile, every profile per instance has a 
                // unique number
                // REQUIRED
                'profileNumber' => 1,

                // ...

Make sure everything still works, i.e. you can see connected clients when 
visiting the "Connections" tab in the portal.

An additional benefit of using the daemon is that you can see the "load" of the
OpenVPN processes for each profile, for example:

```
$ sudo vpn-server-api-status --json
[
    {
        "profile_id": "amsterdam",
        "active_connection_count": 110,
        "max_connection_count": 488,
        "percentage_in_use": 22,
        "port_client_count": {
            "udp/1194": 17,
            "udp/1195": 20,
            "udp/1196": 29,
            "udp/1197": 23,
            "tcp/443": 9,
            "tcp/1194": 5,
            "tcp/1195": 3,
            "tcp/1196": 4
        }
    }
]
```
