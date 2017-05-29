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
* [OAuth 2.0 for Native Apps](https://tools.ietf.org/html/draft-ietf-oauth-native-apps-07);
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

## Instance Discovery

For an application to discover which instances are available to show to the 
user a JSON document can be retrieved. For example eduVPN has a document 
available at `https://static.eduvpn.nl/instances.json`.

The document looks like this:

    {
        "instances": [
            {
                "base_uri": "https:\/\/surf.eduvpn.nl\/",
                "display_name": "SURF",
                "logo_uri": "https:\/\/static.eduvpn.nl\/img\/surfnet.png"
            },
         
            ...

        ],
        "seq": 25,
        "signed_at": "2017-05-11 14:55:03",
        "version": 1
    }

The `base_uri` can be used to perform the API Discovery, see below. The other
fields can be used to enhance the UI for users using the application by 
providing a logo and a human readable name for the instance. Users also SHOULD
have the option to provide their own `base_uri` in the application UI if their
favorite provider is not listed.

### Validation

When downloading the instance discovery file, you also MUST fetch the signature 
file, which is located in the same folder, but has the `.sig` extension, e.g. 
`https://static.eduvpn.nl/instances.json.sig`.

Using [libsodium](https://download.libsodium.org/doc/) you can verify the 
signature using the public key(s) that you hard code in your application. The 
signature file contains the Base64-encoded signature. See 
[this](https://download.libsodium.org/doc/bindings_for_other_languages/) 
document for various language bindings.

The flow:

1. Download `instances.json`;
2. Download `instances.json.sig`;
3. Verify the signature using libsodium and the public key stored in your 
   application
4. If you already have a cached version, verify the `seq` field of the new file
   is higher than the `seq` in the cached copy (see Caching section);
5. Overwrite the cached version if appropriate.
 
## API Discovery

The OAuth and API endpoints can be discovered by requesting a JSON document
from the instance, based on the `base_uri` from the "Instance Discovery" 
above. This is the content of `https://demo.eduvpn.nl/info.json`:

    {
        "api": {
            "http://eduvpn.org/api#1": {
                "authorization_endpoint": "https://demo.eduvpn.nl/portal/_oauth/authorize",
                "create_config": "https://demo.eduvpn.nl/portal/api.php/create_config",
                "profile_list": "https://demo.eduvpn.nl/portal/api.php/profile_list",
                "system_messages": "https://demo.eduvpn.nl/portal/api.php/system_messages",
                "user_messages": "https://demo.eduvpn.nl/portal/api.php/user_messages"
            },
            "http://eduvpn.org/api#2": {
                "api_base_uri": "https://demo.eduvpn.nl/portal/api.php",
                "authorization_endpoint": "https://demo.eduvpn.nl/portal/_oauth/authorize",
                "token_endpoint": "https://demo.eduvpn.nl/portal/oauth.php/token"
            }
        }
    }


**NOTE**: new implementations MUST use `http://eduvpn.org/api#2`!

## Authorization Request 

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

## Using the API

Using the `access_token` some additional server information can be obtained, 
as well as configurations created. The examples below will use cURL to show 
how to use the API.

If the API responds with a 401 it may mean that the user revoked the 
application's permission. Permission to use the API needs to be requested again
in that case. The URLs MUST be taken from the `info.json` document described
above.

### Profile List

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

### User Info

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

### Create a Configuration

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

### Create a Key Pair 

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

### Profile Config

**API VERSION 2 ONLY**

Only get the profile configuration without certificate and private key.

    $ curl -H "Authorization: Bearer abcdefgh" \
        "https://demo.eduvpn.nl/portal/api.php/profile_config?profile_id=internet"

The response will be an OpenVPN configuration file without the `<cert>` and 
`<key>` fields.

### System Messages

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

### User Messages

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

## Flow

See [Application Flow](APP_FLOW.md).

# Authorization

In the scenario above, every instance in the discovery file runs their own 
OAuth server, so for each instance a new token needs to be obtained.

In order to support sharing access tokens between instances, i.e. guest usage,
we introduce three client modes of operation:

1. **Local**: every instance has their own OAuth server;
2. **Federated**: there is one central OAuth server, all instances accept 
   tokens from this OAuth server;
3. **Distributed**: there is no central OAuth server, tokens from all instances 
   can be used at all (other) instances.

The `client_mode` key indicates which mode the client should operate in. The 
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
file is enough and can then be used at all of the instances. Typically the user
has the ability to obtain only an access token at one of the listed instances,
so the user MUST choose first which of the instances they have an account at. 

This is a bit messy from a UX perspective, as the user does not necessarily 
know for which instance they have an account. In case of eduVPN this will most
likely be the instance operated in their institute's home country. So students
of the University of Amsterdam will have to choose "The Netherlands".

The application will need to refresh the access token at the original OAuth 
server it was obtained from. The API discovery still needs to take place, both
for refreshing this token (when the time comes) as well as for finding the 
API endpoint at the target instance.

# Caching

There are two types of discovery:

1. Instance Discovery
2. API Discovery

Both are JSON files that can be cached. It MUST be possible for the user to 
trigger a reload, i.e. get new copies of the cached files. This can be
implemented for example using a button, or at the very least, an application 
restart.

The Instance Discovery files are also signed using public key cryptography, the
signature MUST be verified and the value of the `seq` key of the verified file 
MUST be `>=` the cached copy. It MUST NOT be possible to "rollback", so for the
instances discovery the cached copy MUST be retained.

The API discovery files do not currently have a signature and `seq` key, but 
MAY in the future.

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

* [OAuth 2.0 for Native Apps](https://tools.ietf.org/html/draft-ietf-oauth-native-apps-07)
* [Proof Key for Code Exchange by OAuth Public Clients](https://tools.ietf.org/html/rfc7636)

In particular, the use of PKCE is enforced, and the `response_type` MUST be 
`code` for the authorization request.

In version 2, the `instances.json` is also signed, so the signature MUST be 
validated by the consuming client.
