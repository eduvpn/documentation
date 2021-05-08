---
title: APIv3
description: API Documentation for (Native) Application Developers
category: dev
---

**NOTE**: WORK IN PROGRESS AS OF 2021-05-08

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
in draft. If the application implemented OAuth for [APIv2](API.md) it will also
work as-is with APIv3. 

The _only_ difference is that refresh tokens are now single use. When using a
refresh token, the response includes also a _new_ refresh token. Should a 
refresh token be used multiple times, the whole authorization is revoked and
the client will need to reauthorize.

From my rudimentary tests, it seems all existing eduVPN/Let's Connect! clients 
are handling this properly, but it can't hurt to make sure...

# Endpoint Discovery

A "well-known" URL is provided to figure out the OAuth and API endpoint one
has to use. The document can be retrieved from `/info.json`, e.g.:

```json
{
  "api": {
    "http://eduvpn.org/api#3": {
      "api_endpoint": "https://vpn.example.org/vpn-user-portal/api.php/v3",
      "authorization_endpoint": "https://vpn.example.org/vpn-user-portal/_oauth/authorize",
      "token_endpoint": "https://vpn.example.org/vpn-user-portal/oauth.php/token"
    }
  },
  "v": "3.0.0-1.fc34"
}
```

Servers that provide the `http://eduvpn.org/api#3` key under `api`, support
this API (and WireGuard).

When fetching this document, _redirects_, e.g. `301`, `302`, `303`, MUST be 
followed.

## Endpoint Location

