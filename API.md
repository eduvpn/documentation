# API

The portal has an API for use by applications. It is protected using OAuth 2.0
[[RFC 6749](https://tools.ietf.org/html/rfc6749), 
[RFC 6750](https://tools.ietf.org/html/rfc6750)] and uses the same 
authentication mechanism as the portal itself.

The OAuth and API endpoints can be discovered by requesting a JSON document
from the instance. Assuming the instance is located at `vpn.example`, the 
document can be retrieved from `https://vpn.example/info.json`. 

The contents look like this:

    {
        "api_endpoint": "https://vpn.example/portal/api",
        "api_version": "0.1",
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

### Pool List

**SUBJECT TO CHANGE**

This call will show the available VPN pools for this instance. This will allow
the application to show the user which pools are available and some basic 
information, e.g. whether or not two-factor authentication is enabled.

    $ curl -H "Authorization: Bearer abcdefgh" \
        https://vpn.example/portal/api/pool_list

The response looks like this:

    {
        "data": {
            "pool_list": [
                {
                    "displayName": "Internet Access",
                    "poolId": "internet",
                    "twoFactor": false
                }
            ]
        }
    }

### Create a Configuration

**SUBJECT TO CHANGE**

    $ curl -H "Authorization: Bearer abcdefgh" \
        -d "configName=MyConfig&poolId=internet" \
        https://vpn.example/portal/api/create_config

This will send a HTTP POST to the API endpoint, `/create_config` with the 
parameters `configName` and `poolId` to indicate for which pool a configuration
is downloaded. The `configName` MUST be unique per user.

The acceptable values for `poolId` can be discovered using the `/pool_list` 
call.

The response will be an OpenVPN configuration file.

### System Messages

**SUBJECT TO CHANGE**
**NOT YET IMPLEMENTED**

    $ curl -H "Authorization: Bearer abcdefgh" \
        https://vpn.example/portal/api/system_messages

The application is able to access the `system_messages` endpoint to see if 
there are any notifications available. Currently this can be a simple plain 
text message. In the future other types of notifications can be added, like 
requesting a configuration change in the client.

    {
        "data": {
            "messages": [
                {
                    "date": "2007-04-05T14:30Z",
                    "content": "Maintenance between 7 and 8am on Thursday October 26th 2016 (CEST). The VPN will be unavailable during this time",
                    "type": "notification"
                }
            ]
        }
    }

The date/time is in 
[ISO 8601](https://en.wikipedia.org/wiki/ISO_8601#Combined_date_and_time_representations) 
format.

**TODO**: the notifications will be kept forever, or only current ones? Should
the client keep a list of 'viewed' notifications? Do we need to add a guid 
field or something similar that is unique for every notification? How often do
we need to query the `system_messages` endpoint?

### User Messages

**SUBJECT TO CHANGE**
**NOT YET IMPLEMENTED**

    $ curl -H "Authorization: Bearer abcdefgh" \
        https://vpn.example/portal/api/user_messages

These are messages specific to the user. It can contain a message about the 
user being blocked, or other personal messages from the VPN administrator.

    {
        "data": {
            "messages": [
                {
                    "date": "2007-04-05T14:30Z",
                    "content": "Your account has been blocked because of a malware infection, please contact support at support@example.org",
                    "type": "notification"
                }
            ]
        }
    }

Same considerations apply as for the `system_messages` call.

# Registration

The OAuth client application can be registered in the user portal, in the 
following file, where `vpn.example` is the instance you want to configure:

    /etc/vpn-user-portal/vpn.example/config.yaml

The following options are available:

    enableOAuth: false
    #enableOAuth: true
    # OAuth 2.0 consumers
    apiConsumers:
        vpn-companion:
            redirect_uri: 'vpn://import/callback'

Here `vpn-companion` is the `client_id`.
