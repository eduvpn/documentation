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

## Endpoint Location

Currently we support both `/info.json` and `/.well-known/vpn-user-portal` in 
eduVPN/Let's Connect! 2.x. It would be nice to phase out `/info.json`.

When fetching this document, _redirects_, e.g. `301`, `302`, `303`, MUST be 
followed.

**TODO**: it MUST follow the redirects, but *only* for `/info.json` and 
`/.well-known/vpn-user-portal`, not for the endpoints found through it.

**TODO**: maybe we can "hard code" the list of endpoints as well, so there is
no need to advertise them in the `/info.json`.

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

Optionally you can filter the VPN profile list based on the VPN protocol used. 
If you client does not support WireGuard or OpenVPN, you can indicate this by
sending the `X-Proto-Support` request header with a comma separated list of
supported protocols. If you do not send this header, you are implicitly 
claiming to support all protocols.

This `GET` call has no parameters.

### Request

Request all available VPN profiles:

```bash
$ curl \
    -H "Authorization: Bearer abcdefgh" \
    https://vpn.example.org/vpn-user-portal/api.php/v3/info
```

If your application does not support a particular VPN protocol you can filter
the list by using the `X-Proto-Support` HTTP request header:

| Header                               | VPN Protocol Support in Client |
| _no header_                          | Both OpenVPN and WireGuard     |
| `X-Proto-Support: openvpn,wireguard` | Both OpenVPN and WireGuard     |
| `X-Proto-Support: openvpn`           | Only OpenVPN                   |
| `X-Proto-Support: wireguard`         | Only WireGuard                 |

### Response

```
HTTP/1.1 200 OK
Content-Type: application/json

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

The `display_name` field can be either of type `string` or `object`. When the
field is an object, the keys are 
[BCP-47 language codes](https://en.wikipedia.org/wiki/IETF_language_tag).

## Connect

Get the profile configuration for the profile you want to connect to.

### Request

```bash
$ curl \
    -d "profile_id=employees" \
    --data-urlencode "public_key=nmZ5ExqRpLgJV9yWKlaC7KQ7EAN7eRJ4XBz9eHJPmUU=" \
    -H "Authorization: Bearer abcdefgh" \
    "https://vpn.example.org/vpn-user-portal/api.php/v3/connect"
```

This `POST` call has 2 parameters, `profile_id` and `public_key`. The value of 
`profile_id` MUST be of one of the profiles returned by the `/info` call. The 
value of `public_key` MUST be a WireGuard public key. It has this format:

```
$ wg genkey | wg pubkey
e4C2dNBB7k/U8KjS+xZdbicbZsqR1BqWIr1l924P3R4=
```

**NOTE**: do NOT use the same WireGuard key for different servers, generate 
on *per server*.
**NOTE**: in case your application supports WireGuard, it MUST provide the
`public_key` in all situations as the client has no idea whether the profile.
will be a WireGuard or OpenVPN profile. Currently, the server only enforces the 
`public_key` parameter when the profile turns out to be a WireGuard profile.

### Response

If the profile is an OpenVPN profile you'll get the complete OpenVPN client
configuration with `Content-Type: application/x-openvpn-profile`, e.g.:

```
HTTP/1.1 201 Created
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
Expires: Fri, 06 Aug 2021 03:59:59 GMT
Content-Type: application/x-wireguard-profile

[Interface]
Address = 10.10.10.12/24, fd00:1234:1234:1234::a0a:a0c/64
DNS = 9.9.9.9, 2620:fe::fe

[Peer]
PublicKey = Gwcpqv5WeCI3XotETskDXQLfYQk0fi8gEpuCQVIoKGc=
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

This call is to indicate to the server that the VPN session can be terminated.
This MUST ONLY be called when the _user_ decides to stop the VPN connection.

The purpose of this call is to "release" the IP address reserved for the 
client to make it available for other clients connecting. This is especially
important when using a limited IP range for VPN clients.

This call is "best effort", i.e. it is not a big deal when the call fails. No 
special care has to be taken when this call fails, e.g. the connection is dead,
or the application crashes. However, it MUST be called on "application exit" 
when the user closes the VPN application without disconnecting first, unless 
the VPN connection can also be managed outside the VPN.

This call MUST be executed *after* the VPN connection itself has been 
terminated by the application.

### Request

```bash
$ curl \
    -d "profile_id=employees" \
    -H "Authorization: Bearer abcdefgh" \
    "https://vpn.example.org/vpn-user-portal/api.php/v3/disconnect"
```

This `POST` call has 1 parameter, `profile_id`. Its value MUST be the same as 
used for the `/connect` call.

### Response

```
HTTP/1.1 204 No Content

```

# Flow

Below we describe how the application MUST interact with the API. It does NOT
include information on how to handle OAuth. The application MUST properly 
handle OAuth, including error cases both during the authorization, refreshing
tokens and during the use of the API.

1. Call `/info` to retrieve a list of available VPN profiles for the user;
2. Show the available profiles to the user when there is > 1 profile and allow
   the user to choose;
3. After the user chose (or there was only 1 profile) perform the `/connect` 
   call;
4. Store the configuration file from the response. Make note of the value of
   the `Expires` response header to be able to figure out how long your are 
   able to use the VPN configuration;
5. Connect to the VPN;
6. Wait for the user to disconnect the VPN...;
7. Disconnect the VPN;
8. Call `/disconnect`.

As long as the configuration is not "expired", according to the `Expires` 
response header the same configuration SHOULD be used until the user manually
decides to disconnect. This means that during suspend, or temporary unavailable 
network, the same configuration SHOULD be used. The application SHOULD 
implement "online detection" to be able to figure out whether the VPN allows 
any traffic over it or not.

The basic rules: 

1. `/connect` (and `/disconnect`) ONLY need to be called when the user decides 
   to connect/disconnect, not when this happens automatically for whatever 
   reason, e.g. suspending the device, network not available;
2. There are no API calls as long as the VPN is (supposed to be) up.

**NOTE** if the application implements some kind of "auto connect" on 
(device or application) start-up that of course MUST call `/info` and 
`/connect` as well! The `/info` call to be sure the profile is still available 
(for the user) and the `/connect` to obtain a configuration.

It can of course happen that the VPN is not working when using the VPN 
configuration that is not yet expired. In that case the client SHOULD inform
the user about this, e.g. through a notification that possibly opens the 
application if not yet open. This allows the user to (manually) 
disconnect/connect again restoring the VPN and possibly renewing the 
authorization when e.g. the authorization was revoked.

# TODO

- talk about limits for the API, for example 1 user can only be online _n_ 
  times;
- API returns *same* configuration when client calls `/connect` multiple times
  all other things being equal (only WireGuard)?;
- Give some error responses as examples

# Notes

- we should probably rename the `/connect` call to `/setup` or `/register`, or 
  something like this, as there is no actual connection taking place...
- Clients will have to deal with the scenario that no IP address is available 
  anymore for them, i.e. the `/connect` call fails
- Clients will really need a check to verify the VPN connection is up, e.g. 
  ping the remote peer address (gateway?) or simply by checking when the last
  handshake took place?
- The certificate/public key will expire exactly at the moment the OAuth 
  refresh and access token no longer work
- when the computer goes to sleep you can just try to reconnect with the 
  previously obtained configuration, no need to use the API, BUT if connecting
  doesn't work go back to the API
- we need a flow diagram...
- the application can offer a "Renew" button when the current VPN session is 
  nearing its end. This button would throw away the OAuth tokens and restart 
  the authorization before (automatically) reconnecting to the same 
  server/profile if still available;