Currently we support both `/info.json` and `/.well-known/vpn-user-portal` in 
eduVPN/Let's Connect! 2.x. It would be nice to phase out `/info.json`.

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
    https://vpn.example.org/vpn-user-portal/api.php/v3/info
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
                "profile_id": "employees"
            },
            {
                "display_name": "Administrators",
                "profile_id": "admins"
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
    "https://vpn.example.org/vpn-user-portal/api.php/v3/connect"
```

### Response

If the profile is an OpenVPN profile you'll get the complete OpenVPN client
configuration with `Content-Type: application/x-openvpn-profile`, e.g.:

```
X-Vpn-Connection-Id: 54251e7c9601f38fab88744f4786b76f
Expires: Fri, 06 Aug 2021 03:59:59 GMT
Content-Type: application/x-openvpn-profile

# OpenVPN Client Configuration
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
MIIBQzCB9qADAgECAhBo5To7i6Tlbak616ixNkNjMAUGAytlcDARMQ8wDQYDVQQD
EwZWUE4gQ0EwHhcNMjEwNDI5MDk1MDAyWhcNMzEwNDI5MDk1NTAyWjARMQ8wDQYD
VQQDEwZWUE4gQ0EwKjAFBgMrZXADIQBONDYoafRXDO01zL9vUjbj46g1+5FXh8uX
rMZvX3MCIKNkMGIwDgYDVR0PAQH/BAQDAgKEMB0GA1UdJQQWMBQGCCsGAQUFBwMB
BggrBgEFBQcDAjASBgNVHRMBAf8ECDAGAQH/AgEAMB0GA1UdDgQWBBTUyHw5S0sG
boplw33QDLaLf66gBDAFBgMrZXADQQCfvYY9CYKxMYC6ujoZrysLWVeG5Ay9ZD2o
RJ1hHQHVU3rq/ATpiMOKRmbGy+u+TJH5DFMywJ8D8SEqSrI8+rkN
-----END CERTIFICATE-----
</ca>
<tls-crypt>
#
# 2048 bit OpenVPN static key
#
-----BEGIN OpenVPN Static key V1-----
696fec0fef444105a153448d00f28dce
243928a480cbac07e98c36398c980d13
bbfd600e91fdcd8cfb416baf2a357a7b
b73d5d6595e84d29a55045a4d4d84714
c6a40d7b5a646557a927c6058b17a272
77f111f602aa29933cdba70a59cc9759
0eb851c8f1dcc25807a2251a0546aff5
6eef04dc804243d5790d9b23a79b20a9
b01faa33c0f03953ee6cb418c545bacf
1b8af0c6b49d4bf1b4bcc0a0db5fc3cd
f4d9675ff7a9fefa1e9e25e992b7d66a
ff6d903a9e426ded4b8ce5a3a530e483
f9ee774f99216d0201240f238561ebe2
47cd388a5d1e589945628e0abcf26a1e
c0be30f0f2cfc480f9b55ce670231db9
c90a590cde36ef810a228a192386658d
-----END OpenVPN Static key V1-----
</tls-crypt>
<cert>
-----BEGIN CERTIFICATE-----
MIIBYzCCARWgAwIBAgIRAJe+VDNu0cWrvYqvpi3S1pwwBQYDK2VwMBExDzANBgNV
BAMTBlZQTiBDQTAeFw0yMTA1MDgwOTQwNDBaFw0yMTA4MDYwMTU5NTlaMD0xEDAO
BgNVBAsTB2RlZmF1bHQxKTAnBgNVBAMTIDU0MjUxZTdjOTYwMWYzOGZhYjg4NzQ0
ZjQ3ODZiNzZmMCowBQYDK2VwAyEANtm0hHuT97mwe/VELSB3G+0145ZZhHw/g+Af
OlxJz9ujVjBUMA4GA1UdDwEB/wQEAwIHgDATBgNVHSUEDDAKBggrBgEFBQcDAjAM
BgNVHRMBAf8EAjAAMB8GA1UdIwQYMBaAFNTIfDlLSwZuimXDfdAMtot/rqAEMAUG
AytlcANBAA6tQFgH4NLkgD7SCa3gttpLB7HAKpTZFZwduLw+tOxR1b4jdUY9Caai
8brsE/LqFzafeCw+kgQyGX2Hnd+jWw0=
-----END CERTIFICATE-----
</cert>
<key>
-----BEGIN PRIVATE KEY-----
MC4CAQAwBQYDK2VwBCIEIBh7ZHKGCSVnJne7BTaiB8YSUQXhHcAAR80zJm+zXVlT
-----END PRIVATE KEY-----
</key>
remote vpn.example 1194 udp
remote vpn.example 1194 tcp
```

If the profile is an WireGuard profile you'll get the complete WireGuard client
configuration with `Content-Type: application/x-wireguard-profile`, e.g.:

```
X-Vpn-Connection-Id: KgW+5T/6dwH24VYmOVvvlYLOTjWXijWzm+RXKjKdrGU=
Expires: Fri, 06 Aug 2021 03:59:59 GMT
Content-Type: application/x-wireguard-profile

[Interface]
PrivateKey = +BaCmdzp/55FXY3XrZ2jGL6E1ihHM0vwJiD6XyHKPk4=
Address = 10.10.10.12/24, fd00:1234:1234:1234::a0a:a0c/64
DNS = 9.9.9.9, 2620:fe::fe

[Peer]
PublicKey = Gwcpqv5WeCI3XotETskDXQLfYQk0fi8gEpuCQVIoKGc=
AllowedIPs = 0.0.0.0/0, ::/0
Endpoint = vpn.example:51820
PersistentKeepalive = 25
```

You can use the `Expires` response header value to figure out how long the VPN 
session will be valid without calling `/disconnect`.

The `X-Vpn-Connection-Id` header value MUST be used when calling `/disconnect`,
see below. This in order to make sure the correct connection is cleaned up 
properly.
 
## Disconnect

The `/disconnect` call is necessary in order to free up resources on the 
server. This is mainly the case with WireGuard where there is no concept of IP 
management in WireGuard itself, so we have to do this ourselves in order to 
work with limited IP space when e.g. using public IPv4 addresses.

**NOTE**: this would be completely irrelevant when only using private IP space,
e.g. RFC 1918. In that case we would simply bind a public key to an IP address
in the `10/8` prefix and never change it. But because we do not have this 
luxury (yet?) this is not possible...

### Request

The `connection_id` is the value obtained from the `/connect` call response 
header `X-Vpn-Connection-Id`.

```bash
$ curl --data-urlencode "connection_id=KgW+5T/6dwH24VYmOVvvlYLOTjWXijWzm+RXKjKdrGU=" -H "Authorization: Bearer abcdefgh" \
    "https://vpn.example.org/vpn-user-portal/api.php/v3/disconnect"
```

### Response

The response will be `204 No Content` if all goes well.

# Notes

- we should probably rename the `/connect` and `/disconnect` calls to `/setup` 
  and `/teardown` or `/register` / `/unregister` or something like this, as 
  there is no actual connection taking place...
- as long as the OAuth token works, the client configuration works, there is no
  need to ask the server whether a certificate is (still) valid
- i am not sure it is good idea to generate new keys on every call to 
  `/connect`, that seems inefficient, BUT it is very cheap when using Ed25519 
  which we do for eduVPN 3.x
- we MAY support a `public_key` field on `/connect` for WireGuard profiles to 
  allow the client to use a locally generated key. This may actually be a good
  idea! Then we have to reintroduce `vpn_type` again I guess so the client 
  knows it is a WireGuard profile... APIv3.1?
- As long as you don't call `/disconnect` the obtained configuration will 
  remain valid as long as it doesn't expire (sessionExpiry)
- The certificate/public key will expire exactly at the moment the OAuth 
  refresh and access token no longer work
- when the computer goes to sleep you can just try to reconnect with the 
  previously obtained configuration, no need to use the API, BUT if connecting
  doesn't work go back to the API
- we need a flow diagram...
