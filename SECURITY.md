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
