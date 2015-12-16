# Introduction

This is the eduVPN documentation repository. You can find documents, scripts
and deploy instructions for various deployment scenarios.

# Features

- OpenVPN server running allowing connections over UDP/TCP;
- Full IPv6 support;
- Built in CA for managing client certificates;
- User Portal to allow users to manage their own configurations for their 
  devices;
- Admin Portal manage users, configurations and connections

It is also easy to enable SAML authentication for identity federations, this is
documented separatedly. See [SAML](SAML.md).

# Base

For simple one server deployments and tests, we have a simple deploy script 
available you can run on a fresh CentOS 7 installation. It will configure all
components and will be ready to use after running!

    $ curl -L -O https://github.com/eduVPN/documentation/archive/master.tar.gz
    $ tar -xzf master.tar.gz
    $ cd documentation-master

Modify `deploy.sh` to set the hostname you wish to use for the server and then
run the script:

    $ ./deploy.sh

You can request a certificate from your CA after running the script. The script
put a `vpn.example.csr` file in the directory you ran the script from.

Once you obtained the certificate, you can overwrite 
`/etc/pki/tls/certs/vpn.example.crt` with the certificate you obtained and 
configure the certificate chain as well in `/etc/httpd/conf.d/ssl.conf`.

Make sure you check the configuration with 
[https://www.ssllabs.com/ssltest/](https://www.ssllabs.com/ssltest/)!
