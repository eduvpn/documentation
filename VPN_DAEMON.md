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
