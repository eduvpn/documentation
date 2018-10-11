# Security

This document contains some information about the security of the software, 
more specifically: the configuration choices that were made.

## OpenVPN

### Crypto

The crypto configuration when a server was installed with the 1.0.0 release of
the software and the configuration was not updated since then, but the server
configuration is regenerated, as recommended on every update:

    tls-version-min 1.2
    tls-cipher TLS-ECDHE-RSA-WITH-AES-256-GCM-SHA384
    dh none
    ncp-ciphers AES-256-GCM
    cipher AES-256-GCM
    auth SHA256
    tls-auth /path/to/tls-auth.key 0

The basic OpenVPN server (and client) crypto configuration for installations
after XXXX-YY-ZZ:

    tls-version-min 1.2
    tls-cipher TLS-ECDHE-RSA-WITH-AES-256-GCM-SHA384
    dh none
    ncp-ciphers AES-256-GCM
    cipher AES-256-GCM
    auth none
    tls-crypt /path/to/tls-crypt.key

We chose `TLS-ECDHE-RSA-WITH-AES-256-GCM-SHA384` because it is the first non-EC
cipher mentioned in the modern Mozilla 
[Server Side TLS](https://wiki.mozilla.org/Security/Server_Side_TLS#Modern_compatibility) 
configuration recommendation.

## PHP

CentOS 7 by default provides PHP 5.4. This is not without risks. This version 
is no longer maintained by the PHP project and depends fully on the Red Hat 
engineers that update it when (security) issues appear.

See the `resources/` directory for PHP setting changes.

### Sessions

We use [fkooman/secookie](https://git.tuxed.net/fkooman/php-secookie), a 
library to implement secure PHP sessions (and cookies).

## OAuth

The built-in [OAuth server](https://git.tuxed.net/fkooman/php-oauth2-server) 
uses public key cryptography signed Bearer tokens constructed and verified by 
[libsodium](https://libsodium.org/). The reason we are using public key 
cryptography for the Bearer tokens is that no "back channel" is needed between 
the services verifying the token and issuing the token. This is especially 
helpful in the case of [Guest Usage](GUEST_USAGE.md).

[Ed25519](https://ed25519.cr.yp.to/) is used for the signatures as documented 
[here](https://download.libsodium.org/doc/public-key_cryptography/public-key_signatures.html).

## CA

The CA of the VPN service is "online" as it needs to generate valid 
certificates on the fly. The [easy-rsa](https://github.com/OpenVPN/easy-rsa) 
software is used as CA.
