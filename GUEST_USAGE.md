# Guest Usage

The VPN server software implements "Guest Usage". This means that users of one
VPN server deployment, e.g operated by organization A, can use another 
deployment, say operated by organization B, and vice versa.

The trust created between the VPN servers is based on signatures over OAuth 2.0
access tokens. Each server can configure public keys of other VPN servers it
trusts, thus allowing users of those lists servers to access its VPN service
as well.

This "Guest Usage" scenario is OPTIONAL and DISABLED by default.

# Deployment

In order to list your public key for other VPN servers to list, you can use 
the following command:

```bash
    $ sudo vpn-user-portal-show-public-key 
    ZpdJhuiTiV54K2OIR1ad8KB9selSUfDG4ASrqI5cQoY=
```

There are two ways to configure other public keys:

1. Manually configure public keys;
2. Use a (central) registry that contains a list of vetted public keys.

## Manual

Inside the `Api` section in `/etc/vpn-user-portal/default/config.php`, 
[template](https://github.com/eduvpn/vpn-user-portal/blob/master/config/config.php.example).

```php
    // List of foreign OAuth *PUBLIC* keys of VPN instances for which we
    // want to allow guest usage
    'foreignKeys' => [
        //'vpn.example.org' => 'AABBCC==',
    ],
```

Set the hostname, i.e. `vpn.example.org` to the hostname of the VPN server(s) 
from which you want to allow access and also configure the public key, the 
output of `vpn-user-portal-show-public-key`, as shown above of the other VPN 
server(s).

## Registry

Inside the `Api` section in `/etc/vpn-user-portal/default/config.php`, 
[template](https://github.com/eduvpn/vpn-user-portal/blob/master/config/config.php.example).

```php
    // Fetch a list of foreign public keys automatically
    //
    // ** Production **
    //'foreignKeyListSource' => 'https://static.eduvpn.nl/disco/secure_internet.json',
    //'foreignKeyListPublicKey' => 'E5On0JTtyUVZmcWd+I/FXRm32nSq8R2ioyW7dcu/U88=',
```

The example above is for [eduVPN](https://eduvpn.org). After configuring this, 
the public keys found at that URL will be allowed to access your VPN server. If
you belong to the NREN community and want to be listed in this file as well 
with your VPN server, and thus allowing users of other NRENs to use your VPN 
server (and vice versa) please contact 
[eduvpn@surfnet.nl](mailto:eduvpn@surfnet.nl).
