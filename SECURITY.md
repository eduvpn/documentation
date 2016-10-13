This document contains information about the security of the software, more 
specifically the specific configuration choices that were made.

# DH

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

This file is part of the `vpn-server-api` project and stored in the `config` 
directory. If you want to generate your own DH parameters, you can do so 
using the above command and store the file in `/etc/vpn-server-api/dh.pem`.

Make sure to regenerate (all) server configurations, or manually copy the 
`dh.pem` to `/etc/openvpn/tls/<instance>/<pool>/dh.pem` for all your pools
and configurations.

# Crypto

    tls-version-min 1.2
    tls-cipher TLS-DHE-RSA-WITH-AES-128-GCM-SHA256:TLS-DHE-RSA-WITH-AES-256-GCM-SHA384:TLS-DHE-RSA-WITH-AES-256-CBC-SHA
    auth SHA256
    cipher AES-256-CBC

# PHP

The software, by default, when using the `deploy.sh` script uses PHP 5.4. This
is not without risks. That version is no longer maintained by the PHP project
and depends fully on the Red Hat engineers that update it when (security) 
issues appear.

A number of issues have been identified and workarounds provided:

- missing `random_int` and `random_bytes` that were introduced in PHP 7;
- [session fixation](https://en.wikipedia.org/wiki/Session_fixation) for which 
  a workaround exists;

The configuration updates we made to PHP are all listed 
[here](resources/99-eduvpn.ini).

## Random

For providing random numbers we use the PHP 5.x polyfill 
[paragonie/random_compat](https://github.com/paragonie/random_compat), this 
comes with an additional warning as we really do NOT want to use the OpenSSL 
fallback as that is considered insecure for generating (crypto) random numbers.

The polyfill will try first libsodium and if that is missing it will fallback 
to `/dev/urandom` which is alright. We just have to make really sure that 
`/dev/urandom` is available to PHP.

## Sessions

In PHP >= 5.5.2 there is a way to prevent session fixation. There is a PHP 
[option](https://secure.php.net/manual/en/session.configuration.php#ini.session.use-strict-mode)
for this. Unfortunately we need to support PHP 5.4, so we have to implement a
[workaround](https://paragonie.com/blog/2015/04/fast-track-safe-and-secure-php-sessions).
