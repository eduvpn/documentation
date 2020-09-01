# Client Certificate Authentication

It is rather easy to enable X.509 client certificate authentication for the 
portal. No need for complicated user authentication scenarios if you client
devices already have access to an organization issued client certificate.

## Web Server

**NOTE** configuring client certificate authentication is **separate** from 
the server certificate you MUST configure on your VPN server!

In `/etc/httpd/conf.d/vpn.example.conf` inside the `<VirtualHost *:443>` 
section you can add the following lines:

    SSLVerifyClient require
    SSLVerifyDepth 1
    SSLCACertificateFile /etc/pki/tls/certs/ca.crt
    SSLUserName SSL_CLIENT_S_DN_CN
    
Point `SSLCACertificateFile` to your client certificate validating CA. On 
Debian/Ubuntu this is probably somewhere under `/etc/ssl`. The `SSLUserName` 
variable is set to the SSL variable you want to use as the user's User ID. See
[Environment Variables](https://httpd.apache.org/docs/2.4/mod/mod_ssl.html#envvars) 
for more options.

Restart the web server:

    $ sudo systemctl restart apache2    # Debian/Ubuntu
    $ sudo systemctl restart httpd      # CentOS/RHEL/Fedora

## Portal

Modify `/etc/vpn-user-portal/config.php` and (mis)use the `ShibAuthentication` 
authentication. This authentication module has access to Apache's "Environment 
Variables", so we can use this here as well.

    'authMethod' => 'ShibAuthentication',
    
    // ...
    
    'ShibAuthentication' => [
        'userIdAttribute' => 'REMOTE_USER',
    ]
    
    // ...
    
`REMOTE_USER` is set by the `SSLUserName` option in the Apache configuration.
