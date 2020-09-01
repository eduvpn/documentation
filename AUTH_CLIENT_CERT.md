# Client Certificate Authentication

It is rather easy to enable X.509 client certificate authentication for the 
portal. No need for complicated user authentication scenarios if you client
devices already have access to an organization issued client certificate.

## Web Server

**NOTE**: configuring client certificate authentication is **separate** from 
the server certificate you MUST configure on your VPN server!

In `/etc/httpd/conf.d/vpn.example.conf` inside the `<VirtualHost *:443>` 
section you can add the following lines:

    SSLVerifyClient require
    SSLVerifyDepth 1
    SSLCACertificateFile /etc/pki/tls/certs/ca.crt   # CentOS/RHEL/Fedora
    #SSLCACertificateFile /etc/ssl/certs/ca.crt      # Debian/Ubuntu
    SSLUserName SSL_CLIENT_S_DN_CN
    
Point `SSLCACertificateFile` to your client certificate validating CA. The 
`SSLUserName` variable is set to the SSL variable you want to use as the user's 
User ID. See 
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

## Generating Client Certificates

**NOTE**: this is only for experimentation, mostly a "note to self" :-)

Of course, you could use the X.509 certificates issued for use with OpenVPN 
*also* for authenticating to the portal. But that is a bit of a 🐔🥚 problem 
;-)

For simple testing you can use the "embedded" CA in the VPN server to generate
a separate CA and issue client certificates with it. On your server:

    $ mkdir CA
    $ cd CA
    $ vpn-ca -init-ca -name "My Test CA"
    $ vpn-ca -client -name "foo"
    $ vpn-ca -client -name "bar"

Here we created two client certificates, one for user `foo` (`CN=foo`) and one 
for user `bar` (`CN=bar`). To import them in browsers/OSes it is convenient to 
convert the key/cert to a PKCS#12 file. You can do that using `openssl`:

    $ openssl pkcs12 -export -CAfile ca.crt -in foo.crt -inkey foo.key -out foo.p12
    $ openssl pkcs12 -export -CAfile ca.crt -in bar.crt -inkey bar.key -out bar.p12

The "export" will ask for a password. You'll also need it when importing the 
PKCS#12 file in your OS/browser.

Also make sure you copy the `ca.crt` file to the right place on your VPN 
server, and configure the web server as documented above.
