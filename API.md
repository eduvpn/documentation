# API

The portal has an API for use by applications. It is protected using OAuth 2.0
[[RFC 6749](https://tools.ietf.org/html/rfc6749), 
[RFC 6750](https://tools.ietf.org/html/rfc6749)] and uses the same 
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
* `scope`: this can be `create_config`, `server_pools`, or both;
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

### Pool List

**SUBJECT TO CHANGE**

This call will show the available VPN pools for this instance. This will allow
the application to show the user which pools are available and some basic 
information, e.g. whether or not two-factor authentication is enabled.

This request requires the scope `pool_list`.

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

This request requires the scope `create_config`.

    $ curl -H "Authorization: Bearer abcdefgh" \
        -d "configName=MyConfig&poolId=internet" \
        https://vpn.example/portal/api/create_config

This will send a HTTP POST to the API endpoint, `/create_config` with the 
parameters `configName` and `poolId` to indicate for which pool a configuration
is downloaded. The `configName` MUST be unique per user.

The acceptable values for `poolId` can be discovered using the `/server_pools` 
call.

The response will be an OpenVPN configuration file.

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
            scope: ['create_config', 'pool_list']

Here `vpn-companion` is the `client_id`. The `scope` field indicated which 
scopes this client is allowed to request.
