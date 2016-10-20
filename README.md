# Introduction

This is the eduvpn documentation repository. You can find documents, scripts
and deploy instructions for various deployment scenarios.

# Features

- OpenVPN server accepting connections on various UDP ports and `TCP/443`;
- Support (out of the box) multiple UDP instances for load sharing purposes;
- IPv6 support inside the VPN tunnel;
  - IPv6 in the outer tunnel requires additional setup;
- Support both NAT and routable IP addresses;
- CA for managing client certificates;
- User Portal to allow users to manage their configurations for their 
  devices;
- Multi Language support in the User Portal;
- OAuth 2.0 [API](API.md) for integration with applications;
- Admin Portal manage users, configurations and connections;
- [Two-factor authentication](2FA.md) (TOTP) support with user self-enrollment
  for both access to the portal(s) and the VPN;
- [Deployment scenarios](PROFILE_CONFIG.md):
  - Route all traffic over the VPN (for safer Internet usage on untrusted 
    networks);
  - Route only some traffic over the VPN (for access to the organization 
    network);
  - Client-to-client only networking;
- Support multiple deployment scenarios [simultaneously](MULTI_PROFILE.md);
- Support [multiple instances](MULTI_INSTANCE.md);
- Support for [multiple nodes](MULTI_NODE.md) for better redundancy or access
  points in different locations;
- Group [ACL](ACL.md) support, including [VOOT](http://openvoot.org/);
- Ability to disable all OpenVPN logging;

The VPN server is working with and tested on a variety of platforms and 
clients:
  - Windows (OpenVPN Community Client, Viscosity)
  - OS X (Tunnelblick, Viscosity)
  - Android (OpenVPN for Android, OpenVPN Connect)
  - iOS (OpenVPN Connect)
  - Linux (NetworkManager/CLI)

# Architecture

The architecure is described in a [separate document](ARCHITECTURE.md).

# Authentication 

By default a user name/password login on the User/Admin portal is used, but it 
is easy to enable SAML authentication for identity federations, this is 
documented separately. See [SAML](SAML.md).

For connecting to the VPN service by default only certificates are used, no 
additional user name/password authentication. It is possible to enable 
[2FA](2FA.md) to require an additional TOTP.

# Deployment

For simple one server deployments and tests, we have a simple deploy script 
available you can run on a fresh CentOS 7 installation. It will configure all
components and will be ready to use after running!

    $ curl -L -O https://github.com/eduvpn/documentation/archive/master.tar.gz
    $ tar -xzf master.tar.gz
    $ cd documentation-master

Modify `deploy.sh` to set `HOSTNAME` to the name you want to use for the server 
and possibly the `EXTERNAL_IF` parameter to point to the adapter connecting to 
the Internet. 

Make sure the `HOSTNAME` you use can be resolved through DNS _OR_ is set in 
your `/etc/hosts` file on the machine you want to access the service from, 
e.g.:

    10.20.30.40 vpn.example

Then run the script:

    $ sudo ./deploy.sh

# Users

By default there is a user `me` with a generated password for the User Portal
and a user `admin` with a generated password for the Admin Portal. Those are
printed at the end of the deploy script.

If you want to update/add users you can use the `vpn-user-portal-add-user` and
`vpn-admin-portal-add-user` scripts:

    $ sudo vpn-user-portal-add-user --instance vpn.example --user john --pass s3cr3t

Or to update the existing `admin` password:

    $ sudo vpn-admin-portal-add-user --instance vpn.example --user admin --pass 3xtr4s3cr3t

# CA certificate
You can request a certificate from your CA after running the script. The script
put a `vpn.example.csr` file in the directory you ran the script from.

Once you obtained the certificate, you can overwrite 
`/etc/pki/tls/certs/vpn.example.crt` with the certificate you obtained and 
configure the certificate chain as well in `/etc/httpd/conf.d/ssl.conf`. Feel
free to use [Let's Encrypt](https://letsencrypt.org/).

Make sure you check the configuration with 
[https://www.ssllabs.com/ssltest/](https://www.ssllabs.com/ssltest/)!
