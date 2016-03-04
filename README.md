# Introduction

This is the eduvpn documentation repository. You can find documents, scripts
and deploy instructions for various deployment scenarios.

# Features

- OpenVPN server running allowing connections over UDP/TCP;
- Full IPv6 support (both to the VPN service as over the VPN tunnel);
- Builtin CA for managing client certificates;
- User Portal to allow users to manage their own configurations for their 
  devices;
- Admin Portal manage users, configurations and connections

It is also easy to enable SAML authentication for identity federations, this is
documented separately. See [SAML](SAML.md).

# Base

For simple one server deployments and tests, we have a simple deploy script 
available you can run on a fresh CentOS 7 installation. It will configure all
components and will be ready to use after running!

    $ curl -L -O https://github.com/eduvpn/documentation/archive/master.tar.gz
    $ tar -xzf master.tar.gz
    $ cd documentation-master

Modify `deploy.sh` to set the hostname you wish to use for the server and then
run the script:

    $ ./deploy.sh

# Users

By default there is a user `foo` with the password `bar` for both the User 
Portal and the Admin Portal. You can easily add new users, but you need to 
generate a password hash. You can generate a hash like this, for example 
below we generate one for the password `s3cr3t`:

    $ php -r "require_once '/usr/share/php/password_compat/password.php'; echo password_hash('s3cr3t', PASSWORD_DEFAULT) . PHP_EOL;"

Put this hash in the files `/etc/vpn-user-portal/config.yaml` and 
`/etc/vpn-admin-portal/config.yaml` in the section `FormAuthentication`, 
e.g.:
    
    FormAuthentication:
        admin: $2y$10$i.vmEWgE9HGqlglI8wXYLeFdMWYvYJxEz5k4fjW/RLvCrCcDk0Xjy

# CA certificate
You can request a certificate from your CA after running the script. The script
put a `vpn.example.csr` file in the directory you ran the script from.

Once you obtained the certificate, you can overwrite 
`/etc/pki/tls/certs/vpn.example.crt` with the certificate you obtained and 
configure the certificate chain as well in `/etc/httpd/conf.d/ssl.conf`.

Make sure you check the configuration with 
[https://www.ssllabs.com/ssltest/](https://www.ssllabs.com/ssltest/)!
