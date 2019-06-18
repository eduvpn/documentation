# Discovery 3.0

**NOTE**: this is currently a proposal, feedback welcome!

To make it possible for the native eduVPN apps to figure out which particular 
VPN server is available for which particular user we implement a _discovery_ 
service. This is NOT to be confused with the discovery service as used with 
e.g. SAML.

The native application can query this service, i.e. open the browser to the
discovery service URL and after the user picks their IdP gets a URL back that
contains information about VPN servers available for that particular IdP.

## Request

The native application opens an external browser, or internal "web view" to 
the discovery URL, for example:

    https://disco.eduvpn.org/?return_to=org.eduvpn.app.ios://callback/disco&nonce=6CBlXTnsRRPOcjL0jHarTcH2cP-wKyQFCan99rkygLs

The `return_to` parameter contains the URL to which the application wants the
discovery service to return after the discovery step. This URL MUST be 
registered in the discovery service beforehand! The URL MUST not contain a 
"query" part. The `nonce` parameter MUST be a Base64 URL encoded 
cryptographically randomly generate 256 (32 bytes) string without padding 
(See RFC XXXX).

## Response

After the user selected their IdP, the entity ID of this IdP is returned to 
the specified `return_to` address in the request, for example:

    org.eduvpn.app.ios://callback/disco?server_list=https://disco.eduvpn.org/list/https%3A%2F%2Fidp.surfnet.nl.json&nonce=6CBlXTnsRRPOcjL0jHarTcH2cP-wKyQFCan99rkygLs

The `nonce` received MUST exactly match the `nonce` that was part of the 
request.

The native application needs to register this `return_to` URL, in this case
`org.eduvpn.app.ios://callback/disco` in its application manifest in order to 
be able to be opened as soon as this URL is called from the discovery service.

The native app MAY use an embedded "web view" to enhance the user experience 
by not opening an external browser and listening for the callback.

The app MUST cache the `server_list` URL and refresh it periodically, e.g. once
per day by storing the originally retrieved `ETag` and using that with a `HEAD`
request to figure out whether the file changed.

## Server List

The app can now retrieve the URL 
`https://disco.eduvpn.org/list/https%3A%2F%2Fidp.surfnet.nl.json`. It looks 
like this:

    {
        "server_list": {
            "https://eduvpn1.eduvpn.de": {
                "api_authz_source": "https://nl.eduvpn.org",
                "display_name": {
                    "de-DE": "Deutschland",
                    "en-US": "Germany",
                    "nb-NO": "Tyskland",
                    "nl-NL": "Duitsland"
                },
                "logo_uri": "https://static.eduvpn.nl/disco/img/de.png"
            },
            "https://nl.eduvpn.org": {
                "api_authz_source": "https://nl.eduvpn.org",
                "display_name": {
                    "da-DK": "Holland",
                    "en-US": "The Netherlands",
                    "nb-NO": "Nederland",
                    "nl-NL": "Nederland"
                },
                "logo_uri": "https://static.eduvpn.nl/disco/img/nl.png"
            },
            "https://surfnet.eduvpn.nl": {
                "api_authz_source": "https://surfnet.eduvpn.nl",
                "display_name": {
                    "nl_NL": "SURFnet"
                },
                "logo_uri": "https://static.eduvpn.nl/disco/img/surfnet.png"
            }
        }
    }

As you can notice, this a list of all the available VPN servers for this 
particular IdP (`https://idp.surfnet.nl`).

The `api_authz_source` indicates at which server to obtain an OAuth token for
use with this particular server. So in this case, if the user decides to 
connect to "Germany", it needs an access_token from `https://nl.eduvpn.org` 
first.

The "key" of the `server_list` is the "Origin" of the server. It contains the
scheme, the host and optionally port. It does NOT contain a path. 

Information about the particular server can be obtained by requesting 
`https://nl.eduvpn.org/.well-known/lc-vpn`.

The `display_name` is a map from language code to string. The `logo_uri` is 
either an absolute URL to an common image format, or a "data URI". Both keys 
are OPTIONAL. In case they are missing, they SHOULD be taken from the server's 
`.well-known/lc-vpn` resource. The `display_name` and `logo_uri` if available
from the (global) discovery file MUST be used if available.

If the `display_name` is not available, the "Origin" of the server MUST be used 
as its display name. If the `logo_uri` is not available it is up to the 
application to handle this case and e.g. show a "default logo".

# Open Issues

- do we want to sign this file like the "Disco 1.0" files?
- not sure if the `api_authz_source` is such a good idea? Any other ideas?
- do we need to include a `version` query parameter? Or can we just add this
  later when needed? Maybe better to do it immediately...
