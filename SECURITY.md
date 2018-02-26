# Security

This document contains some information about the security of the software, 
more specifically: the configuration choices that were made.

## OpenVPN

### Crypto

The basic OpenVPN server (and client) crypto configuration:

    tls-version-min 1.2
    tls-cipher TLS-ECDHE-RSA-WITH-AES-256-GCM-SHA384
    auth SHA256
    ncp-ciphers AES-256-GCM
    cipher AES-256-CBC           # NCP overrides this
    dh none                      # use ECDHE only

On deployments after 2018-02-25, the only supported cipher is 
`AES-256-GCM` and `--tls-crypt` is used instead of `--tls-auth`. This does 
NOT allow OpenVPN 2.3 clients from connecting any longer. See 
[Client Compatibility](PROFILE_CONFIG.md#clientcompatibility) for more 
information.

## PHP

CentOS 7 by default provides PHP 5.4. This is not without risks. This version 
is no longer maintained by the PHP project and depends fully on the Red Hat 
engineers that update it when (security) issues appear. An (experimental) 
script is provided to upgrade to the latest stable PHP version.

See the `resources/` directory for PHP setting changes.

### Sessions

We use [fkooman/secookie](https://github.com/fkooman/php-secookie), a library
to implement secure PHP sessions (and cookies).

## CA

The CA of the VPN service is "online" as it needs to generate valid 
certificates on the fly. The [easy-rsa](https://github.com/OpenVPN/easy-rsa) 
software is used as CA.
