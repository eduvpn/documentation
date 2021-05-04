---
title: API Version 3
description: API Documentation for (Native) Application Developers
category: dev
---

**NOTE**: WORK IN PROGRESS AS OF 2021-05-04

This document describes the API provided by all Let's Connect!/eduVPN services.

The API can be used by applications integrating with the VPN software, making
it easier for users to start using the VPN.

# Instance Discovery

This document assumes you already have a FQDN to connect to, for example 
obtained through the user providing it directly, or through a discovery 
mechanism as for example documented [here](SERVER_DISCOVERY.md).

# Standards

OAuth 2.0 is used to provide the API. The following documents are relevant for 
implementations and should be followed except when explicitly stated 
differently:

* [The OAuth 2.0 Authorization Framework](https://tools.ietf.org/html/rfc6749);
* [The OAuth 2.0 Authorization Framework: Bearer Token Usage](https://tools.ietf.org/html/rfc6750);
* [OAuth 2.0 for Native Apps](https://tools.ietf.org/html/rfc8252);
* [Proof Key for Code Exchange by OAuth Public Clients](https://tools.ietf.org/html/rfc7636)

Implementing OAuth 2.0 correctly in native apps is not easy. There are a number 
of sample libraries available for various platforms that can be used as a 
basis:

* [Android](https://github.com/openid/AppAuth-Android)
* [iOS](https://github.com/openid/AppAuth-iOS)
* [Windows](https://github.com/googlesamples/oauth-apps-for-windows)

With this library it is very important that you handle all standard OAuth 
"error" conditions regarding expired, invalid or revoked tokens.

**NOTE**: the server implements the OAuth 2.1 
[draft](https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/) specification.

# Definitions

A VPN service running at a particular domain (FQDN) is called an _instance_, 
e.g. `demo.eduvpn.nl`. An instance can have multiple _profiles_, e.g. 
`students` and `employees`.

# API Discovery

A "well-known" URL is provided to figure out the OAuth and API endpoint one 
has to use. The document can be retrieved from `/.well-known/vpn-user-portal`, 
e.g.:

```json
{
  "api": {
    "http://eduvpn.org/api#3": {
      "api_endpoint": "https://vpn-next.tuxed.net/vpn-user-portal/api/v3",
      "authorization_endpoint": "https://vpn-next.tuxed.net/vpn-user-portal/oauth/authorize",
      "token_endpoint": "https://vpn-next.tuxed.net/vpn-user-portal/oauth/token"
    }
  },
  "v": "3.0.0-0.75.fc34"
}
```

When fetching this document, _redirects_, e.g. `301`, `302`, `303`, MUST be 
followed.

**NOTE**: for legacy purposes this document is also available under 
`/info.json`, but MUST not be used any longer.

# Authorization Endpoint

The `authorization_endpoint` is used to obtain an authorization code. The 
following query parameters MUST be specified on the authorization request:

* `client_id`: the ID that was registered, see below;
* `redirect_uri`; the URL that was registered, see below;
* `response_type`: always `code`;
* `scope`: this is always `config`;
* `state`: a secure random string suitable for cryptography purposes, to avoid 
  CSRF;
* `code_challenge_method`: always `S256`; 
* `code_challenge`: the code challenge (see RFC 7636).

The authorization request is then opened using the platform's default browser. 
Eventually the `redirect_uri` is called where the initiating application can 
extract the authorization code.

All error conditions MUST be handled according to the OAuth specification(s).

# Token Endpoint

The `token_endpoint` is used to exchange the authorization code for an access
and refresh token. It is also used to retrieve new access tokens when the 
current access token expires.

The application MUST reauthorize, i.e. throw away all tokens and send a new 
authorization request, when:

1. The access token did not expire yet, but was rejected by the API endpoint;
2. The access token expired, but obtaining a new one using the refresh token 
   failed.

All error conditions MUST be handled according to the OAuth specification(s).

# Using the API

The API is pragmatic "REST", keeping things as simple as possible without 
obsessing about the proper HTTP verbs. There are no `PUT` and `DELETE` 
requests. Only `GET`, to retrieve information without affecting the state of
the service, and `POST` to modify the server state.

The requests always return `application/json`. The `POST` requests MUST be sent 
encoded as `application/x-www-form-urlencoded`.

The API can be used with the access tokens obtained using the OAuth flow as 
documented above. The following API calls are available:

- Get a list of VPN profiles (`/info`)
- Enroll for a VPN profile (`/enroll`)
  - Obtain a private/public key (for OpenVPN)
  - Allows you to register a public key (for WireGuard)
- "Connect" to a VPN profile (`/connect`)
  - registers "intent to connect" to the server, and obtains required client
    configuration (OpenVPN / WireGuard);
- "Disconnect" from a VPN profile (`/disconnect`)
  - registers intent to disconnect (OpenVPN / WireGuard)

All error conditions MUST be handled according to the OAuth specification(s).

## API Calls

### Multi Language Support

For the calls listed below, applications MUST check if the mentioned value is 
a string, or an object. In case of an object, the language best matching
the application language SHOULD be chosen. If that language is not available, 
the application SHOULD fallback to `en` or `en-US`. If neither of those is 
available, it is up to the application to pick one it deems best.

- `/info`, the `display_name` field;

An example:

```json
"display_name": {
    "nl": "Medewerkers",
    "en-US": "Employees"
}
```

### Info

This call will show the available VPN profiles for this instance. This will 
allow the application to show the user which profiles are available.

    $ curl -H "Authorization: Bearer abcdefgh" \
        https://vpn-next.tuxed.net/vpn-user-portal/api/v3/info

The response looks like this:

```json
{
    "info": [
        {
            "display_name": {
                "nl": "Medewerkers",
                "en-US": "Employees"
            },
            "profile_id": "employees",
            "vpn_type": "openvpn",
            "default_gateway": true,
        },
        {
            "display_name": {
                "nl": "Beheerders",
                "en-US": "Administrators"
            },
            "profile_id": "admins",
            "vpn_type": "wireguard",
            "default_gateway": false,
        }            
    ]
}
```

### Enroll

This allows you to "enroll" for connecting to a VPN profile. Depending on the
`vpn_type` you will need to provide different parameters.

#### OpenVPN

The `employees` profile is an OpenVPN profile. This call will result in 
getting a private/public key for use by OpenVPN. 

```bash
$ curl -d "profile_id=employees" -H "Authorization: Bearer abcdefgh" \
    https://vpn-next.tuxed.net/vpn-user-portal/api/v3/enroll
```

Response:

```json
{
    "enroll": {
        "certificate": "-----BEGIN CERTIFICATE----- ... -----END CERTIFICATE-----",
        "private_key": "-----BEGIN PRIVATE KEY----- ... -----END PRIVATE KEY-----"
    }
}
```

The certificate and the private key SHOULD be stored in the platform's 
"key store" in such a way that the user can **NOT** export the private key.

In traditional OpenVPN client configuration files, the certificate would be 
placed in the `<cert>...</cert>` inline section, and the private key in the 
`<key>...</key>` section.

#### WireGuard

The `admins` profile is a WireGuard profile. This call will allow you to 
register a WireGuard public key for this profile.

```bash
$ curl -d "profile_id=admins" -d "public_key=XYZABCD" -H "Authorization: Bearer abcdefgh" \
    https://vpn-next.tuxed.net/vpn-user-portal/api/v3/enroll
```

The response will be `204 No Content` if all goes well.

### Connect

Only get the profile configuration without certificate and private key.

```bash
$ curl -d "profile_id=employees" -H "Authorization: Bearer abcdefgh" \
    "https://vpn-next.tuxed.net/vpn-user-portal/api/v3/connect"
```

In case of OpenVPN, the response will be an OpenVPN configuration file without 
the `<cert>` and `<key>` fields.

```
${OPENVPN CLIENT CONFIG FILE}
```

In case of WireGuard, the response will be a WireGuard configuration file.

### Disconnect

    $ curl -d "profile_id=employees" -H "Authorization: Bearer abcdefgh" \
        "https://vpn-next.tuxed.net/vpn-user-portal/api/v3/disconnect"

The response will be `204 No Content` if all goes well.
