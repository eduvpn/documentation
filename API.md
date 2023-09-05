# API

This document describes version 3 of the API provided by eduVPN and 
Let's Connect! servers.

The API is intended to be used by the eduVPN and Let's Connect! applications. 
If you are creating your own application, look 
[here](API_CLIENT_REGISTRATION.md) how to register your own client in the 
server.

Using this document you should be able to implement the API in your VPN client, 
or provide the same API for your VPN server to leverage the existing VPN 
clients.

This API is fully supported by all eduVPN / Let's Connect! 3.x servers and 2.x 
servers with version >= 2.4.1.

The API design was finalized and is considered _stable_ from 2022-01-27.

## Standards

We use a simple HTTP API protected by OAuth 2, following all recommendations 
of the [OAuth 2.1](https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/) 
draft specification.

For some further implementation notes and recommendations for the client,
please read [this document](CLIENT_IMPLEMENTATION_NOTES.md).

## Server Discovery

As there are many servers running eduVPN / Let's Connect! you need to know 
which server you need to connect to. This can be either hard-coded in the 
application, the user can be asked to provide a server address or a "discovery" 
can be implemented.

For eduVPN specific we implement "server discovery" as documented 
[here](SERVER_DISCOVERY.md).

## Server Endpoint Discovery

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

### Endpoint Location

When fetching this document, _redirects_, e.g. `301`, `302`, `303`, MUST be 
followed, but MUST NOT allow redirect to anything else than other `https://` 
URLs, e.g. redirects to `http://` MUST be rejected.

## Authorization Endpoint

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

The `authorization_endpoint` with its parameters set MUST be opened in the 
platform's default browser or follow the platform's best practice dealing with
application authorization(s). The `redirect_uri` parameter MUST point back to 
a location the application can intercept.

All error conditions, both during the authorization phase AND when talking 
to the API endpoint MUST be handled according to the OAuth specification(s).

## Token Endpoint

The `token_endpoint` is used to exchange the authorization code, as obtained
through the `redirect_uri` as part of the authorization, for an access and 
refresh token. It is also used to retrieve new access tokens when the current 
access token expires.

All error conditions, both during the authorization phase AND when talking 
to the API endpoint MUST be handled according to the OAuth specification(s).

## Using the API

Every API call below will include a cURL example, and an example response that 
can be expected.

All `POST` requests MUST be sent encoded as 
`application/x-www-form-urlencoded`.

The API can be used with the access token obtained using the OAuth flow as 
documented above. The following API calls are available:

- Get "Info" from the VPN server, including a list of available profiles 
  (`/info`);
- "Connect" to a VPN profile (`/connect`);
- "Disconnect" from a VPN profile (`/disconnect`)

## API Calls

### Info

This call will show the available VPN profiles for this instance. This will 
allow the application to show the user which profiles are available.

This `GET` call has no parameters.

#### Request

Request all available VPN profiles:

```bash
$ curl \
    -H "Authorization: Bearer abcdefgh" \
    https://vpn.example.org/vpn-user-portal/api/v3/info
```

