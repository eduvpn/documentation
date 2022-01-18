# Introduction

This document describes the version 3 API provided by a future version of the 
eduVPN/Let's Connect! servers. The API is intended to be used by the eduVPN and 
Let's Connect! applications and uses OAuth 2 for authorization.

The API can be used to obtain server information, prepare for a connection and 
clean up a connection. 

# Changes

The changes made to the API documentation before it is final.

| Date       | Change                                                                                                          |
| ---------- | --------------------------------------------------------------------------------------------------------------- |
| 2021-08-04 | Allow client to specify supported VPN protocols on `/info` call using the `X-Proto-Support` HTTP request header |
| 2021-09-01 | The `vpn_proto` field was added to the `/info` response                                                         |
|            | The `tcp_only` POST parameter was added for OpenVPN profiles                                                    |
|            | The `public_key` POST parameter is now only required for WireGuard profiles                                     |
|            | Remove the `X-Proto-Support` header again now that we have `vpn_proto` in `/info` response                      |
| 2021-09-02 | Add "Error Responses" section                                                                                   |
| 2021-09-20 | Restored the `default_gateway` bool as needed by the NetworkManager client on Linux                             |
| 2021-10-13 | Remove all references to `/info.json`, MUST use `/.well-known/vpn-user-portal` from now on                      |
| 2021-10-27 | Mention following redirects MUST only allow redirecting to `https://`                                           |
| 2021-11-01 | Allow specifying the protocol to use on the `/connect` call                                                     |
|            | The `vpn_proto` field was in the `/info` response and is of type string array                                   |
| 2021-11-02 | Document [VPN Protocol Selection](#vpn-protocol-selection) for clients                                          |
| 2021-11-04 | Update the `/info` response fields, rewrite "VPN Protocol Selection" section                                    |
| 2022-01-05 | The `vpn_proto` POST parameter was removed and `/connect` call simplified, the server will always decide based  |
|            | on the provided parameters, i.e. `public_key` and `tcp_only` and the supported protocols by the profile...      |
| 2022-01-06 | The `profile_id` parameter on the `/disconnect` call is never used, no point in having the client send it, so   |
|            | the need to send this has been removed                                                                          |
| 2022-01-18 | Rename `tcp_only` to `prefer_tcp` and switch to `yes` and `no` values instead of `on` and `off`                 |

# Instance Discovery

This document assumes you already know which server you want to connect to, by
its FQDN, e.g. `vpn.example.org`. 

We also provide documentation on how to implement "discovery" for the eduVPN 
branded application [here](SERVER_DISCOVERY.md).

# Standards

The VPN servers provide an API protected with 
[OAuth 2.1](https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/), currently 
in draft. If the application implemented the [APIv2](API.md), it will also
work as-is with APIv3. 

The _only_ difference in the OAuth implementation between APIv2 and APIv3 is 
that refresh tokens are now single use. When using a refresh token, the 
response includes also a _new_ refresh token. Should a refresh token be used 
multiple times, the whole authorization is revoked and the client will need to 
reauthorize.

After some rudimentary tests, it seems all existing eduVPN/Let's Connect! 
clients are handling this properly.

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
    "v": "3.0.0-1.fc34"
}
```

Servers that provide the `http://eduvpn.org/api#3` key under `api`, support
this API.

This file MUST be freshly retrieved before all attempts to connect to a server 
to make sure any updates to this file are discovered.

**NOTE**: eduVPN/Let's Connect! 2.x servers also already support the 
`/.well-known/vpn-user-portal` endpoint, so there is no need to still retrieve
`/info.json`.

## Endpoint Location

When fetching this document, _redirects_, e.g. `301`, `302`, `303`, MUST be 
followed, but MUST NOT allow redirect to anything else than other `https://` 
URLs, e.g. redirects to `http://` MUST be rejected.

# Authorization Endpoint

The `authorization_endpoint` is used to obtain an authorization code through an
"Authorization Request". All query parameters as defined by the OAuth 
specification are required, even optional ones: 

