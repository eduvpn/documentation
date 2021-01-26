# IRMA Authentication

**NOTE**: IRMA authentication is NOT supported, you are on your own!

**NOTE**: The IRMA server is NOT part of the VPN software packages. **YOU** 
are responsible for its installation, configuration, installing updates, 
keep it secure and in general keep it running!

**NOTE**: IRMA authentication is NOT production ready! Check the bottom of this
document for open issues.

We assume that you already have a working VPN server with valid TLS 
certificate. See [deployment](README.md#deployment) if you do not already.

## IRMA Server Installation & Configuration

Download and install the IRMA server according to the 
[documentation](https://irma.app/docs/getting-started/). Use the following 
configuration file, e.g. `irma.yml`:

```
# listen only on "localhost" as traffic goes either directly
# to localhost, *or* through the reverse proxy
listen_addr: 127.0.0.1
port: 8088
# this is the URL used by the app to connect to the IRMA-go server through the
# (reverse) proxy
url: https://vpn.example/irma
no_email: true

requestors:
  vpn:
    # the attribute to be used for the user ID
    disclose_perms: [pbdf.sidn-pbdf.email.email]
    auth_method: token
    # key to allow VPN portal to talk to server. Generate one using e.g. 
    # `pwgen -s 32 -n 1`
    key: dz0OSwTqr0tJxpH7uJ9GL0PZMf3OCELF
```

To start the IRMA server:

```
$ irma server -c irma.yml --production
```
 
## Portal Configuration

Modify `/etc/vpn-user-portal/config.php` by changing `authMethod` to 
`IrmaAuthentication` and adding the `IrmaAuthentication` section. For example:

```
// ...

'authMethod' => 'IrmaAuthentication',

// ...

'IrmaAuthentication' => [
    // Specify the URL to your (local) IRMA server.
    // OPTIONAL, DEFAULT: http://localhost:8088
    //'irmaServerUrl' => 'http://localhost:8088',

    // The attribute used for the user ID in the service
    'userIdAttribute' => 'pbdf.sidn-pbdf.email.email',

    // The token to talk to the session endpoint of the IRMA server, make
    // sure it matches the one configured in the IRMA server config
    'secretToken' => 'dz0OSwTqr0tJxpH7uJ9GL0PZMf3OCELF',
],
```

Change the Apache configuration to add the reverse proxy line to allow the IRMA 
app to talk to the IRMA server. Modify `/etc/httpd/conf.d/${WEB_FQDN}.conf` and
add the following line in the `<VirtualHost *:443>` section:

```
ProxyPass   "/irma/"   "http://localhost:8088/irma/"
```

Restart Apache:

```
$ sudo systemctl restart httpd
```

## Open Issues / TODO

* Can we implement IRMA authentication without using any JS in the browser? 
  That seems doable: the only issue might be that the server doesn't know when 
  the app completes and thus has to do some kind of polling, or ask the user
  to click a button when they are finished with the app...
* Bug in `irma.js` that uses inline CSS to style stuff, bad JS! So you need to
  modify `/etc/httpd/conf.d/vpn-user-portal.conf`: 
  `Header always set Content-Security-Policy "default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:"`
* Properly package the IRMA server for Debian/Fedora
* Build the `irma.js` file from source, this is simply a "binary" taken from 
  a Gitlab server
* Is the proxy configuration safe like this? Is really only `/irma` accessible
  on the irma-go server? Or can you use `../../` trickery? If this is safe 
  we can remove the token authentication!
* Document how to properly integrate with systemd
