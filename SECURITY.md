---
title: Security
description: Security Notes
---

This document contains some information about the security of the software, 
more specifically: the configuration choices that were made.

## OpenVPN

### Crypto

The basic OpenVPN server (and client) crypto configuration:

    tls-version-min 1.2
    tls-cipher TLS-ECDHE-RSA-WITH-AES-256-GCM-SHA384
    dh none
    ncp-ciphers AES-256-GCM
    cipher AES-256-GCM
    auth none
    tls-crypt /path/to/tls-crypt.key

We chose `TLS-ECDHE-RSA-WITH-AES-256-GCM-SHA384` because it is listed in 
[RFC 7525](https://tools.ietf.org/html/rfc7525) (section 4.2). It was the 
only cipher that could be used with RSA keys and AES-256-GCM. Furthermore, 
ECDHE is faster than DHE.

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
uses public key cryptography signed JWT Bearer tokens of the type `EdDSA` 
implemented in [php-jwt](https://git.tuxed.net/fkooman/php-jwt). The `EdDSA` 
JWT token in specified in [RFC 8037](https://tools.ietf.org/html/rfc8037).

The reason we are using public key cryptography for the Bearer tokens is that 
no "back channel" is needed between the services verifying the token and 
issuing the token. This is especially helpful in the case of 
[Guest Usage](GUEST_USAGE.md).

## CA

The CA of the VPN service is "online" as it needs to generate valid 
certificates on the fly. The [easy-rsa](https://github.com/OpenVPN/easy-rsa) 
software is used as CA.

The CA uses keys of length 3072 bits, and signs using RSA-SHA256.