- `client_id`;
- `redirect_uri` MUST be a support URL as found 
  [here](https://git.sr.ht/~fkooman/vpn-user-portal/tree/v3/item/src/OAuth/ClientDb.php);
- `response_type`: MUST be `code`;
- `scope`: MUST be `config`;
- `state`;
- `code_challenge_method`: MUST be `S256`; 
- `code_challenge`.

Please follow the OAuth specification, or use a library for your platform that
implements OAuth 2.1.

The `authorization_endpoint` with its parameters set MUST be opened in the 
platform's default browser or follow the platform's best practice dealing with
application authorization(s). The `redirect_uri` parameter MUST point back to 
a location the application can intercept.

All error conditions, both during the authorization phase AND when talking 
to the API endpoint MUST be handled according to the OAuth specification(s).

# Token Endpoint

The `token_endpoint` is used to exchange the authorization code, as obtained
through the `redirect_uri` as part of the authorization, for an access and 
refresh token. It is also used to retrieve new access tokens when the current 
access token expires.

All error conditions MUST be handled according to the OAuth specification(s).

# Using the API

The API is kept as simple as possible, and a considerable simplification of
the [APIv2](API.md). Every API call below will include a cURL example, and an
example response that can be expected.

All `POST` requests MUST be sent encoded as 
`application/x-www-form-urlencoded`.

The API can be used with the access token obtained using the OAuth flow as 
documented above. The following API calls are available:

- Get "Info" from the VPN server, including a list of available profiles 
  (`/info`);
- "Connect" to a VPN profile (`/connect`);
- "Disconnect" from a VPN profile (`/disconnect`)

# API Calls

## Info

This call will show the available VPN profiles for this instance. This will 
allow the application to show the user which profiles are available.

This `GET` call has no parameters.

### Request

Request all available VPN profiles:

```bash
$ curl \
    -H "Authorization: Bearer abcdefgh" \
    https://vpn.example.org/vpn-user-portal/api/v3/info
```

### Response

```
HTTP/1.1 200 OK
Content-Type: application/json

{
    "info": {
        "profile_list": [
            {
                "default_gateway": true,
                "display_name": {
                    "en": "Employees",
                    "nl": "Medewerkers"
                },
                "profile_id": "employees",
                "vpn_proto_list": [
                    "openvpn",
                    "wireguard"
                ],
                "vpn_proto_preferred": "wireguard"
            },
            {
                "default_gateway": false,
                "display_name": "Administrators",
                "profile_id": "admins",
                "vpn_proto_list": [
                    "wireguard"
                ],
                "vpn_proto_preferred": "wireguard"
            }
        ]
    }
}
```

The `default_gateway` field indicates whether the client is expected to
route all traffic over the VPN, or only a subset of it. It is either `true` or
`false`.

The `display_name` field can be either of type `string` or `object`. When the
field is an object, the keys are 
[BCP-47 language codes](https://en.wikipedia.org/wiki/IETF_language_tag). 

The `vpn_proto_list` field indicates which VPN protocol(s) are supported. If 
you client does not support any of the listed protocols, you can omit them, or 
mark them as unsupported. Currently `openvpn` and `wireguard` values are 
supported.

The `vpn_proto_preferred` is set by the server operator for a particular 
profile. This information MUST NOT be used by the VPN client.

## Connect

Get the profile configuration for the profile you want to connect to.

### Request

Connect to the "Employees" profile (`employees`) and specify a WireGuard public 
key for when WireGuard will be used:

```bash
$ curl \
    -d "profile_id=employees" \
    --data-urlencode "public_key=nmZ5ExqRpLgJV9yWKlaC7KQ7EAN7eRJ4XBz9eHJPmUU=" \
    -H "Authorization: Bearer abcdefgh" \
    "https://vpn.example.org/vpn-user-portal/api/v3/connect"
```

**NOTE**: a call to `/connect` immediately invalidates any previously obtained 
VPN configuration files that belong to the same OAuth _authorization_.

The `POST` request has (optional) parameters:

| Parameter    | Required | Value(s)                                                                         |
| ------------ | -------- | -------------------------------------------------------------------------------- |
| `profile_id` | Yes      | The `profile_id` from the `/info` response                                       |
| `public_key` | No       | A WireGuard public key, for WireGuard                                            |
| `prefer_tcp` | No       | Prefer connecting over TCP to the server. Either `yes` or `no`. Defaults to `no` |

#### Profile ID

The value of `profile_id` MUST be of one of the identifiers for the profiles 
returned in the `/info` response.

#### Public Key

When the WireGuard protocol is expected to be used, the `public_key` parameter 
MUST be set. The value of `public_key` MUST be a valid WireGuard public key. It 
has this format:

```bash
$ wg genkey | wg pubkey
e4C2dNBB7k/U8KjS+xZdbicbZsqR1BqWIr1l924P3R4=
```

Note for implementation: you MAY also use 
[libsodium](https://doc.libsodium.org/)'s `crypto_box_keypair()` to generate a 
keypair and extract the public key using `crypto_box_publickey()` instead of
using `exec()` to run the `wg` tool.

**NOTE**: do NOT use the same WireGuard private key for different servers, 
generate one *per server*.

#### Prefer TCP

The `prefer_tcp` parameter is currently only used in combination with the 
OpenVPN protocol.

If set the `yes`, the client indicates that a connection over TCP is preferred.
The server MAY accept this and return an OpenVPN configuration with the TCP 
"remotes" first and thus have the client try to connect over TCP First.

The server MAY ignore the option, for example when the profile only supports
WireGuard, or the OpenVPN process does not listen on TCP ports.

### Response

If the profile is an OpenVPN profile you'll get the complete OpenVPN client
configuration with `Content-Type: application/x-openvpn-profile`, e.g.:

```
HTTP/1.1 201 Created
Expires: Fri, 06 Aug 2021 03:59:59 GMT
Content-Type: application/x-openvpn-profile

dev tun
client
nobind
remote-cert-tls server
verb 3
server-poll-timeout 10
tls-version-min 1.3
data-ciphers AES-256-GCM:CHACHA20-POLY1305
reneg-sec 0
<ca>
-----BEGIN CERTIFICATE-----
MIIBQzCB9qADAgECAhBiISHrvtMXVOiLSaTsLKTKMAUGAytlcDARMQ8wDQYDVQQD
EwZWUE4gQ0EwHhcNMjExMDExMTk1MDE0WhcNMzExMDExMTk1NTE0WjARMQ8wDQYD
VQQDEwZWUE4gQ0EwKjAFBgMrZXADIQBysHsh1pkJpLj6wJVQLGQW1C6cfW74tSZu
cCUP/wXF86NkMGIwDgYDVR0PAQH/BAQDAgKEMB0GA1UdJQQWMBQGCCsGAQUFBwMB
BggrBgEFBQcDAjASBgNVHRMBAf8ECDAGAQH/AgEAMB0GA1UdDgQWBBQmdLockXn6
YJFZ/a1X9PvhH2eD+jAFBgMrZXADQQCI2MtG+k3CtCHDM8+4lZG7LXpVLFG4EACJ
JJlplLlFlLr5qMsNFkf2oTjWccsn9qXmBkfvIcda4BLJF0xRZ08L
-----END CERTIFICATE-----
</ca>
<cert>
-----BEGIN CERTIFICATE-----
MIIBbjCCASCgAwIBAgIQTXCf2KpYiGLLFMl3roW7BTAFBgMrZXAwETEPMA0GA1UE
AxMGVlBOIENBMB4XDTIxMTEwMjA4MjM0MloXDTIyMDEzMTAzNTk1OVowSTEQMA4G
A1UECxMHZGVmYXVsdDE1MDMGA1UEAxMsanlkUkprdUd1Vk9uL1QzNnR6dEE3aVNq
KzFTUThtZXZKQlYxZ1hvZ3l0VT0wKjAFBgMrZXADIQADR7x0pbS6C8YxHOW4wXUE
0wXlez1go0xrhnEXaKjSBqNWMFQwDgYDVR0PAQH/BAQDAgeAMBMGA1UdJQQMMAoG
CCsGAQUFBwMCMAwGA1UdEwEB/wQCMAAwHwYDVR0jBBgwFoAUJnS6HJF5+mCRWf2t
V/T74R9ng/owBQYDK2VwA0EAY1pNvtE2N11hkyGEFXyTJzYvp/FRnR4AOM1mtxCu
1cLEt2mZW+lGB/0JOLDyyrYJ/1A+DvYeJhbto30FY50yDA==
-----END CERTIFICATE-----
</cert>
<key>
-----BEGIN PRIVATE KEY-----
MC4CAQAwBQYDK2VwBCIEIDtCkdkMVO5IV1HWsGqDSX0sIE0FENW6estLvfDSr4bp
-----END PRIVATE KEY-----
</key>
<tls-crypt>
#
# 2048 bit OpenVPN static key
#
-----BEGIN OpenVPN Static key V1-----
7a086674dc25cf16c609a6cf6b206046
0592cf3e98dc58262d4c780d9d37ad30
e726d4d4b4da651ccaa232e84e0eea14
13870e2cd391057ca402fac3eb3ced8e
e88c848a785a6878f01ea9f9c8e947d9
2cede35d0a51a34f6c2e06a6c118e5c2
267a81a8c69b67d110c264d03bd7e2e9
a529a7d37828050f1031cc405369903a
d092231c573794e07333c72b832cddde
a4f071a90063edf1561b32ab28884a4b
786abe2438c5e6e312811e3eacf90196
648a17cc193295e684a475ad5bb6510f
d4cf0f1061ddb7d69dc4fd355774cf7f
d904456b668e128a861151ed12da788c
c34b9a63c3f74fa96a26a61d203a0e85
fe9edd1611499201429a2f6e91d1e307
-----END OpenVPN Static key V1-----
</tls-crypt>
remote vpn.example 1194 udp
remote vpn.example 1194 tcp
```

If the profile is an WireGuard profile you'll get the complete WireGuard client
configuration with `Content-Type: application/x-wireguard-profile`, e.g.:

```
Expires: Fri, 06 Aug 2021 03:59:59 GMT
Content-Type: application/x-wireguard-profile

[Interface]
Address = 10.43.43.2/24, fd43::2/64
DNS = 9.9.9.9, 2620:fe::fe

[Peer]
PublicKey = iWAHXts9w9fQVEbA5pVriPlAYMwwEPD5XcVCZDZn1AE=
AllowedIPs = 0.0.0.0/0, ::/0
Endpoint = vpn.example:51820
```

You MUST use the `Expires` response header value to figure out how long the VPN 
session will be valid for. When implementing the client, make sure you never
connect to the VPN server with an expired VPN configuration.

Before using this configuration, your locally generated private key needs to 
be added under the `[Interface]` section, e.g.:

```
[Interface]
PrivateKey = AJmdZTXhNRwMT1CEvXys2T9SNYnXUG2niJVT4biXaX0=

...
```

## Disconnect

This call is to indicate to the server that the VPN session(s) belonging to 
this OAuth authorization can be terminated. This MUST ONLY be called when the 
_user_ decides to stop the VPN connection.

The purpose of this call is to clean up, i.e. release the IP address reserved
for the client (WireGuard) and delete the certificate from the list of allowed 
certificates (OpenVPN). 

After calling this method you MUST NOT use the same configuration again to 
attempt to connect to the VPN server. First call `/connect` again.

This call is "best effort", i.e. it is not a huge deal when the call fails. No 
special care has to be taken when this call fails, e.g. the connection is dead,
or the application crashes. However, it MUST be called on "application exit" 
when the user closes the VPN application without disconnecting first, unless 
the VPN connection can also be managed outside the VPN.

This call MUST be executed *after* the VPN connection itself has been 
terminated by the application, if possible.

### Request

```bash
$ curl \
    -H "Authorization: Bearer abcdefgh" \
    "https://vpn.example.org/vpn-user-portal/api/v3/disconnect"
```

This `POST` call has no parameters.

### Response

```
HTTP/1.1 204 No Content

```

## Error Responses

| Call          | Message                      | Code | Description                                                          |
| ------------- | ---------------------------- | ---- | -------------------------------------------------------------------- |
| `/connect`    | `profile not available`      | 400  | When the profile does not exist, or the user has no permission       |
| `/connect`    | `invalid "prefer_tcp"`       | 400  | When the specified values are neither `yes` nor `no`                 |
| `/connect`    | `invalid "profile_id"`       | 400  | When the syntax for the `profile_id` is invalid                      |

An example:

```
HTTP/1.1 400 Bad Request
Content-Type: application/json

{"error":"profile not available"}
```

In addition to these errors, there can also be an error with the server that we
did not anticipate or is an unusual situation. In that case the response code
will be 500 and the JSON `error` key will contain more information about the
error. This is usually not something the user/client can do anything with and 
it should probably be shown as a "server error" to the user. Possibly with a 
"Try Again" button. The exact error response MUST be logged and accessible by
the user if so instructed by the support desk, and MAY be shown to the user in 
full, however a generic "Server Error" could be considered as well, perhaps 
with a "Details..." button.

# VPN Protocol Selection

Profiles are able to support both OpenVPN and WireGuard. It is up to the 
server administrator to enable particular protocols. Profiles can support 
either OpenVPN, WireGuard, or _both_. Administrators can also configure a 
_preferred_ protocol per profile if both are supported.

Clients supporting this version of the API SHOULD support both OpenVPN and 
WireGuard, but MAY support only OpenVPN.

All existing eduVPN/Let's Connect! applications have some sort of "Force TCP" 
setting that allows users to force OpenVPN connections to use TCP only. This is 
important in case UDP is blocked in the network, or is broken, typically due to 
(Path) MTU Discovery issues. Eventually applications SHOULD be able to 
determine automatically whether UDP works reliably and we could get rid of this 
setting toggle.

For now, the "Force TCP" selection SHOULD be interpreted as: "Prefer using 
OpenVPN over TCP, if available". This works for protocols that support both 
OpenVPN and WireGuard, but not for protocols supporting only WireGuard where 
a WireGuard configuration will be returned no matter what. WireGuard MAY work
over UDP where OpenVPN did not, so it is still better than doing nothing.

We assume the client always supports OpenVPN. In scope of this API version, the 
following _pseudo code_ can be used to implement the protocol selection.

If the client supports both OpenVPN and WireGuard:

```
POST /connect [public_key=${PK}, prefer_tcp=${Force_TCP}]
```

If the client only supports OpenVPN:

```
POST /connect [prefer_tcp=${Force_TCP}]
```

# Flow

Below we describe how the application MUST interact with the API. It does NOT
include information on how to handle OAuth. The application MUST properly 
handle OAuth, including error cases both during the authorization, when using
a "Refresh Token" and when using the API with an "Access Token".

1. Call `/info` to retrieve a list of available VPN profiles for the user;
2. Show the available profiles to the user if there is >1 profile and allow
   the user to choose, show "No Profiles Available for your Account" when there
   are no profiles;
3. After the user chose (or there was only 1 profile) perform the `/connect` 
   call as per [VPN Protocol Selection](#vpn-protocol-selection);
4. Store the configuration file from the response. Make note of the value of
   the `Expires` response header to be able to figure out how long your are 
   able to use this VPN configuration;
5. Connect to the VPN;
6. Wait for the user to request to disconnect the VPN...;
7. Disconnect the VPN;
8. Call `/disconnect`;
9. Delete the stored configuration file and its expiry time.

As long as the configuration is not "expired", according to the `Expires` 
response header the same configuration SHOULD be used until the user manually
decides to disconnect. This means that during suspend, or temporary unavailable 
network, the same configuration SHOULD be used. The application SHOULD 
implement "online detection" to be able to figure out whether the VPN allows 
any traffic over it or not.

The basic rules:

1. `/connect` (and `/disconnect`) ONLY need to be called when the user decides 
   to connect/disconnect, not when this happens automatically for whatever 
   reason, e.g. suspending the device, network not available, ...;
2. There are no API calls as long as the VPN is (supposed to be) up (or down).

**NOTE** if the application implements some kind of "auto connect" on 
(device or application) start-up that of course MUST call `/info` and 
`/connect` as well! The `/info` call to be sure the profile is still available 
(for the user) and the `/connect` to obtain a configuration. This does NOT 
apply when the application configures a "system VPN" that also runs without the 
VPN application being active. The application MUST implement a means to notify
the user when the configuration is about to expire.

It can of course happen that the VPN is not working when using the VPN 
configuration that is not yet expired. In that case the client SHOULD inform
the user about this, e.g. through a notification that possibly opens the 
application if not yet open. This allows the user to (manually) 
disconnect/connect again restoring the VPN and possibly renewing the 
authorization when e.g. the authorization was revoked.
