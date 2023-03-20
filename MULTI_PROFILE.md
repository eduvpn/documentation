# Multi Profile Deployments

It is possible to add additional "profiles" to a VPN service. This is useful 
when you for example have two categories of users using the same VPN server,
e.g. "employees" and "administrators". 

Each profile has their own [Profile Configuration](PROFILE_CONFIG.md).

Below, we will end up with two profiles:

| profileId | displayName    |
| --------- | -------------- |
| office    | Office         |
| admin     | Administrators |

You may also need to take a look at the [SELinux](SELINUX.md) instructions when
running on Fedora.

## Configuration

The configuration file `/etc/vpn-user-portal/config.php` needs to be 
modified, you can remove the `default` profile that was there if you didn't
modify the default configuration yet.

```
'ProfileList' => [
    // Office Employees
    [
        'profileId' => 'office',
        'displayName' => 'Office',
        'hostName' => 'office.vpn.example',
        'oRangeFour' => '172.23.114.0/24',
        'oRangeSix' => 'fc74:dd8:87c5:a38::/64',
        'routeList' => ['192.168.0.0/23'],
        'oUdpPortList => [1194],
        'oTcpPortList => [1194],
    ],

    // Administrators
    [
        'profileId' => 'admin',
        'displayName' => 'Administrators',
        'hostName' => 'admin.vpn.example',
        'oRangeFour' => '10.61.60.0/24',
        'oRangeSix' => 'fd85:f1d9:20b7:b74c::/64',
        'oUdpPortList => [1195],
        'oTcpPortList => [1195],
    ],
],
```

It is best to use unique `hostName` values for the profiles as this gives 
more flexibility to move to a setup with multiple machines in the future.

**NOTE**: if you add/modify UDP and TCP ports you may also need to update the 
[firewall](FIREWALL.md)!

### Apply Changes

To apply the configuration changes:

```
$ sudo vpn-maint-apply-changes
```
