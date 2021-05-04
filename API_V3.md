---
title: APIv3
description: API Documentation for (Native) Application Developers
category: dev
---

**NOTE**: WORK IN PROGRESS AS OF 2021-05-04

This document describes the API provided by all eduVPN/Let's Connect! servers.
The API is intended to be used by the eduVPN and Let's Connect! applications.

The API can be used to obtain a list of supported VPN _profiles_ on the server,
and download a VPN client configuration for a particular profile.

# Instance Discovery

This document assumes you already know which server you want to connect to, by
its FQDN, e.g. `vpn.example.org`. 

We also provide documentation on how to implement "discovery" for the eduVPN 
branded application [here](SERVER_DISCOVERY.md).

# Standards

The VPN servers provide an API protected with 
[OAuth 2.1](https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/), currently 
in draft. If the application implemented [APIv2](API.md) it will also
work with APIv3.

# Endpoint Discovery

A "well-known" URL is provided to figure out the OAuth and API endpoint one 
has to use. The document can be retrieved from `/.well-known/vpn-user-portal`, 
e.g.:

```json
{
  "api": {
    "http://eduvpn.org/api#3": {
      "api_endpoint": "https://vpn.example.org/vpn-user-portal/api/v3",
      "authorization_endpoint": "https://vpn.example.org/vpn-user-portal/oauth/authorize",
      "token_endpoint": "https://vpn.example.org/vpn-user-portal/oauth/token"
    }
  },
  "v": "3.0.0-0.75.fc34"
}
```

When fetching this document, _redirects_, e.g. `301`, `302`, `303`, MUST be 
followed.

**NOTE**: this used to be the `/info` endpoint. We MAY still change the 
endpoint to something like `/.well-known/org.eduvpn.api`.

# Authorization Endpoint

The `authorization_endpoint` is used to obtain an authorization code through an
"Authorization Request". All query parameters as defined by the OAuth 
specification are required, even optional ones: 

- `client_id`;
- `redirect_uri`;
- `response_type`: MUST be `code`;
- `scope`: MUST be `config`;
- `state`;
- `code_challenge_method`: MUST be `S256`; 
- `code_challenge`.

Please follow the OAuth specification, or use a library for your platform that
implements OAuth 2.1. 

The `authorization_endpoint` with its parameters set MUST be opened in the 
platform's default browser. The `redirect_uri` parameter MUST point back to 
a location the application can intercept.

All error conditions MUST be handled according to the OAuth specification(s).

# Token Endpoint

The `token_endpoint` is used to exchange the authorization code, as obtained
through the `redirect_uri` as part of the authorization, for an access and 
refresh token. It is also used to retrieve new access tokens when the current 
access token expires.

All error conditions MUST be handled according to the OAuth specification(s).

# Using the API

The API is kept as simple as possible, and a considerable simplication from
the [APIv2](API.md). Every API call below will include a cURL example, and the
response that can be expected.

All `POST` requests MUST be sent encoded as 
`application/x-www-form-urlencoded`.

The API can be used with the access token obtained using the OAuth flow as 
documented above. The following API calls are available:

- Get "Info" from the VPN server, including a list of available profiles 
  (`/info`);
- "Connect" to a VPN profile (`/connect`);
- "Disconnect" from a VPN profile (`/disconnect`);

# API Calls

## Info

This call will show the available VPN profiles for this instance. This will 
allow the application to show the user which profiles are available.

### Request

```bash
$ curl -H "Authorization: Bearer abcdefgh" \
    https://vpn.example.org/vpn-user-portal/api/v3/info
```

### Response

```json
{
    "info": {
        "profile_list": [
            {
                "display_name": {
                    "en": "Employees",
                    "nl": "Medewerkers"
                },
                "profile_id": "employees",
                "vpn_type": "openvpn"
            },
            {
                "display_name": "Administrators",
                "profile_id": "admins",
                "vpn_type": "wireguard"
            }
        ]
    }
}
```

**TODO**: mention the `display_name` field can be either a string, or an object
with BCP47 language codes as key.

## Connect

Get the profile configuration for the profile you want to connect to.

### Request

```bash
$ curl -d "profile_id=employees" -H "Authorization: Bearer abcdefgh" \
    "https://vpn.example.org/vpn-user-portal/api/v3/connect"
```

### Response

If the profile is an OpenVPN profile you'll get the complete OpenVPN client
configuration with `Content-Type: application/x-openvpn-profile`, e.g.:

