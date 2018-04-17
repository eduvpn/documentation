# Introduction

**NOTE**: if you are an end-user of eduVPN and want to contact someone, please
contact [eduvpn@surfnet.nl](mailto:eduvpn@surfnet.nl).

This is the eduVPN documentation repository. This repository targets
administrators and developers. It contains information on how to deploy the VPN
software, but also (technical) details about the implementation needed to 
(better) integrate it in existing infrastructure, and how to modify the 
software for one's own needs.

# Features

This is an (incomplete) list of features of the VPN software:

- OpenVPN server accepting connections on both UDP and TCP ports;
- Support (out of the box) multiple OpenVPN processes for load sharing 
  purposes;
- Full IPv6 support, using IPv6 inside the tunnel and connecting over IPv6;
- Support both NAT and routable IP addresses;
- CA for managing client certificates;
- User Portal to allow users to manage their configurations for their 
  devices;
- Admin Portal to manage users, configurations and connections;
- Multi Language support in User Portal and Admin Portal;
- Authentication to portals using "static" username and password, 
  [LDAP](LDAP.md), [RADIUS](RADIUS.md) and [SAML](SAML.md);
- OAuth 2.0 [API](API.md) for integration with applications;
- [Two-factor authentication](2FA.md) TOTP and YubiKey support with user 
  self-enrollment for both access to the portal(s) and the VPN;
- [Deployment scenarios](PROFILE_CONFIG.md):
  - Route all traffic over the VPN (for safer Internet usage on untrusted 
    networks);
  - Route only some traffic over the VPN (for access to the organization 
    network);
  - Client-to-client (only) networking;
- Group [ACL](ACL.md) support, including LDAP and [VOOT](http://openvoot.org/);
- Ability to disable all OpenVPN logging (default);
- Support multiple deployment scenarios [simultaneously](MULTI_PROFILE.md);
- [SELinux](SELINUX.md) fully enabled;
- [Guest Usage](GUEST_USAGE.md)

## Client Support

The VPN server is working with and tested on a variety of platforms and 
clients:

  - Windows (OpenVPN Community Client, Viscosity)
  - OS X (Tunnelblick, Viscosity)
  - Android (OpenVPN for Android, OpenVPN Connect)
  - iOS (OpenVPN Connect)
  - Linux (NetworkManager/CLI)

By default, only clients using OpenVPN >= 2.4 (or OpenVPN 3) are supported! See 
[Client Compatibility](PROFILE_CONFIG.md#client-compatibility) for more 
information.

### Native Applications

Applications are being developed that you can use for connecting to the VPN. 
These will work for both the "official" deployments, as well as your own. You 
can find a list [here](https://app.eduvpn.nl/).

# Deployment

**NOTE**: if you plan to run eduVPN please consider subscribing to the 
mailing list [here](https://list.surfnet.nl/mailman/listinfo/eduvpn-deploy). It 
will be used for announcements of updates and discussion about running eduVPN.

**NOTE**: at the moment only a fully updated official CentOS 7 is supported, 
there is experimental support for Debian >= 9 and Fedora.

* [CentOS / Red Hat Enterprise Linux](DEPLOY_CENTOS.md)
* [Fedora](DEPLOY_FEDORA.md) (experimental)
* [Debian](DEPLOY_DEBIAN.md) (experimental)

# Development

See [DEVELOPMENT_SETUP](DEVELOPMENT_SETUP.md).

# Security Contact

If you find a security problem in the code, the deployed service(s) and want to
report it responsibly, contact [fkooman@tuxed.net](mailto:fkooman@tuxed.net). 
You can use PGP. My key is `0x9C5EDD645A571EB2`. The full fingerprint is 
`6237 BAF1 418A 907D AA98  EAA7 9C5E DD64 5A57 1EB2`.
