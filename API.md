# API

The portal has an API for use by applications. It is protected using OAuth 2.0,
the following documents are relevant for implementations:

* [The OAuth 2.0 Authorization Framework](https://tools.ietf.org/html/rfc6749);
* [The OAuth 2.0 Authorization Framework: Bearer Token Usage](https://tools.ietf.org/html/rfc6750);
* [OAuth 2.0 for Native Apps](https://tools.ietf.org/html/draft-ietf-oauth-native-apps-07);
* [Proof Key for Code Exchange by OAuth Public Clients](https://tools.ietf.org/html/rfc7636)

## Instance Discovery

A list of all available instances is available on 
`https://static.eduvpn.nl/instances.json`. That document can be used to 
discover the various instances that should be listed in the application.

    {
        "instances": [
            ...

            {
                "base_uri": "https://demo.eduvpn.nl/",
                "display_name": "eduVPN Demo",
                "logo_uri": "https://static.eduvpn.nl/demo.png"
            },

            ...
        ],
        "version": 1
    }

The `base_uri` can be used to perform the API Discovery, see below. The other
fields can be used to improve the UI for users using the application by 
providing a logo and a human readable name for the instance.

## API Discovery

The OAuth and API endpoints can be discovered by requesting a JSON document
from the instance, either based on the `base_uri` from the Instance Discovery,
or from a "domain name". Assuming the instance is located at `vpn.example`, 
the document can be retrieved from `https://vpn.example/info.json`.

    {
        "api": {
            "http://eduvpn.org/api#1": {
                "authorization_endpoint": "https://vpn.example/portal/_oauth/authorize",
                "create_config": "https://vpn.example/portal/api.php/create_config",
                "profile_list": "https://vpn.example/portal/api.php/profile_list",
                "system_messages": "https://vpn.example/portal/api.php/system_messages",
                "user_messages": "https://vpn.example/portal/api.php/user_messages"
            },
            "http://eduvpn.org/api#2": {
                "authorization_endpoint": "https://vpn.example/portal/_oauth/authorize",
                "create_certificate": "https://vpn.example/portal/api.php/create_certificate",
                "create_config": "https://vpn.example/portal/api.php/create_config",
                "profile_config": "https://vpn.example/portal/api.php/profile_config",
                "profile_list": "https://vpn.example/portal/api.php/profile_list",
                "system_messages": "https://vpn.example/portal/api.php/system_messages",
                "token_endpoint": "https://vpn.example/portal/_oauth/token",
                "user_messages": "https://vpn.example/portal/api.php/user_messages"
            }
        }
    }

**NOTE**: new implementations MUST use `http://eduvpn.org/api#2`.

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

There are a number of example applications that implement the OAuth 2.0 
"Native Apps" profile like described above in a secure fashion:

* [Android](https://github.com/openid/AppAuth-Android)
* [iOS](https://github.com/openid/AppAuth-iOS)
* [Windows](https://github.com/googlesamples/oauth-apps-for-windows)

## Using the API

Using the `access_token` some additional server information can be obtained, 
as well as configurations created. The examples below will use cURL to show 
how to use the API.

If the API responds with a 401 it may mean that the user revoked the 
application's permission. Permission to use the API needs to be request again
in that case. The URLs MUST be taken from the `info.json` document described
above.

### Profile List

This call will show the available VPN profiles for this instance. This will 
allow the application to show the user which profiles are available and some 
basic information, e.g. whether or not two-factor authentication is enabled.

    $ curl -H "Authorization: Bearer abcdefgh" \
        https://vpn.example/portal/api.php/profile_list

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

A call that can be used to get a full working OpenVPN configuration file 
including certificate and key. This MUST NOT be used by "Native Apps". Instead
the separate `/create_certificate` and `/profile_config` MUST be used as they 
allow for obtaining a new configuration without generating a new 
certificate/key.

    $ curl -H "Authorization: Bearer abcdefgh" \
        -d "display_name=eduVPN%20for%20Android&profile_id=internet" \
        https://vpn.example/portal/api.php/create_config

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
        https://vpn.example/portal/api.php/create_certificate

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
        "https://vpn.example/portal/api.php/profile_config?profile_id=internet"

The response will be an OpenVPN configuration file.

### System Messages

    $ curl -H "Authorization: Bearer abcdefgh" \
        https://vpn.example/portal/api.php/system_messages

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
        https://vpn.example/portal/api.php/user_messages

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

The OAuth client application(s) can be registered in the user portal, in the 
following file, where `vpn.example` is the instance you want to configure:

    /etc/vpn-user-portal/vpn.example/config.php

The following options are available:

    'Api' => [
        // access_tokens expire after 3 months
        'tokenExpiry' => 3*31*24*3600,

        // OAuth 2.0 consumers
        'consumerList' => [
            // API 1 Apps
            'nl.eduvpn.app' => [
                'redirect_uri' => 'nl.eduvpn.app://import/callback',
                'response_type' => 'token',
                'display_name' => 'eduVPN for Android',
            ],
            // API 2 Apps
            //'nl.eduvpn.app.android' => [
            //    'redirect_uri' => 'nl.eduvpn.app.android://api/callback',
            //    'response_type' => 'code',
            //    'display_name' => 'eduVPN for Android',
            //],
            //'nl.eduvpn.app.windows' => [
            //    'redirect_uri' => 'nl.eduvpn.app.windows://api/callback',
            //    'response_type' => 'code',
            //    'display_name' => 'eduVPN for Windows',
            //],
        ],
    ],

Here `nl.eduvpn.app` is the `client_id`.

# Building Applications

There are a number of things to consider when building an application using 
this API. The most important being handling the OAuth 2.0 tokens and the 
VPN configurations.

1. OAuth tokens can be revoked or expire. The application will need to deal
   with this. If a token no longer works (or is about to expire) a new token
   needs to be obtained (though user interaction with the browser). In the 
   future, the "refresh token" flow will be implemented for dealing with token
   expiry;
2. VPN server configuration can change which would require an update to the 
   configuration of the client. This does not necessarily mean a new client 
   certificate is required as well. It could for example be a change in allowed
   encryption ciphers, or additional/new hosts to connect to;
3. VPN (client) certificates can expire. The application needs to deal with 
   obtaining a new certificate if the old one expired, or is about to expire;
4. VPN (CA) certificates can expire. By default, the VPN server has a CA that 
   expires after 5 years. If this happens, a new client certificate and new 
   configuration needs to be obtained.

## Flow

TBD.

# Changelog

In API version 2, two calls were added:

* `POST` to `/create_certificate` to create a `private_key` and 
  `certificate` for an instance to be used with all profiles. This makes it 
  possible to use one key pair per instance;
* `GET` to `/profile_config` to obtain only the configuration file, without 
  generating a key pair. This means the configuration can easily be refetched 
  in case an update is needed without creating a new key pair;

For security reasons, API 2 switches to the _authorization code_ flow, together 
with mitigations described in the following documents:

* [OAuth 2.0 for Native Apps](https://tools.ietf.org/html/draft-ietf-oauth-native-apps-07)
* [Proof Key for Code Exchange by OAuth Public Clients](https://tools.ietf.org/html/rfc7636)

In particular, the use of PKCE is enforced, and the `response_type` MUST be 
`code` for the authorization request.
