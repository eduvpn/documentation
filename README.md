# Introduction
This is the eduVPN deploy manual.

# Software Requirements
CentOS >= 6.6 is the only officially supported deployment platform. However, 
it should also work on Fedora >= 20, CentOS >= 7.1 and Red Hat 
Enterprise >= 6.6 or >= 7.1.

# Hardware Requirements
It is highly recommended to use at least three (virtual) machines to run this.

1. the `vpn-cert-service` (CERT) machine handling the signing/configuration 
   management an revocation. The web service MUST only available to the other 
   two machines
2. the `vpn-user-portal` (PORTAL) machine handling the user interaction. It 
   MUST have access to the `vpn-cert-service` and have a password to use the 
   API
3. the OpenVPN (VPN) machine handling the VPN connections. It does not need to 
   have a connection to `vpn-user-portal` machine, and only needs read access 
   to the `ca.crl` URL on the `vpn-cert-service` machine. It does not need a 
   password to access the API

# Security Considerations

    +-----+         +------+         +--------+
    |     |  VLAN1  |      |  VLAN2  |        |
    | VPN +---------+ CERT +---------+ PORTAL |
    |     |         |      |         |        |
    +--+--+         +------+         +----+---+
       |                                  |
       |                                  |
       | Internet                         | Internet
          
Of course, CERT should also get software and security updates, but it should 
not be reachable from the Internet in any way. Only through the VLANs from 
PORTAL and VPN.

VPN should only be able to retrieve the CRL from CERT.
PORTAL should only be allowed to send POST and DELETE requests to CERT to 
generate and delete configurations.

For testing purposes of course this can be deployed on one machine. But for
production you MUST use at least three machines with sufficient security in 
place to avoid unauthorized access.

## Revoking a VPN server certificate
A potential problem is the revocation of a server in case its private key falls
into the wrong hands. In order to solve this, all clients need to become 
aware of this fact and thus need to also obtain the CRL periodically. This is 
a bit of a nightmare as the CRL needs to be downloaded regularly by all the
clients. One of the potential solutions for this is use short lived server
certificates that last e.g. one day. This is highly cumbersome.

**UNSOLVED PROBLEM**

# Docker
See `docker/` directory. Currently only `vpn-cert-service `and 
`vpn-user-portal` can be tested. OpenVPN will not be running inside the 
Docker container.

# Repositories
For CentOS/Red Hat Enterprise you will need to enable 
[EPEL](https://fedoraproject.org/wiki/EPEL#How_can_I_use_these_extra_packages.3F).

# Packages
The software is contained in two projects:

- [vpn-user-portal](https://github.com/fkooman/vpn-user-portal)
- [vpn-cert-service](https://github.com/fkooman/vpn-cert-service)

The component `vpn-user-portal` is the UI for the end user, protected by SAML 
(using `mod_mellon`). It interacts with `vpn-cert-service` using a HTTP API 
protected by basic authentication.

The `vpn-cert-service` component is responsible for all the 'low level' 
configuration handling like running the CA, generating certificates, generating 
configurations, handling revocations and maintaining the CRL.

These components depend on the following PHP libraries that are not available
in EPEL or the base repository:

- [php-lib-rest](https://github.com/fkooman/php-lib-rest)
- [php-lib-rest-plugin-basic](https://github.com/fkooman/php-lib-rest-plugin-basic)
- [php-lib-rest-plugin-mellon](https://github.com/fkooman/php-lib-rest-plugin-mellon)
- [php-lib-ini](https://github.com/fkooman/php-lib-ini)
- [php-lib-json](https://github.com/fkooman/php-lib-json)

These libraries are also all packaged as RPMs. All required files for 
generating the RPMs are available in the project directories under the `rpm` 
directory in their respective repository.

# Building RPMs
You can regenerate the eduVPN RPMs (or any of its dependencies) yourself from
source using the files in the `rpm` directory of this project. On a development 
machine you can do the following:

    $ sudo yum install rpmdevtools createrepo
    $ rpmdev-setuptree

    $ cd rpm
    $ sh ./build_all.sh

This should create the RPMs in `${HOME}/rpmbuild/RPMS`, ready for install using
`yum`. See `build_all.sh` source for more information and an `rsync` example to
copy the whole repository to a web server.

# Installation
For your convenience the RPMs are also available from two repositories, signed 
with my GPG key:

    https://www.php-oauth.net/repo/fkooman/fkooman.repo
    https://www.php-oauth.net/repo/eduVPN/eduVPN.repo

The first one contains the dependencies, the second one the actual eduVPN 
software. The GPG key can be found here:

    https://www.php-oauth.net/repo/fkooman/RPM-GPG-KEY-fkooman

You can install it with `rpm --import RPM-GPG-KEY-fkooman` and then add the
`repo` files to `/etc/yum.repos.d`.

To install `vpn-cert-service`: 
    
    $ sudo yum -y install vpn-cert-service

To install `vpn-user-portal`:

    $ sudo yum -y install vpn-user-portal

You will also want to install `mod_ssl`. The `mod_auth_mellon` package is an 
(indirect) dependency of `vpn-user-portal`. 

# Configuration
Both `vpn-cert-service` and `vpn-user-portal` will have a working configuration
file on installation. But you SHOULD update the configuration files in 
`/etc/vpn-user-portal` and `/etc/vpn-cert-service` to suit your environment if
needed. For example if you want to use something else than SQlite, you need to
setup your database first and modify the configuration.

You then need to run the database initialization scripts, they will populate
the database:

    $ sudo -u apache vpn-cert-service-init
    $ sudo -u apache vpn-user-portal-init

Do not forget to update the passwords and Apache configuration of both 
`vpn-cert-service` (`/etc/httpd/conf.d/vpn-cert-service.conf`) and 
`vpn-user-portal` (`/etc/httpd/conf.d/vpn-user-porta.conf`). They allow only 
connections from `localhost` by default. To generate a password hash you can 
use this:

    $ vpn-cert-service-generate-password-hash mySecretPass

You can add the hash to `/etc/vpn-cert-service/config.ini` and the plain text
value to `/etc/vpn-user-portal/config.ini`.

# SAML configuration
Using the Apache module `mod_auth_mellon`. See 
[php-lib-rest-plugin-mellon](https://github.com/fkooman/php-lib-rest-plugin-mellon) 
documentation for more information on how to configure `mod_auth_mellon`. There
is an example line in `/etc/httpd/conf.d/vpn-user-portal.conf` to "fake"
`mod_auth_mellon` by directly specifying the `MELLON_NAME_ID` request header.

# Server configuration
You can now generate a OpenVPN server configuration on the `vpn-cert-service` 
machine and copy that to OpenVPN machine:

    $ sudo -u apache vpn-cert-service-generate-server-config

Copy/paste the output and place it in `/etc/openvpn/server.conf` on your 
OpenVPN server.

## CRL
The make the CRL work, a 'cronjob' is needed to occasionally retrieve the CRL
from `vpn-cert-service` using the following command:

    # wget -q -N https://example.org/vpn-cert-service/api.php/ca.crl -O /etc/openvpn/ca.crl

Run this as often as you want. Probably every hour is enough. You SHOULD use 
`https` and of course change the domain name to your own server.

Modify the `/etc/openvpn/server.conf` file to use the CRL.

**NOTE: current connections will not be terminated if the certificate is added to the CRL, only new connections will be denied**.
