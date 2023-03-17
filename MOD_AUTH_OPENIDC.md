# Mod Auth OpenIDC

This module configures the Apache web server to operate as an OpenID Connect 
Relying Party (RP) towards an OpenID Connect Provider (OP) using 
[mod_auth_openidc](https://github.com/zmartzone/mod_auth_openidc).

## Installation

### Fedora

```
$ sudo dnf install mod_auth_openidc
$ sudo systemctl restart httpd
```

### Debian / Ubuntu

```
$ sudo apt install libapache2-mod-auth-openidc
$ sudo systemctl restart apache2
```

## Configuration

### OpenID Connect

The below instructions will show you what to do at the _minimum_ to get your
RP working.

You need the following information from your OP:

* `OIDCProviderMetadataURL`: the provider's metadata URL, e.g.: 
  `https://oidc.example.org/.well-known/openid-configuration`;
* `OIDCClientID`: the RP client ID, as obtained for your OP;
* `OIDCClientSecret`: the RP client secret, as obtained from your OP.

You MUST generate your own strong password to use for `OIDCCryptoPassphrase`,
e.g.:

```
$ pwgen -s 64 -n 1
```

Once you have/know all values configure the "VirtualHost" as mentioned below.

### Virtual Host

Modify your Apache "Virtual Host" by changing 
`/etc/apache2/sites-available/vpn.example.org.conf` (Debian / Ubuntu) or 
`/etc/httpd/conf.d/vpn.example.org.conf` (Fedora). The below is an example of
what it should look like. Replace with your own values. 

**NOTE**: do **NOT** reuse the`OIDCCryptoPassphrase` as shown below, generate 
your own as shown above!

```
<VirtualHost *:443>

    ...

    OIDCProviderMetadataURL https://oidc.example.org/.well-known/openid-configuration
    OIDCClientID s2kpEtzBpme1b6VU
    OIDCClientSecret z1YGPSHYHU3T8eY8
    OIDCRedirectURI https://vpn.example.org/vpn-user-portal/redirect_uri
    OIDCCryptoPassphrase 2iSPYVjVeC9cB0PmhUZfSyKVtxwescz7Hyb7oHIbnNbpn5TQDb8npdS1P1oyokYc

    <Location /vpn-user-portal>
        AuthType openid-connect
        Require valid-user
    </Location>

    # do not restrict API Endpoint as used by VPN clients
    <Location /vpn-user-portal/api>
        Require all granted
    </Location>

    # do not secure OAuth Token Endpoint as used by VPN clients
    <Location /vpn-user-portal/oauth/token>
        Require all granted
    </Location> 

    # If you run separete node(s) you MUST allow access to "node-api.php" 
    # withouh protecting it with Shibboleth
    #<Location /vpn-user-portal/node-api.php>
    #    Require all granted
    #</Location>
    ...

</VirtualHost>
```

Make sure you restart Apache, on Fedora:

```
$ sudo systemctl restart httpd
```

On Debian / Ubuntu:

```
$ sudo systemctl restart apache2
```
    
### VPN Portal

Modify `/etc/vpn-user-portal/config.php` and set:

```
    'authModule' => 'OidcAuthModule',
```

Additional configuration, i.e. the `userIdAttribute` and 
`permissionAttributeList` can be done under the `OidcAuthModule` section.
