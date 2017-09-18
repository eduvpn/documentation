# Introduction

This document describes the API provided by the VPN portal. The API can be used
by applications wanting to integrate with the VPN software to make it easy for
users to configure their VPN.

The API is pragmatic "REST", keeping things as simple as possible without 
obsessing about the proper HTTP verb. There are no `PUT` and `DELETE` requests,
just simple `GET` and `POST` requests that use "form submit". The responses 
are always `application/json` though.

# Standards

OAuth 2.0 is used to provide the API. The following documents are relevant for 
implementations and should be followed to the letter except when stated 
differently:

* [The OAuth 2.0 Authorization Framework](https://tools.ietf.org/html/rfc6749);
* [The OAuth 2.0 Authorization Framework: Bearer Token Usage](https://tools.ietf.org/html/rfc6750);
* [OAuth 2.0 for Native Apps](https://tools.ietf.org/html/draft-ietf-oauth-native-apps-11) (use latest version of specification);
* [Proof Key for Code Exchange by OAuth Public Clients](https://tools.ietf.org/html/rfc7636)

Implementing OAuth 2.0 correctly is not easy, there are a number of sample 
applications available for various platforms that can (and probably should) be 
used as a basis:

* [Android](https://github.com/openid/AppAuth-Android)
* [iOS](https://github.com/openid/AppAuth-iOS)
* [Windows](https://github.com/googlesamples/oauth-apps-for-windows)

# Definitions

A VPN service running at a particular domain is called an _instance_, e.g. 
`demo.eduvpn.nl`. An instance can have multiple _profiles_, e.g. 
`internet` and `office`.

# Instance Discovery

For an application to discover which instances are available to show to the 
user a JSON document can be retrieved. For example eduVPN has those JSON 
documents available at 
[https://static.eduvpn.nl/disco/](https://static.eduvpn.nl/disco/).

Typically an application will use one or two discovery files for retrieving the
list of instances. It SHOULD be possible to configure additional sources. The 
URL of the discovery file could be used to map it to certain branding and
UI texts in the application.

## Format

The base JSON document looks like this:

    {
        "authorization_type": "distributed",
        "instances": [
            ...
        ]
    }

The `authorization_type` is described in the [Authorization](#authorization) 
section. 

The `instances` key has an array with objects, in the most simple form:

    {
        "base_uri": "https://demo.eduvpn.nl/",
        "display_name": "Demo VPN Provider",
        "logo": "https://static.eduvpn.nl/disco/img/demo.png"
    }

For multi language support, the values of the keys `display_name` and `logo` 
can contain multiple texts and logos depending on the language:

    {
        "base_uri": "https://demo.eduvpn.nl/",
        "display_name": {
            "en-US": "Demo VPN Provider",
            "nl-NL": "Demo VPN-aanbieder"
        },
        "logo": {
            "en-US": "https://static.eduvpn.nl/disco/img/demo.en.png",
            "nl-NL": "https://static.eduvpn.nl/disco/img/demo.nl.png"
        },
        "public_key": "Ch84TZEk4k4bvPexrasAvbXjI5YRPmBcK3sZGar71pg="
    }

Applications MUST check if the value of `display_name` and `logo` is a 
simple string, or an object. In case of an object, the language best matching
the application language SHOULD be chosen. If that language is not available, 
the application SHOULD fallback to `en-US`. If `en-US` is not available, it is
up to the application to pick one it deems best.

The `base_uri` field can be used to perform the API Discovery of the instances 
themselves, see below.

The `public_key` field is used by the VPN services for the `distributed` 
Authorization, this can be ignored by API clients.

## Validation

When downloading the instance discovery file, you also MUST fetch the signature 
file, which is located in the same folder, but has the `.sig` extension, e.g. 
`https://static.eduvpn.nl/disco/secure_internet.json.sig`.

Using [libsodium](https://download.libsodium.org/doc/) you can verify the 
signature using the public key(s) that you hard code in your application. The 
signature file contains the Base64-encoded signature. See 
[this](https://download.libsodium.org/doc/bindings_for_other_languages/) 
document for various language bindings.

The flow:

1. Download `secure_internet.json`;
2. Download `secure_internet.json.sig`;
3. Verify the signature using libsodium and the public key stored in your 
   application
4. If you already have a cached version, verify the `seq` field of the new file
   is higher than the `seq` in the cached copy (see Caching section);
5. Overwrite the cached version if appropriate.

The `signed_at` key is just informative and cannot be relied on to be 
available.

The public key that is currently used is 
`E5On0JTtyUVZmcWd+I/FXRm32nSq8R2ioyW7dcu/U88=`. This is a Base64-encoded 
[Ed25519](https://en.wikipedia.org/wiki/Curve25519) public key.

# API Discovery

The OAuth and API endpoints can be discovered by requesting a JSON document
from the instance, based on the `base_uri` from the "Instance Discovery" 
above. This is the content of `https://demo.eduvpn.nl/info.json`:

    {
        "api": {
            "http://eduvpn.org/api#2": {
                "api_base_uri": "https://demo.eduvpn.nl/portal/api.php",
                "authorization_endpoint": "https://demo.eduvpn.nl/portal/_oauth/authorize",
                "token_endpoint": "https://demo.eduvpn.nl/portal/oauth.php/token"
            }
        }
    }

# Authorization Request 

The `authorization_endpoint` is then used to obtain an access token by 
providing it with the following query parameters, they are all required, 
despite some of them being OPTIONAL according to the OAuth specification:

* `client_id`: the ID that was registered, see below;
* `redirect_uri`; the URL that was registered, see below;
* `response_type`: always `code`;
* `scope`: this is always `config`;
* `state`: a cryptographically secure random string, to avoid CSRF;
* `code_challenge_method`: always `S256`; 
* `code_challenge`: the code challenge (see RFC 7636).

The `authorization_endpoint` URL together with the query parameters is then 
opened using a browser, and eventually redirected to the `redirect_uri` where
the application can extract the `access_token` field from the URL fragment. 
The `state` parameter is also added to the fragment of the `redirect_uri` and 
MUST be the same as the `state` parameter value of the initial request. The 
response also includes `expires_in` that indicates when the access token 
will expire.

# Using the API

Using the `access_token` some additional server information can be obtained, 
as well as configurations created. The examples below will use cURL to show 
how to use the API.

If the API responds with a 401 it may mean that the user revoked the 
application's permission. Permission to use the API needs to be requested again
in that case. The URLs MUST be taken from the `info.json` document described
above.

## Profile List

This call will show the available VPN profiles for this instance. This will 
allow the application to show the user which profiles are available and some 
basic information, e.g. whether or not two-factor authentication is enabled.

    $ curl -H "Authorization: Bearer abcdefgh" \
        https://demo.eduvpn.nl/portal/api.php/profile_list

The response looks like this:

    {
        "profile_list": {
            "data": [
                {
                    "display_name": "Internet Access",
                    "profile_id": "internet",
                    "two_factor": false
                }
            ],
            "ok": true
        }
    }

The `display_name` can be multi language as well, e.g.:

    "display_name": {
        "nl-NL": "Internettoegang",
        "en-US": "Internet Access"
    }

The same rules for detecting multi language apply as in 
[Instance Discovery](#instance-discovery) apply here.

In case of 2FA, the `two_factor` field is set to `true`. In that case, there 
MAY be a `two_factor_method` field that indicates which 2FA methods are 
accepted by the server. This is an array. If the field is missing, all 2FA 
methods are supported. Empty array means no 2FA method is supported, but 2FA 
is still enabled, making it impossible to authenticate.

## User Info

**API VERSION 2 ONLY**

This call will show information about the user, whether or not the user is 
enrolled for 2FA and whether or not the user is prevented from connecting to
the VPN.

    $ curl -H "Authorization: Bearer abcdefgh" \
        https://demo.eduvpn.nl/portal/api.php/user_info

The response looks like this:

    {
        "user_info": {
            "data": [
                {
                    "two_factor_enrolled": false,
                    "is_disabled": false
                }
            ],
            "ok": true
        }
    }

If `two_factor_enrolled` is `true`, there MAY be a `two_factor_enrolled_with` 
field. The `two_factor_enrolled_with` values can be `[]`, one of `yubi` or 
`totp` or both. This field indicates for which 2FA methods the user is 
enrolled.

## Create a Configuration

A call that can be used to get a full working OpenVPN configuration file 
including certificate and key. This MUST NOT be used by "Native Apps". Instead
the separate `/create_keypair` and `/profile_config` MUST be used as they 
allow for obtaining a new configuration without generating a new 
certificate/key.

    $ curl -H "Authorization: Bearer abcdefgh" \
        -d "display_name=eduVPN%20for%20Android&profile_id=internet" \
        https://demo.eduvpn.nl/portal/api.php/create_config

This will send a HTTP POST to the API endpoint, `/create_config` with the 
parameters `display_name` and `profile_id` to indicate for which profile a 
configuration is downloaded.

The acceptable values for `profile_id` can be discovered using the 
`/profile_list` call as shown above.

The response will be an OpenVPN configuration file that can be used "as-is".

## Create a Key Pair 

**API VERSION 2 ONLY**

    $ curl -H "Authorization: Bearer abcdefgh" \
        -d "display_name=eduVPN%20for%20Android" \
        https://demo.eduvpn.nl/portal/api.php/create_keypair

This will send a HTTP POST to the API endpoint, `/create_keypair` with the 
parameter `display_name`. It will only create a public and private key and
return them.

    {
        "create_keypair": {
            "data": {
                "certificate": "-----BEGIN CERTIFICATE----- ... -----END CERTIFICATE-----",
                "private_key": "-----BEGIN PRIVATE KEY----- ... -----END PRIVATE KEY-----"
            },
            "ok": true
        }
    }

The certificate and the private key need to be combined with a profile 
configuration as `<cert>...</cert>` and `<key>...</key>` that can be obtained 
through the `/profile_config` call.

**NOTE**: a certificate is valid for ALL _profiles_ of a particular _instance_, 
so if an instance has e.g. the profiles `internet` and `office`, only one 
certificate is required!

## Profile Config

**API VERSION 2 ONLY**

Only get the profile configuration without certificate and private key.

    $ curl -H "Authorization: Bearer abcdefgh" \
        "https://demo.eduvpn.nl/portal/api.php/profile_config?profile_id=internet"

The response will be an OpenVPN configuration file without the `<cert>` and 
`<key>` fields.

## System Messages

    $ curl -H "Authorization: Bearer abcdefgh" \
        https://demo.eduvpn.nl/portal/api.php/system_messages

The application is able to access the `system_messages` endpoint to see if 
there are any notifications available. These are the types of messages:

* `notification`: a plain text message in the `message` field;
* `motd`: a plain text "message of the day" (MotD) of the service, to be 
  displayed to users on login or when establishing a connection to the VPN;
* `maintenance`: an (optional) plain text message in the `message` field
  and a `begin` and `end` field with the time stamp;

All message types have the `date_time` field indicating the date the message 
was created. This can be used as a unique identifier.

The `date_time`, `begin` and `end` fields are in
[ISO 8601](https://en.wikipedia.org/wiki/ISO_8601#Combined_date_and_time_representations) 
format. Note that seconds are also included.

An example:

    {
        "system_messages": {
            "data": [
                {
                    "message": "Hello World!",
                    "date_time": "2016-12-02T10:42:08Z",
                    "type": "notification"
                }
            ],
            "ok": true
        }
    }

The messages of type `maintenance` will be available through the API until they 
are no longer relevant. Messages of type `notification` will be always 
available through the API until an administrator (manually) removes it.

The same rules for detecting multi language (for `message`) apply as in 
[Instance Discovery](#instance-discovery) apply here.

## User Messages

    $ curl -H "Authorization: Bearer abcdefgh" \
        https://demo.eduvpn.nl/portal/api.php/user_messages

These are messages specific to the user. It can contain a message about the 
user being blocked, or other personal messages from the VPN administrator.

These are the types of messages:

* `notification`: a plain text message in the `message` field;

An example:

    {
        "user_messages": {
            "data": [
                {
                    "message": "Your account has been disabled. Please contact support.",
                    "date_time": "2016-12-02T10:43:10Z",
                    "type": "notification"
                }
            ],
            "ok": true
        }
    }

Same considerations apply as for the `system_messages` call.

# Flow

See [Application Flow](app/APP_FLOW.md).

# Authorization

In the scenario above, every instance in the discovery file runs their own 
OAuth server, so for each instance a new token needs to be obtained.

In order to support sharing access tokens between instances, e.g. for guest 
usage, we introduce three "types" of authorization:

1. **local**: every instance has their own OAuth server;
2. **federated**: there is one central OAuth server, all instances accept 
   tokens from this OAuth server;
3. **distributed**: there is no central OAuth server, tokens from all instances 
   can be used at all (other) instances.

The `authorization_type` key indicates which type is used. The supported 
values are `local`, `federated` or `distributed` mapping to the three modes
described above.

## Local

See API Discovery section above for determining the OAuth endpoints. The 
application MUST store the obtained access token and bind it to the instance
the token was obtained from. If a user wants to use multiple VPN instances, a 
token MUST be obtained from all of them individually.

## Federated

Here there is one central OAuth server that MUST be used. The OAuth server is 
specified in the discovery file in the `authorization_endpoint` and 
`token_endpoint` keys. When API discovery is performed, the keys for 
`authorization_endpoint` and `token_endpoint` for the specific instance MUST
be ignored. Refreshing access tokens MUST also be done at the central server.

## Distributed

Obtaining an access token from any of the instances listed in the discovery 
file is enough and can then be used at all the instances. Typically the user
has the ability to obtain only an access token at one of the listed instances, 
because only there they have an account, so the user MUST choose first which 
of the instances they have an account at. 

This is a bit messy from a UX perspective, as the user does not necessarily 
know for which instance they have an account. In case of eduVPN this will most
likely be the instance operated in their institute's home country. So students
of the University of Amsterdam will have to choose "The Netherlands" first.

When API discovery is performed, the keys for 
`authorization_endpoint` and `token_endpoint` for the specific instance MUST
be ignored. Refreshing access tokens MUST also be done at the original OAuth
server that was used to obtain the access token.

# Caching

There are two types of discovery:

1. Instance Discovery
2. API Discovery

Both are JSON files that can be cached. In addition to this, also the instance 
logos can be cached in the application to speed up displaying the UI. The 
`If-None-Match` or `If-Modified-Since` HTTP header can be used to retrieve 
updates.

The user SHOULD be able to clear all cache in the application to force 
reloading everything.

The Instance Discovery files are also signed using public key cryptography, the
signature MUST be verified and the value of the `seq` key of the verified file 
MUST be `>=` the cached copy. It MUST NOT be possible to "rollback", so for the
instances discovery the cached copy MUST be retained.

The API discovery files do not currently have a signature and `seq` key, but 
MAY in the future.

# Client Registration

For the official eduVPN applications, you can use the following OAuth client
configuration:

* `client_id`: `org.eduvpn.app`;
* `redirect_uri`: any of the following:
  * `org.eduvpn.app:/api/callback`;
  * `http://127.0.0.1:{PORT}/callback`;
  * `http://[::1]:{PORT}/callback`;

Here, `{PORT}` can be any port >= 1024 and <= 65535. You **MUST** use the 
`org.eduvpn.app:/api/callback` redirect URI if at all possible on your 
platform.

# Changelog

In API version 2, some calls were added:

* `POST` to `/create_keypair` to create a `private_key` and 
  `certificate` for an instance to be used with all profiles. This makes it 
  possible to use one key pair per instance;
* `GET` to `/profile_config` to obtain only the configuration file, without 
  generating a key pair. This means the configuration can easily be refetched 
  in case an update is needed without creating a new key pair;
* `GET` to `/user_info` to obtain user information;
* Extended authorization model in "Authorization" section.

For security reasons, API 2 switches to the _authorization code_ flow, together 
with mitigations described in the following documents:

* [OAuth 2.0 for Native Apps](https://tools.ietf.org/html/draft-ietf-oauth-native-apps-11) (use latest version of specification);
* [Proof Key for Code Exchange by OAuth Public Clients](https://tools.ietf.org/html/rfc7636)

In particular, the use of PKCE is enforced, and the `response_type` MUST be 
`code` for the authorization request.

In version 2, we have a new discovery file format, and the file is also 
signed. The signature MUST be validated by the consuming client.
