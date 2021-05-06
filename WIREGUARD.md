## Introduction

**NOTE**: WireGuard functionality is **EXPERIMENTAL** and not available in 
any official VPN packages yet! Do NOT use in production!

It is available in the eduVPN/Let's Connect! 3.x development release.

## Requirements

WireGuard will only be supported on servers running Debian >= 11 and 
Fedora >= 34. Currently only Fedora 34 (x86_64) is tested.

You can install the eduVPN 3.x development release on Fedora 34 using the 
`deploy_fedora_v3.sh` script instead of the `deploy_fedora.sh` script. That 
should set up a lot for you already.

## WireGuard Configuration

```
# cat /etc/wireguard/wg1.conf 
[Interface]
Address = 10.85.134.1/24,fd8e:5472:d976:ce6a::1/64
ListenPort = 51820
PrivateKey = QFqtgK09YJ9onVLNNAunZawHojHK+j8SROfHU/NNQ3E=
```

To generate a private key you can use `wg genkey`. Replace the `PrivateKey` 
value with your own value. In order to generate "random" IPv4 and IPv6 prefixes
to use in your configuration you can use the `vpn-user-portal-suggest-ip` 
command. Make sure they match with the `rangeFour` and `rangeSix` parameters
in the portal configuration below. **NOTE**: use `.1` and `::1` in `Address` 
above and use `.0` and `::` in `rangeFour` and `rangeSix`.

To start the WireGuard interface and enable it to start on boot:

```
$ sudo systemctl enable --now wg-quick@wg1
```

Still need to figure out whether this is best way to make this persistent. 
Maybe through NetworkManager or `systemd-networkd` would be better.

## Daemon

You can test the interface with WireGuard:

```
$ curl -s http://localhost:8080/info?Device=wg1
{
  "PublicKey": "2obnZaov/Idd1zHFZqziWurRubx98ldKmDH44nB7nF0=",
  "ListenPort": 51820,
}
```

## Portal

You need to enable WireGuard in the portal configuration by modifying 
`/etc/vpn-user-portal/config.php`. You can add a WireGuard profile:

```
'vpnProfiles' => [
    // OpenVPN Profile
    'default' => [ 
        'vpnType' => 'openvpn',
        'profileNumber' => 1,

        // ...
        
    ],
        
    // WireGuard Profile
    'default-wg' => [
        'vpnType' => 'wireguard',
        'profileNumber' => 2,
        'displayName' => 'Default WireGuard',
        'range' => '10.85.134.0/24',
        'range6' => 'fd8e:5472:d976:ce6a::/64',
        'hostName' => 'vpn.example.org',
        'dns' => ['9.9.9.9', '2620:fe::fe'],
        
        // not all other options are supported yet...
    ],
],
```

## Firewall

We assume you are using the default firewall, some rules need to be added, 
both in the `/etc/sysconfig/iptables` and `/etc/sysconfig/ip6tables` files:

```
-A INPUT -p udp -m state --state NEW -m udp --dport 51820 -j ACCEPT
-A FORWARD -i wg+ ! -o wg+ -j ACCEPT
-A FORWARD ! -i wg+ -o wg+ -j ACCEPT
```

After modifying the firewall, restart it:

```
$ sudo systemctl restart iptables
$ sudo systemctl restart ip6tables
```

**NOTE**: restarting `iptables` and `ip6tables` doesn't (always?) seem to 
work (anymore) on Fedora 34. You may need to reboot your system.

## API

The WireGuard integration also exposes an API for use by apps. It works the 
same way as the existing API, protected using OAuth. This API is in a state of 
flux and will defintely change before being rolled out in production!

Check our [APIv3](API_V3.md) document on how to use it for obtaining WireGuard 
client configurations.

## TODO

- (re)implement portal support for manual configuration downloads
- we currently have a "sync" that adds all peers to WG from DB that were 
  manually created, i.e. not through the API. This needs to be done better, 
  every 2 minutes a partial sync, only peers get added, never removed, is 
  not great... it *does* work, for now... at least we need a call for multi 
  peer add
- implement wg-server-config.php to write `/etc/wireguard/wg*.conf` files in 
  vpn-server-node package
- add entries to `connection_log` table when peer is added/removed so we know
  who had an IP at a certain time
- prevent 1 user claiming all IPs in 2 seconds through API or web, limit to 
  maximum number of configs (also for OpenVPN perhaps...)
- clean up "dead" connections from the daemon (make the sync a *real* sync)
- show WG connections on "Connections" page
- make disable user remove/disable? WG connections
- show WG info on "Info" page
