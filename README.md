# Home

Welcome to the VPN server documentation page. This site is intended for 
VPN server operators. It contains information on how to deploy the VPN 
software on a server, but also (technical) details on how to (better) 
integrate the software in existing infrastructure, and how configure the 
software for one's own organization.

**NOTE**: if you are an end-user of eduVPN and want to contact someone, please
try to find the contact information of your organization 
[here](https://status.eduvpn.org/). If you don't know where to go, then contact 
us at [eduvpn-support@lists.geant.org](mailto:eduvpn-support@lists.geant.org).

## Features

This is an (incomplete) list of features of the VPN software:

- OpenVPN server accepting connections on both UDP and TCP ports;
- Uses multiple OpenVPN processes for load sharing purposes;
- Scales from a Raspberry Pi to many core systems with 10GBit networking;
- Full IPv6 support, using IPv6 inside the tunnel and connecting over IPv6;
- Support both NAT and publically routable IP addresses;
- CA for managing client certificates;
- Support for [WireGuard](WIREGUARD.md);
- [Secure](SECURITY.md) server and client configuration out of the box;
- Portal to allow users to manage their configurations for their 
  devices and admins to manage users, configurations and connections;
- Multi Language support;
- Authentication to portals using local user database (default), 
  [LDAP](LDAP.md), [RADIUS](RADIUS.md), [OIDC](MOD_AUTH_OPENIDC.md), 
  [SAML](SAML.md) and [Client Certificates](CLIENT_CERT_AUTH.md);
- OAuth 2.0 [API](API.md) for integration with native eduVPN/Let's Connect! 
  applications;
- [Deployment scenarios](PROFILE_CONFIG.md):
    - Route all traffic over the VPN (for safer Internet usage on untrusted 
      networks);
    - Route only some traffic over the VPN (for access to the organization 
      network);
    - Client-to-client (only) networking;
- Group [ACL](ACL.md) support with SAML and LDAP;
- Ability to disable all OpenVPN logging (default);
- Support multiple deployment scenarios [simultaneously](MULTI_PROFILE.md);
- [SELinux](SELINUX.md) fully enabled (on Fedora);

## Installation

We support the following operating systems for deploying the VPN server:

- [Debian](DEPLOY_DEBIAN.md) 11 (`x86_64`) 
- [Ubuntu](DEPLOY_DEBIAN.md) 22.04 (`x86_64`) 
- [Fedora](DEPLOY_FEDORA.md) 36, 37 (`x86_64`)
- Enterprise Linux
    - [AlmaLinux](DEPLOY_EL.md) 9 (`x86_64`)
    - [Rocky Linux](DEPLOY_EL.md) 9 (`x86_64`)

We recommend you install your VPN server on Debian 11.

**NOTE**: we expect ALL software updates to be installed and the server 
rebooted before you install the VPN software!

**NOTE**: if you want to deploy on multiple machines for load balancing / high 
availability, please follow [these](HA.md) instructions instead!

If you installed a VPN server and want to keep using it, please subscribe to 
the mailing list [here](https://lists.geant.org/sympa/info/eduvpn-deploy). This 
list will be used for announcements of updates and discussion about running the 
VPN software.

## Supported Versions

We support a server release until such time the EOL date has been reached. We 
**ONLY** support the particular release on operating systems that are still 
supported by their vendor!

| Version                                                      | Release Date | OS Support                                                   |  EOL       |
| ------------------------------------------------------------ | ------------ | ------------------------------------------------------------ | ---------- |
| [3](https://docs.eduvpn.org/server/v3/)                      | 2022-05-25   | Debian (>= 11), Ubuntu (>= 22.04), Fedora (>= 36), EL (>= 9) | TBD        |
| [2](https://docs.eduvpn.org/server/v2/)                      | 2019-04-02   | Debian (>= 10), CentOS 7, Fedora (>= 35)                     | 2024-06-30 |
| [1](https://codeberg.org/eduVPN/documentation/src/branch/v1) | 2017-07-13   | _N/A_                                                        | _N/A_      |
