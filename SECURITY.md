**Work in Progress**

# Security

This document contains information about the security of the software, more 
specifically the specific configuration choices that were made.

## OpenVPN

### Crypto

    tls-version-min 1.2
    tls-cipher TLS-ECDHE-RSA-WITH-AES-256-GCM-SHA384
    auth SHA256
    # NCP may override this
    cipher AES-256-CBC
    # use ECDHE only
    dh none

## PHP

The software, by default, when using the `deploy.sh` script uses PHP 5.4. This
is not without risks. That version is no longer maintained by the PHP project
and depends fully on the Red Hat engineers that update it when (security) 
issues appear.

A number of issues have been identified and workarounds provided:

- PHP 5.4 does not have a (secure) CSPRNG, so we use 
  [pecl-libsodium](https://paragonie.com/book/pecl-libsodium) instead;

See the `resources/` directory for PHP setting changes.

### Sessions

We use [fkooman/secookie](https://github.com/fkooman/php-secookie), a library
to implement secure PHP sessions (and cookies).

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