#### Response

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
                ]
            },
            {
                "default_gateway": false,
                "display_name": "Administrators",
                "profile_id": "admins",
                "vpn_proto_list": [
                    "wireguard"
                ]
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
a VPN client does not support (some) of the listed protocols, they can be 
omitted, or marked as unsupported in that VPN client. Currently `openvpn` and 
`wireguard` values are supported. As an example: a WireGuard only client 
SHOULD NOT list VPN profiles that only support OpenVPN.

### Connect

Get the profile configuration for the profile you want to connect to.

#### Request

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
| `profile_id` | Yes      | The `profile_id`, as obtained from the `/info` response                          |
| `public_key` | No       | A WireGuard public key, for the WireGuard protocol                               |
| `prefer_tcp` | No       | Prefer connecting over TCP to the server. Either `yes` or `no`. Defaults to `no` |

The following `Header` can be used:

| Header | Required | Value(s)                                                                                                                                                          |
| ------ | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Accept | No       | `application/x-openvpn-profile` to only accept OpenVPN, `application/x-wireguard-profile` to only accept WireGuard. For both concatenate both values with a comma |

See [VPN Protocol Selection](#vpn-protocol-selection) for more info.

##### Profile ID

The value of `profile_id` MUST be of one of the identifiers for the profiles 
returned in the `/info` response.

##### Public Key

When the WireGuard protocol is expected to be used, the `public_key` parameter 
MUST be set. The value of `public_key` MUST be a valid WireGuard public key. It 
has this format:

```bash
$ wg genkey | wg pubkey
e4C2dNBB7k/U8KjS+xZdbicbZsqR1BqWIr1l924P3R4=
```

##### Prefer TCP

The `prefer_tcp` parameter is a hint for the VPN server, currently only for the 
OpenVPN protocol.

If set to `yes`, the client indicates that a connection over TCP is preferred.
The server MAY accept this and return an OpenVPN configuration with the TCP 
"remotes" first and thus have the client try to connect over TCP first.

The server MAY ignore the option, for example when the profile only supports
WireGuard, or the OpenVPN server configuration does not use TCP.

#### Response

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

If the profile is an WireGuard profile you'll get a WireGuard client
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

### Disconnect

This call is to indicate to the server that the VPN session(s) belonging to 
this OAuth authorization can be terminated.

The purpose of this call is to clean up, i.e. release the IP address reserved
for the client (WireGuard) and delete the certificate from the list of allowed 
certificates (OpenVPN).

#### Request

```bash
$ curl -X POST \
    -H "Authorization: Bearer abcdefgh" \
    "https://vpn.example.org/vpn-user-portal/api/v3/disconnect"
```

This `POST` call has no parameters.

#### Response

```
HTTP/1.1 204 No Content

```

### Error Responses

| Call          | Example Message                        | Code | Description                                                                                   |
| ------------- | -------------------------------------- | ---- | --------------------------------------------------------------------------------------------- |
| `/connect`    | `no such "profile_id"`                 | 404  | When the profile does not exist, or the user has no permission                                |
| `/connect`    | `invalid "prefer_tcp"`                 | 400  | When the specified values are neither `yes` nor `no`                                          |
| `/connect`    | `invalid value for "profile_id"`       | 400  | When the syntax for the `profile_id` is invalid                                               |
| `/connect`    | `missing "public_key" parameter`       | 400  | When the profile only supports WireGuard and no WireGuard public key was provided             |
| `/connect`    | `profile "x" does not support OpenVPN` | 406  | When the profile does not support the VPN protocol(s) supported by the client (or vice versa) | 

An example:

```
HTTP/1.1 404 Not Found
Content-Type: application/json

{"error":"no such \"profile_id\""}
```

In addition to these errors, there can also be an error with the server that we
did not anticipate or is an unusual situation. In that case the response code
will be 500 and the JSON `error` key will contain more information about the
error.

## VPN Protocol Selection

The VPN server decides which protocol will be used for the VPN connection. This
can be either OpenVPN or WireGuard. The client _is_ able to influence this 
decision. You don't really need to understand the algorithm, but it will 
explain what is going on when what you see is not what you expect.

The algorithm in the server:

```
Which Protocol Will be Used?
    VPN Client Supports: OpenVPN, but not WireGuard:
        Profile Supports: OpenVPN:
            ---> "OpenVPN"
        ---> Error
        
    VPN Client Supports: WireGuard, but not OpenVPN:
        Profile Supports: WireGuard
            ---> "WireGuard"
        ---> Error
    
    # At this point we know the client supports OpenVPN & WireGuard
     
    Profile Supports: OpenVPN, but not WireGuard:
        ---> "OpenVPN"
        
    Profile Supports: WireGuard, but not OpenVPN:
        ---> "WireGuard"
        
    # At this point we know both the VPN client and Profile supports OpenVPN & WireGuard

    OpenVPN is Preferred Protocol:
        ---> "OpenVPN"
            
    Client Prefers TCP:
        OpenVPN Server Supports TCP:
            ---> "OpenVPN"
        
    Client Provides WireGuard Public Key:
        ---> "WireGuard"
        
    ---> "OpenVPN"
```

A VPN application can indicate protocol support by using the HTTP `Accept` 
request header. This header is used on the `/connect` call.

If the VPN client only supports OpenVPN:

```
Accept: application/x-openvpn-profile
```

If the VPN client only supports WireGuard:

```
Accept: application/x-wireguard-profile
```

If the VPN client supports both OpenVPN and WireGuard:

```
Accept: application/x-openvpn-profile, application/x-wireguard-profile
```

**NOTE**: if the `Accept` request header is missing, it is assumed that the 
VPN client supports both OpenVPN and WireGuard.

## History

The changes made to the API documentation.

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
|            | When profile does not exist, a 404 is returned on `/connect` instead of 400                                     |
|            | Remove the `vpn_proto_preferred` key from the `/info` response                                                  |
|            | Rewrite [VPN Protocol Selection](#vpn-protocol-selection) and document protocol selection, add `Accept` header  |
| 2022-01-27 | **Declared API "Stable"**                                                                                       |
| 2023-02-07 | Improve "Disconnect" section to list all cases where `/disconnect` should be called                             |
| 2023-02-08 | Simplify "Session Expiry" section                                                                               |
| 2023-08-25 | Mention a second "Countdown Timer" in "Connection Info"                                                         |
| 2023-09-05 | Move client specific changes to own file                                                                        |
