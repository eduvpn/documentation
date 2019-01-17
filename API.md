# Introduction

This document describes the API provided by all Let's Connect!/eduVPN services.

The API can be used by applications integrating with the VPN software, making
it easier for users to start using the VPN.

# Instance Discovery

This document assumes you already have a FQDN to connect to, e.g. specified by
the user, but in order to allow applications to create a list of VPN services 
available to the user to connect to, we also documented 
[Instance Discovery](INSTANCE_DISCOVERY.md).

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

# Definitions

A VPN service running at a particular domain is called an _instance_, e.g. 
`demo.eduvpn.nl`. An instance can have multiple _profiles_, e.g. 
`employees` and `administrators`.

# API Discovery

The OAuth and API endpoints can be discovered by requesting a JSON document
from the instance, based on the `base_uri`, e.g. `demo.eduvpn.nl`. As an 
example, here is the content of `https://demo.eduvpn.nl/info.json`:

    {
        "api": {
            "http://eduvpn.org/api#2": {
                "api_base_uri": "https://demo.eduvpn.nl/portal/api.php",
                "authorization_endpoint": "https://demo.eduvpn.nl/portal/_oauth/authorize",
                "token_endpoint": "https://demo.eduvpn.nl/portal/oauth.php/token"
            }
        }
    }

# Authorization Endpoint

The `authorization_endpoint` is used to obtain an authorization code. The 
following query parameters MUST be specified on the authorization request:

* `client_id`: the ID that was registered, see below;
* `redirect_uri`; the URL that was registered, see below;
* `response_type`: always `code`;
* `scope`: this is always `config`;
* `state`: a cryptographically secure random string, to avoid CSRF;
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

- Get a list of profiles available for the user (`/profile_list`);
- Obtain a new X.509 client certificate and private key (`/create_keypair`);
- Obtain OpenVPN profile configuration (`/profile_config`);
- Verify whether an existing X.509 client certificate can be used to connect
  to the VPN (`/check_certificate`).
- Check if there are any messages available to show to the user 
  (`/system_messages`)

All error conditions MUST be handled according to the OAuth specification(s).

## API Calls

### Multi Language Support

For the calls listed below, applications MUST check if the mentioned value is 
a string, or an object. In case of an object, the language best matching
the application language SHOULD be chosen. If that language is not available, 
the application SHOULD fallback to `en-US`. If `en-US` is not available, it is
up to the application to pick one it deems best.

- `/profile_list`, the `display_name` field;
- `/system_messages`, the `message` field.

An example:

    "display_name": {
        "nl-NL": "Internettoegang",
        "en-US": "Internet Access"
    }

### Date / Time Formats

Any occurence of data and/or time has the 
[ISO 8601](https://en.wikipedia.org/wiki/ISO_8601#Combined_date_and_time_representations)
format. It is used by the following API calls:

- `/system_messages`

### Profile List

This call will show the available VPN profiles for this instance. This will 
allow the application to show the user which profiles are available.

    $ curl -H "Authorization: Bearer abcdefgh" \
        https://demo.eduvpn.nl/portal/api.php/profile_list

The response looks like this:

    {
        "profile_list": {
            "data": [
                {
                    "display_name": "Internet Access",
                    "profile_id": "internet"
                }
            ],
            "ok": true
        }
    }

### Create a Key Pair 

**NOTE**: an obtained keypair is valid for ALL _profiles_ of a particular 
_instance_, so if an instance has multiple profiles, only one keypair is 
needed.

**NOTE**: on old(er) servers the `display_name` POST parameter is required, on 
up-to-date servers the parameter is ignored.

    $ curl -H "Authorization: Bearer abcdefgh" \
        -d 'display_name=OAuth' https://demo.eduvpn.nl/portal/api.php/create_keypair

The call will create a certificate and private key and return them:

    {
        "create_keypair": {
            "data": {
                "certificate": "-----BEGIN CERTIFICATE----- ... -----END CERTIFICATE-----",
                "private_key": "-----BEGIN PRIVATE KEY----- ... -----END PRIVATE KEY-----"
            },
            "ok": true
        }
    }

The certificate and the private key SHOULD be stored in the platform's 
"key store" in such a way that the user can **NOT** export the private key.

In traditional OpenVPN client configuration files, the certificate would be 
placed in the `<cert>...</cert>` inline section, and the private key in the 
`<key>...</key>` section.

### Profile Config

Only get the profile configuration without certificate and private key.

    $ curl -H "Authorization: Bearer abcdefgh" \
        "https://demo.eduvpn.nl/portal/api.php/profile_config?profile_id=internet"

The response will be an OpenVPN configuration file without the `<cert>` and 
`<key>` fields.

### Check Certificate

A call is available to check whether an already obtained certificate will be 
accepted by the VPN server. There are a number of reasons why this may not be 
the case:

- The certificate does not exist (anymore) (`certificate_missing`);
- The certificate is not yet valid (`certificate_not_yet_valid`) or not 
   valid anymore (`certificate_expired`).

The client MAY implement this call, but MAY also opt to attempt to connect and 
handle a connection rejection by attempting to obtain a new X.509 certificate / 
key using the `/create_keypair` call and retry the connection.

API call:

    $ curl -H "Authorization: Bearer abcdefgh" \
        "https://demo.eduvpn.nl/portal/api.php/check_certificate?common_name=fd2c32de88c87d38df8547c54ac6c30e"

The `common_name` is the value of the X.509 certificate's common name (CN) 
already in possesion of the client.

The response looks like this:

    {
        "check_certificate": {
            "data": {
                "is_valid": true
            },
            "ok": true
        }
    }

Here, `is_valid` can also be `false` if the certificate won't be accepted by 
the server. There MAY be a `reason` field that indicates the reason for the 
certificate to not be valid. The `reason` field is only there when `is_valid` 
is `false`:

    {
        "check_certificate": {
            "data": {
                "is_valid": false,
                "reason": "certificate_missing"
            },
            "ok": true
        }
    }

### System Messages

    $ curl -H "Authorization: Bearer abcdefgh" \
        https://demo.eduvpn.nl/portal/api.php/system_messages

The application is able to access the `system_messages` endpoint to see if 
there are any notifications available.

All messages have the type `notification`. All messages have a `date_time` 
field containing the date the message was created.

An example response:

    {
        "system_messages": {
            "data": [
                {
                    "date_time": "2018-12-10T14:10:30Z",
                    "message": "This is the MOTD!",
                    "type": "notification"
                }
            ],
            "ok": true
        }
    }

## OAuth Client Registration

A list of OAuth client registrations that are available for all installations 
can be found [here](https://github.com/eduvpn/vpn-user-portal/blob/master/src/OAuthClientInfo.php).

Administrators MAY define additional OAuth clients in the 
`/etc/vpn-user-portal/config.php` configuration file.
