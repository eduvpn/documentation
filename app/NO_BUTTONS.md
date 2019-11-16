# Getting rid of the buttons...

**NOTE**: none of the file formats / JSON encodings are final!

We are trying to get rid of the "use case" buttons in the eduVPN apps. 
Currently the user first has to choose "Institute Access" or "Secure Internet". 
This is not easy to explain to users. It would be better when users can simply
select their institute from a list, like they are already used to from the 
existing identity federations.

The advantage here is that the user does not have to choose from a list of 
VPN servers that don't necessarily have a (direct) link to their organization.

## User Flow

In the "first run" scenario:

1. The user opens the application;

2. The user chooses their organization;

3. The app shows the available VPN servers linked to that particular 
   organization, e.g. a VPN server for "Institute Access" and a list of VPNs 
   around the world that can be used for "Secure Internet".
   
4. (Optionally) the app connects automatically to a / one of the VPN servers

The app stores the organization identifier (`org_id`) the user chooses so this 
selector step does not need to be repeated anymore. 

On subsequent runs the app immediately shows VPN servers as obtained/configured 
during the last run.

## App Flow

In the "first run" scenario:

1. Application shows available organizations and allows users to scroll/search 
   the list by name / keywords;

2. The users chooses their organization from a list;

3. The app downloads the `org_id` -> Server mapping from a web server to obtain 
   the list of VPN servers the chosen organization has access to;

5. The app adds the obtained server addresses to the app so the user can choose
   them afterwards;

6. The app automatically connects to a VPN server if specified in the 
   mapping file.

### Notes

* The app MUST allow for forgetting the chosen organization;
* The app MUST periodically (on app start?) fetch the "mapping file" to see if 
  there are any new servers available for this `orgId`;
* Servers are only ever added from the app, NEVER removed. If a server is no 
  longer available in the mapping file, the app marks this server with a 
  special tag/icon to indicate it is not listed anymore;
* Allow the user to (un)hide VPN servers they never use (anymore) or that are 
  no longer mentioned in the mapping file;
* If the mapping file is no longer available for this `orgId` this is also 
  indicated in the app, but nothing is ever removed.
* The individual VPN servers are ONLY contacted AFTER the user decides to 
  connect to it, never before. The only connection the app makes by itself 
  is fetching the mapping file on start, nothing more.
* Be careful with caching! At most cache the data until the user (fully) 
  restarts the app to avoid needing to wait 3 months before the app starts 
  working again if something changes.
* The "orgList" can be quite big, so caching for this for longer time _is_ 
  important. However, it should always be possible for the user to refresh the
  list.

## Organization file

This file is for example hosted on `https://disco.eduvpn.org/org_list.json`. If
we include all eduGAIN IdPs, we'd have ~ 3000 entries, the file is around 500kB
in that case (uncompressed).

    {
        "org_list": [
            {
                "display_name": "SURFnet bv",
                "org_id": "https://idp.surfnet.nl",
                "keyword_list": [
                    "SURFnet",
                    "bv",
                    "SURF",
                    "konijn",
                    "surf",
                    "surfnet",
                    "powered",
                    "by"
                ],
                "server_info_url": "https://disco.eduvpn.org/mapping/https%3A%2F%2Fidp.surfnet.nl.json"
            },
            {
                 ...
            }
        ]
    }

## Mapping file

Obtain the server information available servers for an `org_id` by querying the
server mentioned in `server_info_url`.

The result may look like this:

    {
        "auto_connect": {
            "base_url": "https://nl.eduvpn.org/",
            "profile_id": "default"
        },
        "secure_internet_home": "https://nl.eduvpn.org/",
        "server_list": [
            {
                "base_url": "https://surfnet.eduvpn.nl/",
                "display_name": {
                    "nl-NL": "SURFnet"
                },
                "logo_uri": {
                    "nl-NL": "https://surfnet.nl/logo.png"
                },
                "server_type": "institute_access"
            },
            {
                "base_url": "https://nl.eduvpn.org/",
                "display_name": {
                    "en-US": "The Netherlands",
                    "nl-NL": "Nederland"
                },
                "logo_uri": {
                    "en-US": "https://nl.eduvpn.org/logo.png"
                },
                "server_type": "secure_internet"
            },
            {
                "base_url": "https://guest.uninett.no/",
                "display_name": {
                    "en-US": "Norway",
                    "nl-NL": "Noorwegen"
                },
                "logo_uri": {
                    "en-US": "https://guest.uninett.no/logo.png"
                },
                "server_type": "secure_internet"
            }
        ]
    }

