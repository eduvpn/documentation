---
title: Multi Profile
description: Configure VPN Profiles on VPN Server
category: howto
---

It is possible to add additional "profiles" to a VPN service. This is useful 
when you for example have two categories of users using the same VPN server,
e.g. "employees" and "administrators". 

Each profile needs to either use different ports, or different IP addresses 
to listen on. Furthermore, each profile MUST have its own unique 
`profileNumber` and `profileId`. A maximum of 64 profiles is supported.

Below, we will end up with two profiles:

| profileId | profileNumber | displayName    |
| --------- | ------------- | -------------- |
| office    | 1             | Office         |
| admin     | 2             | Administrators |

You may also need to take a look at the [SELinux](SELINUX.md) instructions.

# Configuration

The configuration file `/etc/vpn-server-api/config.php` needs to be 
modified, you can remove the `internet` profile that was there by default:

    'vpnProfiles' => [
        // Office Employees
        'office' => [
            'profileNumber' => 1,
            'displayName' => 'Office',
            ...
            ...
            'hostName' => 'office.vpn.example',
            'range' => '10.0.5.0/24',
            'range6' => 'fd10:0:5::/48',
            'routes' => ['192.168.0.0/24', '192.168.1.0/24'],
            'vpnProtoPorts' => ['udp/1194', 'tcp/1194'],
        ],

        // Administrators
        'admin' => [
            'profileNumber' => 2,
            'displayName' => 'Administrators',
            ...
            ...
            'hostName' => 'admin.vpn.example',
            'range' => '10.0.10.0/24',
            'range6' => 'fd10:0:10::/48',
            'routes' => ['192.168.0.0/24', '192.168.1.0/24', '192.168.5.0/24'],
            'vpnProtoPorts' => ['udp/1195', 'tcp/1195'],
        ],
    ],

It is best to use different `hostName` values for the profiles as this gives 
more flexibility to move to a setup with multiple machines in the future.

If you have multiple (public) IP addresses at your disposal for the VPN server, 
you can use the `listen` key to specify them. This will make you loose the IPv4 
and IPv6 support though, but you _can_ use the same port numbers for both 
profiles. In most cases you will want to keep `::` as the value of `listen` and
just use different ports.

**NOTE**: if you add/modify UDP and TCP ports you may also need to update the 
[firewall](FIREWALL.md)!

## Apply Changes

To apply the changes run the `apply_changes.sh` script from this repository 
on your VPN server.
