---
title: Security
description: Security Notes
category: documentation
---

This document contains some information about the security of the software, 
more specifically: the configuration choices that were made.

## OpenVPN

### Crypto

The basic OpenVPN server (and client) crypto configuration:

    tls-version-min 1.2
    tls-cipher TLS-ECDHE-RSA-WITH-AES-256-GCM-SHA384:TLS-ECDHE-ECDSA-WITH-AES-256-GCM-SHA384
    dh none
    ncp-ciphers AES-256-GCM
    cipher AES-256-GCM
    tls-crypt /path/to/tls-crypt.key

We chose `TLS-ECDHE-RSA-WITH-AES-256-GCM-SHA384` as TLS cipher because it is 
listed in [RFC 7525](https://tools.ietf.org/html/rfc7525) (section 4.2). It was 
the only cipher that could be used with RSA keys and AES-256-GCM. Furthermore, 
ECDHE is faster than DHE.

For the data channel we chose to use `AES-256-GCM`.

We do _not_ specify the `auth` OpenVPN configuration option as it is no longer 
used when using an AEAD cipher like `AES-256-GCM` and `tls-crypt`.

**NOTE**: the `tls-cipher` option is only used with TLSv1.2. When a TLSv1.3 
connection is established it is ignored. TLSv1.3 has a limited selection of 
algorithms that are all secure, no need to put any restriction on it.

**NOTE**: vpn-user-portal >= 2.3.4 and vpn-server-node >= 2.2.4 add support for 
the `ECDSA` TLS cipher `TLS-ECDHE-ECDSA-WITH-AES-256-GCM-SHA384` to support 
ECDSA certificates on TLSv1.2 connections. It was already supported when a 
TLSv1.3 connection was used.

### TLS Crypt

Starting from vpn-server-api 2.1.1 there no longer is a "global" `tls-crypt` 
key that is the same for all profiles. From this version on all new 
installations will use a `tls-crypt` key per profile. 

**NOTE**: if you already installed your VPN server before the release of 
vpn-server-api 2.1.1 you will continue to use the same `tls-crypt` key for all
profiles. If you want to switch to using one key per profile you need to 
delete `/var/lib/vpn-server-api/ta.key`.

To apply the configuration changes:

    $ sudo vpn-maint-apply-changes

If the command is not available, install the `vpn-maint-scripts` package first.

Please be aware that existing clients will need to fetch a new configuration, 
unless the eduVPN or Let's Connect! apps are used where that will happen 
automatically.

## PHP

CentOS 7 by default provides PHP 5.4. This is not without risks. This version 
is no longer maintained by the PHP project and depends fully on the Red Hat 
engineers that update it when (security) issues appear.

See the `resources/` directory for PHP setting changes.

### Sessions

We use [fkooman/secookie](https://git.sr.ht/~fkooman/php-secookie), a 
library to implement secure PHP sessions (and cookies).

## OAuth

The built-in [OAuth server](https://git.sr.ht/~fkooman/php-oauth2-server) 
uses public key cryptography signed JWT Bearer tokens of the type `EdDSA` 
implemented in [php-jwt](https://git.sr.ht/~fkooman/php-jwt). The `EdDSA` 
JWT token in specified in [RFC 8037](https://tools.ietf.org/html/rfc8037).

The reason we are using public key cryptography for the Bearer tokens is that 
no "back channel" is needed between the services verifying the token and 
issuing the token. This is especially helpful in the case of 
[Guest Usage](GUEST_USAGE.md).

## CA

The CA of the VPN service is "online" as it needs to generate valid 
certificates on the fly. The [vpn-ca](https://git.sr.ht/~fkooman/vpn-ca) 
software is used as CA.

By default the CA uses `RSA` with keys of length 3072 bits, and signs using 
`RSA-SHA256`.

The CA also supports `ECDSA` with the NIST P-256 curve, also known as 
secp256r1 or prime256v1, and `EdDSA` with `Ed25519`. Refer to the next section
to see what is possible.

Currently, RSA is the default. Future versions of the VPN software will switch
to `EdDSA` and drop TLSv1.2 support.

### TLS Algorithm Support

From the point of view of the VPN server the following tables can help to 
figure out which algorithms are supported.

| OS        | TLS              |
| --------- | ---------------- |
| CentOS 7  | TLSv1.2          |
| Fedora    | TLSv1.2, TLSv1.3 |
| Debian 9  | TLSv1.2          | 
| Debian 10 | TLSv1.2, TLSv1.3 |

Whenever possible, the client/server will use the highest TLS version. As for 
which types of keys are supported by the VPN server:

| CA    | CentOS 7 | Fedora | Debian 9 | Debian 10 |
|-------|--------- | ------ | -------- | --------- |
| RSA   | Y        | Y      | Y        | Y         |
| ECDSA | Y        | Y      | Y        | Y         |
| EdDSA | N        | Y      | N        | Y         |

The client plays an important role here. In order to support `EdDSA` the client 
MUST support TLSv1.3, *and* support storing `EdDSA` keys in its key store.

When using TLSv1.2, the server *and* client `tls-cipher` option are consulted,
this option is ignored when using TLSv1.3. When introducing `ECDSA` support, we 
had to add an additional `tls-cipher` just for the TLSv1.2 case to both the 
client and server OpenVPN configuration, otherwise only `RSA` was allowed. As 
only TLSv1.3 supports `EdDSA`, we did not need to modify anything for this 
scenario, but using `EdDSA` is restricted to "modern" VPN servers. Only servers
(and clients) using OpenSSL >= 1.1.1 support TLSv1.3 (and `EdDSA`).

**NOTE** in order to support `ECDSA` on CentOS 7 and Debian 9 you need to run
vpn-user-portal >= 2.3.4 and vpn-server-node >= 2.2.4 on your server.

### Switching Key Type

Switching to another key type from RSA is easy. Modify 
`/etc/vpn-server-api/config.php` and set the `vpnCaKeyType` option, as an 
example we switch to ECDSA:

```
<?php

return [
    //'vpnCaKeyType' => 'RSA',
    'vpnCaKeyType' => 'ECDSA',
    //'vpnCaKeyType' => 'EdDSA',
    
    'vpnProfiles' => [
        // ...
```

Now, you need to "reset" your VPN server, which is easy:

	$ sudo vpn-maint-reset-system

This will re-initialize the VPN server and bring it back to "defaults", it will
remove all data, but not the configuration. 

**NOTE**: if you are using the default username/password authentication module, 
all users will be lost on "reset" and you need to add them again using 
`vpn-user-portal-add-user`, e.g.:

```
$ sudo vpn-user-portal-add-user
```