The servers marked with `server_type` value `institute_access` are VPN servers 
that are exclusively available for this organization. The access tokens for 
servers mentioned here are tied to each individual VPN server in this list.

The entry `secure_internet_home` entry contains the "Home" server of users of 
that organization. It will be used to obtain an access token that can be used 
at all servers of type `secure_internet`. The field `secure_internet_home` is
OPTIONAL.

The `display_name` can have a string as value, OR an object with translations 
in various languages. If the application language is not specified here, use 
`en-US`. The same is true of `logo_uri`. Note that the `logo_uri` MAY also be 
a "data URI".

The `auto_connect` entry contains a server that the application 
should automatically connect to after adding the servers to the application. 
Here "auto connect" means: obtain OAuth authorization, and connect to the 
server. If multiple profiles are available for the user, use the one mentioned 
in `profile_id`.

The `auto_connect` entry is OPTIONAL. So it does not necessarily exist!

## Organization Hint

**NOTE**: this is currently only relevant for SAML, we use IdP here instead of
organization.

Many (all?) servers that want to provide "Guest Usage" are linked to SAML 
federations. If the discovery of the user's IdP is moved to the application 
itself, opening the OAuth authorization URL may trigger another "WAYF" from 
the identify federation. 

In order to avoid the user having to choose their IdP twice, it makes sense to
be able to provide an IdP hint to the VPN server and avoid the WAYF.

OAuth does not provide a mechanism for this directly, OIDC would, but we do not
exclusively use OIDC, so we need something "vendor independent" to open the 
correct URL.

How to this exactly depends on the SAML implementation chosen by the VPN 
server. As the VPN app has no knowledge of the used authentication mechanism, 
we can provide some kind of "IdP hint". 

Typically, an SP uses the "Identity Provider Discovery Service Protocol and 
Profile". This means that a WAYF, after the user selects the IdP, returns 
to the SP. By using a special URL, we can already "choose" for the user based
on the IdP the user chose in the eduVPN app, and use the OAuth "authorize URI"
as the `return` or `ReturnTo` parameter.

For example, for `vpn.tuxed.net` the following URL can be used to trigger a 
login using the IdP `https://idp.tuxed.net/metadata` and `ReturnTo` the OAuth 
authorization URL, skipping the VPN server WAYF:

    https://vpn.tuxed.net/vpn-user-portal/_saml/login?ReturnTo=https%3A%2F%2Fvpn.tuxed.net%2Fvpn-user-portal%2F_oauth%2Fauthorize%3Fclient_id%3Dorg.eduvpn.app.windows%26redirect_uri%3Dhttp%3A%2F%2F127.0.0.1%3A12345%2Fcallback%26response_type%3Dcode%26scope%3Dconfig%26state%3D12345%26code_challenge_method%3DS256%26code_challenge%3DE9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM&IdP=https%3A%2F%2Fidp.tuxed.net%2Fmetadata

A mechanism exist to tell the app about server specific configurations, i.e. 
the `info.json` file. We can add a special key there that provides a template 
for the application to use. For example, the template for the above URL could
be:

    https://vpn.tuxed.net/vpn-user-portal/_saml/login?ReturnTo=@AUTHORIZE_URI@&IdP=@ORG_ID@

This template URL will depend on the SAML software used at the SP, and 
also on the host name of the VPN server. 

**NOTE**: the `@AUTHORIZE_URI@` MUST be already URL encoded before being used 
as a replacement for the `@AUTHORIZE_URI@` string! `@ORG_ID@` is the entity ID
of the IdP in SAML terminology, obtained from the `org_list.json`.

Example:

    {
        "api": {
            "http://eduvpn.org/api#2": {
                "api_base_uri": "https://vpn.tuxed.net/vpn-user-portal/api.php",
                "authorization_endpoint": "https://vpn.tuxed.net/vpn-user-portal/_oauth/authorize",
                "authorization_endpoint_template": "https://vpn.tuxed.net/vpn-user-portal/_saml/login?ReturnTo=@AUTHORIZE_URI@&IdP=@ORG_ID@",
                "token_endpoint": "https://vpn.tuxed.net/vpn-user-portal/oauth.php/token"
            }
        }
    }

