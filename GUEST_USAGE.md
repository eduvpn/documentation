---
title: Guest Usage
description: Setup and Enable Guest Usage (VPN Federation)
category: advanced
---

The VPN server software implements "Guest Usage". This means that users of one
VPN server deployment, e.g operated by organization A, can use another 
deployment, say operated by organization B, and vice versa.

The trust created between the VPN servers is based on signatures over OAuth 2.0
access tokens. Each server can configure public keys of other VPN servers it
trusts, thus allowing users of those lists servers to access its VPN service
as well.

This "Guest Usage" scenario is OPTIONAL and **DISABLED** by default.

# Deployment

In the file `/etc/vpn-user-portal/config.php` you need to enable `remoteAccess` 
and the registry:

    'Api' => [

        ...

        'remoteAccess' => true,
        'remoteAccessList' => [
            'production' => [
                'discovery_url' => 'https://static.eduvpn.nl/disco/secure_internet.json',
                'public_key' => 'E5On0JTtyUVZmcWd+I/FXRm32nSq8R2ioyW7dcu/U88=',
            ],
            //'development' => [
            //    'discovery_url' => 'https://static.eduvpn.nl/disco/secure_internet_dev.json',
            //    'public_key' => 'zzls4TZTXHEyV3yxaxag1DZw3tSpIdBoaaOjUGH/Rwg=',
            //],
        ],

        ...

    ],

The `production` example above is to allow access from all 
[eduVPN](https://eduvpn.org/) servers part of the federation. 

If you want to register your server for eduVPN, please contact 
[eduvpn-support@lists.geant.org](mailto:eduvpn-support@lists.geant.org) and 
provide your server's public key, for example:

```bash
$ sudo vpn-user-portal-show-oauth-key 
OAuth Key
    Public Key: o4KD2G_-t1fHVyB8VNpD3DbGEOsWvX6EmuPddJCWCPA
    Key ID    : eia8y1dTfbTIj_6W4fadk6OZPb2jRULclVh69b0ZS20
```
