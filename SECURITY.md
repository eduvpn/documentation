**WIP**

# Security

This document contains information about the security of the software, more 
specifically the specific configuration choices that were made.

## OpenVPN

### Crypto

    tls-version-min 1.2
    tls-cipher TLS-ECDHE-RSA-WITH-AES-256-GCM-SHA384:TLS-ECDHE-ECDSA-WITH-AES-256-GCM-SHA384:TLS-ECDHE-RSA-WITH-AES-256-CBC-SHA384:TLS-ECDHE-ECDSA-WITH-AES-256-CBC-SHA384:TLS-DHE-RSA-WITH-AES-256-GCM-SHA384:TLS-DHE-RSA-WITH-AES-128-GCM-SHA256
    auth SHA256
    cipher AES-256-CBC

### Diffie-Hellman

We use a hard coded DH parameter file generated using OpenSSL running on 
Fedora 24, specifically `openssl-1.0.2j-1.fc24.x86_64`.

    $ openssl dhparam 4096 > dh.pem

The output is this key:

```
-----BEGIN DH PARAMETERS-----
MIICCAKCAgEAiH9x4TPTKSDDYqOouVruHvlCiIDrqr/AoJ0IpWvolCCCS7pojkpO
8Shx+hCOcHOjsgJrHvPEg40qC6g2dCIdwcLwmmPjopszEzHgzwxIZMDm7wylkRAf
uYHSfDtEWMDAX3f0q+TMJLQv8NRtu4fjEkXU3p5JVNGAQhEPWt1gYrlbJwkaf0Bo
jutzb+IJJwSRpVwHrKE9M6dN5CE/fhwICSqRjFxjYQGKKnq1rJ6lYHnsnAmDR3J1
FWwZtknYFK4MElFJIESoFHw5CVnb92vN8k5EpGc2WtBJewYr6EspvnDeCHaPVDat
oOZSYjO/i1B2j2ALQTqyAQIgi7YOhhLfLIFVlzNLMRhLuJNcPJbo4gz8CrzkuCpq
czuTz1U9bL+aY9e3wFT/M+4YlkjdkcYoaRMfGzfgfdojdVogy59/c5t/ciWIgumA
78PzUyYNZ3im7F9On+C64SZDrEbmoZwfsqOfY1JFjIZXvhbw8FeyByk1bXwg9aA8
USav1aeleUQtoyXXKYHBTclsJKYrSDqMe0qhmqdsiQ34PsEQi19Qk5zUHBN4Z8+x
2MUE4oCpMALGhRbfz7gj3AF3EGKqgz7dBWRdpcZsM1Fd8Olj456egwxvFLxnlERo
NdWOSJxYsvki1w9JePcg39nImSi9jLpSp/3c1XrWsby7RdN8zgbZOSsCAQI=
-----END DH PARAMETERS-----
```

This file is part of the `vpn-server-node` project and stored in the `config` 
directory. If you want to generate your own DH parameters, you can do so 
using the above command and store the file in `/etc/vpn-server-node/dh.pem`.

Make sure to regenerate (all) server configurations, or manually copy the 
`dh.pem` to `/etc/openvpn/server/tls/<instance>/<profile>/dh.pem` for all your 
profiles and configurations.

## PHP

The software, by default, when using the `deploy.sh` script uses PHP 5.4. This
is not without risks. That version is no longer maintained by the PHP project
and depends fully on the Red Hat engineers that update it when (security) 
issues appear.

A number of issues have been identified and workarounds provided:

- PHP 5.4 does not have a CSPRNG, so we use 
  [pecl-libsodium](https://paragonie.com/book/pecl-libsodium) instead;
- [session fixation](https://en.wikipedia.org/wiki/Session_fixation) for which 
  a workaround exists that is implemented;

The configuration updates we made to PHP are all listed 
[here](resources/99-eduvpn.ini).

### Sessions

In PHP >= 5.5.2 there is a way to prevent session fixation. There is a PHP 
[option](https://secure.php.net/manual/en/session.configuration.php#ini.session.use-strict-mode)
for this. Unfortunately we need to support PHP 5.4, so we have to implement a
[workaround](https://paragonie.com/blog/2015/04/fast-track-safe-and-secure-php-sessions).

## Threat Model

We will consider the following scenarios:

1. A user uses the VPN to safely use the Internet;
2. An organization uses the VPN to allow employees to access the internal 
   resources;

The main purpose of scenario 1 is to avoid being MITMed, e.g. to prevent 
JavaScript injection in an attempt to exploit the web browser, or avoid 
surveillance. An attack that would make either possible basically makes the 
VPN useless, or even more dangerous than not using the VPN in the first place.

There are a number of attacks that could result in this MITM:

1. The VPN server itself is compromised allowing the attacker to snoop all 
   traffic and modify it;
2. The CA is compromised, allowing creation of valid VPN server certificates;
3. The "upstream" ISP running the VPN service is compromised and under 
   surveillance;

### Server Compromise

TBD.

#### Recovery

TBD.

### CA 

Because of the nature of the VPN service, the CA needs to be "online", i.e. it 
should be able to sign certificates on demand. There are a number of 
countermeasures that could be taken to avoid compromising the CA by using e.g. 
a hardware HSM that contains the CA. This is currently not done because that 
actually is quite complicated in a (managed) VM platform.

It would be very interesting to investigate if it is possible to have a 
separate CA for signing the client certificates and a different one for server 
certificates so that generating server certificates requires an offline CA. 

However, if a VPN server certificate is stolen it can be used to intercept 
client connections by hijacking DNS.

#### Recovery

In order to recover, the entire CA needs to be regenerated including all 
client and server certificates.

### Compromised ISP

This is out of scope of this threat model, but is mentioned anyway for 
completeness.
