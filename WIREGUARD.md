### Introduction

**NOTE**: WireGuard functionality is **EXPERIMENTAL** and not available in 
any official VPN packages yet! Do NOT use in production!

### Requirements

WireGuard will only be supported on servers running Debian >= 11 and 
Fedora >= 33. Currently only Fedora works.

```
$ sudo dnf -y install wireguard-tools
```

### WireGuard Configuration

```
$ sudo cat /etc/wireguard/wg0.conf
[Interface]
Address = 10.10.10.1/24
Address = fd00:1234:1234:1234::1/64
ListenPort = 51820
PrivateKey = (hidden)
```

To generate a private key you can use `wg genkey`. Put that in the place above
where it says `(hidden)`.

To start it:

```
$ sudo wg-quick up wg0
```

This should be enough to get going. Still need to figure out the best way to 
make this persistent. Either through NetworkManager, networkd or simply using
the `wg-quick` systemd service file.

### Daemon

```
$ sudo dnf -y install wg-daemon
$ sudo systemctl enable --now wg-daemon
```

You can test it out:

```
$ curl -s http://localhost:8080/info | jq
{
  "PublicKey": "2obnZaov/Idd1zHFZqziWurRubx98ldKmDH44nB7nF0=",
  "ListenPort": 51820,
}
```

### Portal

You need to enable WireGuard in the portal configuration by modifying 
`/etc/vpn-user-portal/config.php`, you can also configure WireGuard:

```
// DEFAULT: false
'enableWg' => true,
'WgConfig' => [
    // where to reach "wg-daemon"
    // DEFAULT: http://localhost:8080
    'wgDaemonUrl' => 'http://localhost:8080',

    // the DNS to put in the configuration you send to the clients
    // DEFAULT: 9.9.9.9, 2620:fe::fe
    'dns' => ['9.9.9.9', '2620:fe::fe'],
],
```

### Firewall

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
