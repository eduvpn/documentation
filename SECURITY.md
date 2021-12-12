# Security

This document contains some information about the security of the software, 
more specifically: the configuration choices that were made.

## Web Server

By default [Apache](https://httpd.apache.org/) is used. 

### Debian

TBD.

### Fedora

TBD. Look into "Crypto Policies" on Fedora/CentOS.

## OpenVPN

The basic OpenVPN server (and client) cryptography configuration:

* Minimum TLS version (`--tls-version-min`) >= 1.3;
* Data ciphers (`--data-ciphers`) `AES-256-GCM` and `CHACHA20-POLY1305`;
* TLS crypt (`--tls-crypt`) as a DoS prevention "firewall" when this shared key
  is not known by an attacker.

The server supports two data ciphers allowing the client to choose one of 
those. If the server supports hardware accelerated AES, `AES-256-GCM` is 
preferred, otherwise `CHACHA20-POLY1305`.
                        
There's no need to configure specific TLS ciphers, as all ciphers defined in
the TLSv1.3 specification are secure to use.

## WireGuard

There are no configuration toggles regarding security properties, except 
_preshared keys_ which is currently NOT used.

## Sessions

We use [fkooman/secookie](https://git.sr.ht/~fkooman/php-secookie), a 
library to implement secure PHP sessions (and cookies).

## OAuth

We use [fkooman/oauth2-server](https://git.sr.ht/~fkooman/php-oauth2-server), 
a library to implement a secure OAuth 2.1 server.

It uses public key signatures to sign/verify the issues OAuth 
[tokens](https://git.sr.ht/~fkooman/php-oauth2-server/tree/v7/item/TOKEN_FORMAT.md).

## CA

The CA of the VPN service is "online" as it needs to generate valid 
keys/certificates on the fly. The [vpn-ca](https://git.sr.ht/~fkooman/vpn-ca) 
software is used as CA.

Only `EdDSA` keys are supported.

## SSH

By default we do NOT modify the SSH configuration itself, however we do 
configure the firewall to allow SSH access from everywhere, including VPN 
clients.

You SHOULD change/update this! Look [here](FIREWALL.md#restricting-ssh-access).
