This document will describe how to add your VPN server to join the distributed
network of VPN servers. We assume you used the offical installation 
instructions using the `deploy_${PLATFORM}.sh` script.

You need to perform the following steps:

1. Allow other VPN servers from the central list of VPN servers to use your VPN 
   server;
2. Have your public key published in the registry so other servers will accept
   users from your server.

# Allowing VPN Servers from the Registry

Modify `/etc/vpn-user-portal/default/config.php`, under the `Api` section 
add the `foreignKeyListSource` and `foreignKeyListPublicKey` fields. You can 
look at the example configuration file 
[here](https://github.com/eduvpn/vpn-user-portal/blob/master/config/config.php.example) 
on how to do this. Make sure you use the "production" values.

```php
    ...

    'Api' => [
            
        ...


        'foreignKeyListSource' => 'https://static.eduvpn.nl/disco/secure_internet.json',
        'foreignKeyListPublicKey' => 'E5On0JTtyUVZmcWd+I/FXRm32nSq8R2ioyW7dcu/U88=',

        ...
    ],

    ...

```

# Have Your Server Added to the Registry

You can have your own VPN server added to 
`https://static.eduvpn.nl/disco/secure_internet.json` by sending your VPN 
server's (OAuth) public key to `eduvpn@surfnet.nl`. Please also provide the 
information that is used by the other instances already in the JSON file so we 
can create a complete entry. To find the public key of your server:

```bash
    $ sudo vpn-user-portal-show-public-key 
    ZpdJhuiTiV54K2OIR1ad8KB9selSUfDG4ASrqI5cQoY=
```

After your public key is added, it takes generally up to an hour for cronjobs
to run on all servers fetching the new JSON file and allowing users of your
server to use the other servers and allow users of other servers to use your 
server.
