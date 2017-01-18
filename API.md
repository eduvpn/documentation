# API

The portal has an API for use by applications. It is protected using OAuth 2.0
[[RFC 6749](https://tools.ietf.org/html/rfc6749), 
[RFC 6750](https://tools.ietf.org/html/rfc6750)] and uses the same 
authentication mechanism as the portal itself.

The OAuth and API endpoints can be discovered by requesting a JSON document
from the instance. Assuming the instance is located at `vpn.example`, the 
document can be retrieved from `https://vpn.example/info.json`. 

**New implementations MUST use API version 2**.

### Version 1

    {
        "api": {
            "create_config": "https://vpn.example/portal/api/create_config",
            "profile_list": "https://vpn.example/portal/api/profile_list",
            "system_messages": "https://vpn.example/portal/api/system_messages",
            "user_messages": "https://vpn.example/portal/api/user_messages"
        },
        "version": 1,
        "authorization_endpoint": "https://vpn.example/portal/_oauth/authorize"
    }

### Version 2

    {
        "api": {
            "profile_config": "https://vpn.example/portal/api/profile_config",
            "create_certificate": "https://vpn.example/portal/api/create_certificate",
            "profile_list": "https://vpn.example/portal/api/profile_list",
            "system_messages": "https://vpn.example/portal/api/system_messages",
            "user_messages": "https://vpn.example/portal/api/user_messages"
        },
        "version": 2,
        "authorization_endpoint": "https://vpn.example/portal/_oauth/authorize"
    }

## Authorization Request 

The `authorization_endpoint` is then used to obtain an access token by 
providing it with the following query parameters, they are all required:

* `client_id`: the ID that was registered, see below;
* `redirect_uri`; the URL that was registered, see below;
* `response_type`: this is always `token`;
* `scope`: this is always `config`;
* `state`: a cryptographically secure random string, to avoid CSRF;

The `authorization_endpoint` URL together with the query parameters is then 
openened using a browser, and eventually redirected to the `redirect_uri` where
the application can extract the `access_token` field from the URL fragement. 
The `state` parameter is also added to the fragement of the `redirect_uri` and 
MUST be the same as the `state` parameter value of the initial request.

## Using the API

Using the `access_token` some additional server information can be obtained, 
as well as configurations created. The examples below will use cURL to show 
how to use the API.

If the API responds with a 401 it may mean that the user revoked the 
application's permission. Permission to use the API needs to be request again
in that case.

### Profile List

This call will show the available VPN profiles for this instance. This will 
allow the application to show the user which profiles are available and some 
basic information, e.g. whether or not two-factor authentication is enabled.

    $ curl -H "Authorization: Bearer abcdefgh" \
        https://vpn.example/portal/api/profile_list

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

### Create a Configuration

**DEPRECATED IN API VERSION 2**

    $ curl -H "Authorization: Bearer abcdefgh" \
        -d "display_name=eduVPN%20for%20Android&profile_id=internet" \
        https://vpn.example/portal/api/create_config

This will send a HTTP POST to the API endpoint, `/create_config` with the 
parameters `display_name` and `profile_id` to indicate for which profile a 
configuration is downloaded.

The acceptable values for `profile_id` can be discovered using the 
`/profile_list` call.

The response will be an OpenVPN configuration file.

### Create a Certificate 

**API VERSION 2 ONLY**

    $ curl -H "Authorization: Bearer abcdefgh" \
        -d "display_name=eduVPN%20for%20Android" \
        https://vpn.example/portal/api/create_certificate

This will send a HTTP POST to the API endpoint, `/create_certificate` with the 
parameter `display_name`. It will only create a certificate and return the 
public and private key.

    {
        "create_certificate": {
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

### Profile Config

**API VERSION 2 ONLY**

Only get the profile configuration without certificate and private key.

    $ curl -H "Authorization: Bearer abcdefgh" \
        "https://vpn.example/portal/api/profile_config?profile_id=internet"

The response will be an OpenVPN configuration file.

### System Messages

    $ curl -H "Authorization: Bearer abcdefgh" \
        https://vpn.example/portal/api/system_messages

The application is able to access the `system_messages` endpoint to see if 
there are any notifications available. These are the types of messages:

* `notification`: a plain text message in the `message` field;
* `motd`: a plain text "message of the day" (MotD) of the service, to be 
  displayed to users on login or when establishing a connection to the VPN;
* `maintenance`: an (optional) plain text message in the `message` field
  and a `begin` and `end` field with the timestamp;

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
        https://vpn.example/portal/api/user_messages

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

# Registration

The OAuth client application can be registered in the user portal, in the 
following file, where `vpn.example` is the instance you want to configure:

    /etc/vpn-user-portal/vpn.example/config.php

The following options are available:

    'enableOAuth' => true,
    // OAuth 2.0 consumers
    'apiConsumers' => [
        'nl.eduvpn.app' => [
            'redirect_uri' => 'nl.eduvpn.app://import/callback',
            'response_type' => 'code',
            'display_name' => 'eduVPN for Android'
        ],
    ],

Here `nl.eduvpn.app` is the `client_id`.

# Changelog

In API version 2, two calls were added:

* `POST` to `/create_certificate` to create a `private_key` and 
  `certificate` for an instance to be used with all profiles. This makes it 
  possible to use one key pair per instance;
* `GET` to `/profile_config` to obtain only the configuration file, without 
  generating a key pair. This means the configuration can easily be refetched 
  in case an update is needed without creating a new key pair;

The following call is **DEPRECATED** and will be removed in the future:

* `POST` to `/create_config`, use the newly added API calls

For security reasons, API 2 switches to the _authorization code_ flow, together 
with mitigations described in the following documents:

* [OAuth 2.0 for Native Apps](https://tools.ietf.org/html/draft-ietf-oauth-native-apps-07)
* [Proof Key for Code Exchange by OAuth Public Clients](https://tools.ietf.org/html/rfc7636)

In particular, the use of PKCE is enforced, and the `response_type` MUST be 
`code` for the authorization request.
