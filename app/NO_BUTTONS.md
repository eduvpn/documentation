# Getting rid of the buttons...

## TODO

* maybe we SHOULD have entries no longer found in the mapping file be deleted
  from the app? Only always keep manually added servers... Seems risky though!
* we consider using 3 files for discovery, also the "secure_internet.json" as
  currently provided... this would simplify the mapping files as they no longer
  need to include (all) secure internet servers...

**NOTE**: none of the file formats / JSON encodings are final!

## Introduction

Our current eduVPN applications suffer from a complication making it 
difficult for (new) users to get started. The initial screen asks them to 
choose whether they want to "safely use the Internet" (Secure Internet) or 
access their institute's network (Institute Access). Especially for 
"Secure Internet" this is a problem. The "Secure Internet" function allows 
users (after authentication and authorization) to choose servers in any other 
country that participates in eduVPN. The way the authorization is set up, the 
user *first* has to select their "home" country and login there before being 
able to choose other countries. This works by using the token obtained from
the "home" organization at the other VPN servers.

We try to solve this by allowing the user to choose their organization first, 
after which the application will determine which (if any) VPN servers are 
available for the user.

## Advantages

1. The user no longer has to know which is their "Home" server;
2. The user no longer has to browse a (long) list to find their organization
   server, which does not necessarily map 1-to-1 to their institute name;
3. There can be no confusion by getting stuck at a login screen where the 
   user can not go any further as they do not have an account at the server.

## User Flow

In the app's "first run" scenario:

1. The user opens the application;

2. The user chooses their organization;

3. The app shows the available VPN servers linked to that particular 
   organization, e.g. a VPN server for "Institute Access" and a list of VPN 
   servers around the world that can be used for "Secure Internet".
   
4. (Optionally) the app connects automatically to a / one of the VPN servers

The app stores the organization identifier (`org_id`) the user chooses so this 
selector step does not need to be repeated anymore. 

On subsequent runs the app immediately shows VPN servers as obtained/configured 
during the last run.

## App Flow

0. Application Starts;
1. Do we have a `server_info_url`? Yes: go to 5, No: go to 2;
2. Download `organization_list.json`;
3. Show a list of all organizations from the `organization_list.json` and 
   allow the user to browse and search based on name and keywords;
4. Store the `server_info_url` associated with the user's choice from 
   `organization_list.json` in the app's internal storage;
5. Download the mapping file linked to in `server_info_url`;
6. Add all servers that are found in the `server_info_url` document to the list 
   of (pre)configured VPN servers in the application if they are not yet there;
7. Visually mark servers previously configured using the `server_info_url` 
   which are no longer listed in the `server_info_url` document, i.e. by 
   "graying" them out, but still allow the user to use them (and/or hide them);

## Notes

* The app MUST allow for forgetting the chosen organization (which deletes 
  the `server_info_url` from the app's internal storage);
* Allow the user to (un)hide VPN servers they never use;
* If the mapping file is no longer available allow the user to select an 
  organization (again), but nothing is ever (automatically) removed from the 
  application;
* The individual VPN servers are ONLY contacted AFTER the user decides to 
  connect to them, never before. The only connection the app makes by itself 
  is fetching the mapping file on start, nothing more.
* Do not cache any of the JSON files retrieved;
* The `organization_list` is ONLY retrieved when the user needs to choose 
  their organization, so typically only once and then never again;
* The rules above do not hold for manually added servers by the user.

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

