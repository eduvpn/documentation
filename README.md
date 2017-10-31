# Introduction

**NOTE**: if you are an end-user of eduVPN and want to contact someone, please
contact [eduvpn@surfnet.nl](mailto:eduvpn@surfnet.nl).

This is the eduVPN deploy documentation repository. This documentation is meant
for system administrators that want to deploy their own VPN service based on 
the code that is also used in eduVPN.

You can find documentation, scripts and deploy instructions for various 
scenarios.

## Security Contact

If you find a security problem in the code, the deployed service(s) and want to
report it responsibly, contact [fkooman@tuxed.net](mailto:fkooman@tuxed.net). 
You can use PGP. My key is `0x9C5EDD645A571EB2`. The full fingerprint is 
`6237 BAF1 418A 907D AA98  EAA7 9C5E DD64 5A57 1EB2`.

The security contact will change in the future, but for now you can use the 
above information.

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
- Group [ACL](ACL.md) support, including [VOOT](http://openvoot.org/);
- Ability to disable all OpenVPN logging (default);
- Support multiple deployment scenarios [simultaneously](MULTI_PROFILE.md);
- [SELinux](SELINUX.md) fully enabled;

# Client Support

The VPN server is working with and tested on a variety of platforms and 
clients:

  - Windows (OpenVPN Community Client, Viscosity)
  - OS X (Tunnelblick, Viscosity)
  - Android (OpenVPN for Android, OpenVPN Connect)
  - iOS (OpenVPN Connect)
  - Linux (NetworkManager/CLI)

# Deployment

**NOTE**: if you plan to run eduVPN please consider subscribing yourself to the 
mailing list [here](https://list.surfnet.nl/mailman/listinfo/eduvpn-deploy). It 
will be used for announcements of updates and discussion about running eduVPN.

**NOTE**: at the moment only a fully updated official CentOS 7 is supported, 
there is experimental support for Debian >= 9 and Fedora.

* [CentOS](DEPLOY_CENTOS.md)

# Authentication 

## Username & Password

By default there is a user `me` with a generated password for the User Portal
and a user `admin` with a generated password for the Admin Portal. Those are
printed at the end of the deploy script.

If you want to update/add users you can use the `vpn-user-portal-add-user` and
`vpn-admin-portal-add-user` scripts:

    $ sudo vpn-user-portal-add-user --user john --pass s3cr3t

Or to update the existing `admin` password:

    $ sudo vpn-admin-portal-add-user --user admin --pass 3xtr4s3cr3t

## SAML

It is easy to enable SAML authentication for identity federations, this is 
documented separately. See [SAML](SAML.md).

## 2FA

For connecting to the VPN service by default only certificates are used, no 
additional user name/password authentication. It is possible to enable 
[2FA](2FA.md) to require an additional TOTP or YubiKey.

## ACLs

If you want to restrict the use of the VPN a bit more than on whether someone
has an account or not, e.g. to limit certain profiles to certain (groups of)
users, see [ACL](ACL.md).

# Development

See [DEVELOPMENT_SETUP](DEVELOPMENT_SETUP.md).
