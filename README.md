# Introduction

**NOTE**: if you are an end-user of eduVPN and want to contact someone, please
contact [eduvpn@surfnet.nl](mailto:eduvpn@surfnet.nl).

This is the eduVPN deploy documentation repository. This documentation is meant
for system administrators that want to deploy their own VPN service based on 
the code that is also used in eduVPN.

You can find documentation, scripts and deploy instructions for various 
scenarios.

# Features

- OpenVPN server accepting connections on both UDP and TCP ports;
- Support (out of the box) multiple OpenVPN processes for load sharing 
  purposes;
- Full IPv6 support, using IPv6 inside the tunnel and connecting over IPv6;
- Support both NAT and routable IP addresses;
- CA for managing client certificates;
- User Portal to allow users to manage their configurations for their 
  devices;
- Multi Language support in the User Portal;
- OAuth 2.0 [API](API.md) for integration with applications;
- Admin Portal manage users, configurations and connections;
- [Two-factor authentication](2FA.md) TOTP and YubiKey support with user 
  self-enrollment for both access to the portal(s) and the VPN;
- [Deployment scenarios](PROFILE_CONFIG.md):
  - Route all traffic over the VPN (for safer Internet usage on untrusted 
    networks);
  - Route only some traffic over the VPN (for access to the organization 
    network);
  - Client-to-client (only) networking;
- Support multiple deployment scenarios [simultaneously](MULTI_PROFILE.md);
- Support [multiple instances](MULTI_INSTANCE.md);
- Support for [multiple nodes](DISTRIBUTED_NODES.md) in different locations;
- Group [ACL](ACL.md) support, including [VOOT](http://openvoot.org/);
- Ability to disable all OpenVPN logging (default);

# Client Support

The VPN server is working with and tested on a variety of platforms and 
clients:

  - Windows (OpenVPN Community Client, Viscosity)
  - OS X (Tunnelblick, Viscosity)
  - Android (OpenVPN for Android, OpenVPN Connect)
  - iOS (OpenVPN Connect)
  - Linux (NetworkManager/CLI)

# Architecture

The architecure is described in a [separate document](ARCHITECTURE.md). 
**NOT UP TO DATE**

# Authentication 

By default a user name/password login on the User/Admin portal is used, but it 
is easy to enable SAML authentication for identity federations, this is 
documented separately. See [SAML](SAML.md).

For connecting to the VPN service by default only certificates are used, no 
additional user name/password authentication. It is possible to enable 
[2FA](2FA.md) to require an additional TOTP or YubiKey.

# Deployment

**At the moment only CentOS 7 is supported!**

## CentOS

For simple one server deployments and tests, we have a deploy script available 
you can run on a fresh CentOS 7 installation. It will configure all components 
and will be ready to use after running!

Not all "cloud" instances will work, because they modify CentOS, by e.g. 
disabling SELinux or other (network) changes. We test only with the official 
CentOS [Minimal ISO](https://centos.org/download/) and the official 
[Cloud](https://wiki.centos.org/Download) images.

**NOTE**: make sure SELinux is **enabled** and the filesystem correctly 
(re)labeled! Look [here](https://wiki.centos.org/HowTos/SELinux).

    $ curl -L -O https://github.com/eduvpn/documentation/archive/master.tar.gz
    $ tar -xzf master.tar.gz
    $ cd documentation-master

Modify `deploy.sh` and set the variables at the top of the file to something 
that makes sense for your deployment. Read the comments at the top of the file.

To run the script:

    $ sudo -s
    $ ./deploy.sh

## Fedora 

**NOT UP TO DATE**

See the [Fedora](FEDORA_VPN_SERVER.md) document, it contains 
all steps to get the software running on a fresh Fedora VM, with more advanced
features like port sharing, TLS using Let's Encrypt and two-factor 
authentication.

The deployment was succesfully tested on the official Fedora 25 cloud image, 
as well as the Fedora 25 image @ [DigitalOcean](https://www.digitalocean.com/).

## Users

By default there is a user `me` with a generated password for the User Portal
and a user `admin` with a generated password for the Admin Portal. Those are
printed at the end of the deploy script.

If you want to update/add users you can use the `vpn-user-portal-add-user` and
`vpn-admin-portal-add-user` scripts:

    $ sudo vpn-user-portal-add-user --instance vpn.example --user john --pass s3cr3t

Or to update the existing `admin` password:

    $ sudo vpn-admin-portal-add-user --instance vpn.example --user admin --pass 3xtr4s3cr3t