```
dev tun
client
nobind
remote-cert-tls server
verb 3
server-poll-timeout 10
tls-version-min 1.3
data-ciphers AES-256-GCM
reneg-sec 0
<ca>
-----BEGIN CERTIFICATE-----
MIIBRDCB96ADAgECAhEAj8Qvi/o+rgDsjHFbFsgWSjAFBgMrZXAwETEPMA0GA1UE
AxMGVlBOIENBMB4XDTIxMDQyOTA5MzkzNVoXDTMxMDQyOTA5NDQzNVowETEPMA0G
A1UEAxMGVlBOIENBMCowBQYDK2VwAyEAszmmBhVeMVEhu5ZodvhcfyMbF2IRQ3zI
FNCLzKDcljWjZDBiMA4GA1UdDwEB/wQEAwIChDAdBgNVHSUEFjAUBggrBgEFBQcD
AQYIKwYBBQUHAwIwEgYDVR0TAQH/BAgwBgEB/wIBADAdBgNVHQ4EFgQUDJSRwh1Q
1b5rvp6ikk7DzCy4zp0wBQYDK2VwA0EAu28CZxjoGeVX+xLiWwkGMW4QqPI5GkTG
HLR87eg7lHRBEX2C2qYQ00Ssd9pIdL4x5fOb2Z7APRQV7REyjb04Aw==
-----END CERTIFICATE-----
</ca>
<tls-crypt>
#
# 2048 bit OpenVPN static key
#
-----BEGIN OpenVPN Static key V1-----
93552466d1be60184adc39647b3d6bdf
a8a09702dfc85da97af6c1880b473397
22ba7e85774bf1fa4297611e3a45d603
82f4134e5868cf9c14c109cc24379c99
4f097a48211f8a7366270c90ab6f7b03
987b89b533551d4cc2a47196846489ad
20d9e9c231476f6e7daeee2695a362eb
c02a8dfae60e6ba886151b280242a599
fcd6332bb26eeb83744a2aa90c7e2127
944615855494b706d71c68241349c404
8bde489886c56894c321371c16dd0b7e
342f17f8307d21b48f3e9df96f53ff62
9d21d5b3af73273a7af5bdc4ff712333
6f4f67fd7b9da44539f3229d067405ae
7acbebbf91d9982ae9130d5cc5598072
569b6637f7984e378358fe80fd1b313f
-----END OpenVPN Static key V1-----
</tls-crypt>
<cert>
-----BEGIN CERTIFICATE-----
MIIBUDCCAQKgAwIBAgIQci4N0pS9xjEc+0bdQtKN0DAFBgMrZXAwETEPMA0GA1UE
AxMGVlBOIENBMB4XDTIxMDUwNDE3NTkyOFoXDTIxMDgwMjAyMDAwMFowKzEpMCcG
A1UEAxMgYjAxYTkxMjA1MTQzZjY3Mzk3ZTQxMjJiMzYyYTI0MjMwKjAFBgMrZXAD
IQDXbjUnU4QAtbOTzr4q9c1x193pxkN0RKcU3ObxowrycaNWMFQwDgYDVR0PAQH/
BAQDAgeAMBMGA1UdJQQMMAoGCCsGAQUFBwMCMAwGA1UdEwEB/wQCMAAwHwYDVR0j
BBgwFoAUDJSRwh1Q1b5rvp6ikk7DzCy4zp0wBQYDK2VwA0EAUDxGrjIDVAN/vJLB
qQKYY23ss1/DzX++yNKZ9aLgdocTnUoTnKRbB122qLIZ7efuW1WPCWWKGRgesp6X
0NTLAw==
-----END CERTIFICATE-----
</cert>
<key>
-----BEGIN PRIVATE KEY-----
MC4CAQAwBQYDK2VwBCIEIJYfYOeDrJ46U2Q4uZQ9NUUymTqYrZfc1FRYabQUDx1x
-----END PRIVATE KEY-----
</key>
remote vpn.example.org 1194 udp
remote vpn.example.org 1194 tcp
```

If the profile is an WireGuard profile you'll get the complete WireGuard client
configuration with `Content-Type: application/x-wireguard-profile`, e.g.:

```
[Peer]
PublicKey = 2obnZaov/Idd1zHFZqziWurRubx98ldKmDH44nB7nF0=
AllowedIPs = 0.0.0.0/0, ::/0
Endpoint = vpn.example.org:51820

[Interface]
Address = 10.10.10.5/24, fd00:1234:1234:1234::5/64
DNS = 9.9.9.9, 2620:fe::fe    
PrivateKey = IE5RrlVJSN+/soFhmd/hZDST/bVu8voNk9mq1u6IQWI=
```

## Disconnect

### Request

```bash
$ curl -d "profile_id=employees" -H "Authorization: Bearer abcdefgh" \
    "https://vpn.example.org/vpn-user-portal/api/v3/disconnect"
```

### Response

The response will be `204 No Content` if all goes well.

# Notes

- as long as the OAuth token works, the client configuration works, there is no
  need to ask the server whether a certificate is (still) valid
- i am not sure it is good idea to generate new keys on every call to 
  `/connect`, that seems inefficient, BUT it is very cheap when using Ed25519 
  which we do for eduVPN 3.x
- we MAY supprot a `public_key` field on `/connect` for WireGuard profiles to 
  allow the client to use a locally generated key. This may actually be a good
  idea!
- As long as you don't call `/disconnect` the obtained configuration will 
  remain valid as long as it doesn't expire (sessionExpiry)
- when the computer goes to sleep you can just try to reconnect with the 
  previously obtained configuration, no need to use the API, BUT if connecting
  doesn't work go back to the API
- we need a flow diagram...
