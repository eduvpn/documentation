# Introduction

This document proposes a new way for eduVPN applications to discover VPN 
servers. This document will replace [INSTANCE_DISCOVERY](INSTANCE_DISCOVERY.md)
in the near future.

In the current server discovery we ask users first to choose their use-case, 
i.e. "Institute Access" or "Secure Internet". As that may be confusing to (new)
users, we decided to switch to the more common flow where the user is asked for 
their own institute first, e.g. the university they study at. This matches the 
behavior the user is already familiar with from other federated (web) 
services that offer "where are you from" (WAYF).

In this new proposal the users choose their organization, and then a list of 
VPN servers they have access to is shown to them.

# Advantages

1. The user no longer has to know which is their "Home" server, only the 
   organization they work/study at;
2. The user no longer has to browse a (long) list to find their organization
   server, which does not necessarily map 1-to-1 to their organization name;
3. There can be no confusion by getting stuck at a login screen where the 
   user can not go any further as they do not have an account at the server.

# User Flow

In the app's "first run" scenario:

1. The user opens the application;

2. The user chooses their organization;

3. The app shows the available VPN servers linked to that particular 
   organization, e.g. a VPN server for "Institute Access" and a list of VPN 
   servers around the world that can be used for "Secure Internet".

On subsequent runs, the list of servers is immediately available and 
potentially shows new servers that the user can now access based on their 
organization.

# App Flow

0. Application Starts;
1. Do we have a configured `server_info_url`? Yes: go to 5, No: go to 2;
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

**FIXME**: now there is no way to modify the `server_info_url` maybe we should
include the requirement for the app to delete the URL when it is unable to 
fetch the file and pretend it is a "first run"? Maybe a 410 response header 
is required for it to forget the `server_info_url`? Seems quite complicated,
what if the domain is no longer there?!

**FIXME**: how do we handle VPN server removals? Maybe we should really just 
delete them from the app as well? Of course NOT for manually added VPN 
servers...

## Notes

* The app MUST allow for forgetting the chosen organization (which deletes 
  the `server_info_url` from the app's internal storage);
* Allow the user to (un)hide VPN servers they never use;
* The individual VPN servers are ONLY contacted AFTER the user decides to 
  connect to them, never before. The only connection the app makes by itself 
  is fetching the mapping file and `secure_internet.json` on start, nothing 
  more.
* Do NOT cache any of the JSON files retrieved;
* The file `organization_list.json` is ONLY retrieved when the user needs to 
  choose their organization, so typically only once and then never again;

# Discovery Files

## Organization file

Proposed URL:

    https://discovery.eduvpn.org/v2/organization_list.json

Format:

    {
        "organization_list": [
            {
                "display_name": {
                    "nl-NL": "SURFnet bv",
                    "en-US": "SURFnet bv"
                },
                "organization_id": "https://idp.surfnet.nl",
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
                "server_info_url": "https://discovery.eduvpn.org/v2/mapping/https%3A%2F%2Fidp.surfnet.nl.json"
            },
            {
                 ...
            }
        ]
    }

The `server_info_url` can point to other domains than `discovery.eduvpn.org`, 
for example if an NREN wants to maintain their own mapping from organization 
to server list, see below.

**FIXME**: also have multi language keywords?!
**FIXME**: MUST always have `en-US` language? That seems not okay...
**FIXME**: language thing MUST always be object? simplifies app code somewhat

## Mapping file

Obtain the server information available servers for an `organization_id` by 
querying the server mentioned in `server_info_url`.

The result may look like this:

    {
        "server_list": [
            {
                "base_url": "https://surfnet.eduvpn.nl/",
                "display_name": {
                    "nl-NL": "SURFnet"
                },
                "logo_uri": {
                    "nl-NL": "https://surfnet.nl/logo.png"
                },
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
                "server_group_url": "https://discovery.eduvpn.org/v2/secure_internet.json"
            },
            {
                ...
            }
        ]
    }

The `server_group_url` points to a list of servers that can be used with an 
access token obtained from this server. This is the "Secure Internet" usage 
where users can use VPN servers hosted by other NRENs.

The field `display_name` is an object with translations in various languages. 
If the language of the user's device running the app is not available, the app
decides which language to choose. Typically `en-US` would be a good fallback, 
but it does not necessarily exist.

The field `logo_uri` contains the URL or URI (data URI) of the logo.

**FIXME**: we removed "auto connect" as we first have to think about *when* to 
actually auto connect, on initial launch? On every launch? And how to implement 
this (properly) in all apps... To me it would just seem very cumbersome and 
annoying, especially if the user cannot override this...

## Secure Internet File

Proposed URL:

    https://discovery.eduvpn.org/v2/secure_internet.json

Format:

    {
        "server_list": [
            {
                "base_url": "https://guest.eduvpn.no/",
                "display_name": {
                    "da-DK": "Norge",
                    "en-US": "Norway",
                    "nb-NO": "Norge",
                    "nl-NL": "Noorwegen"
                },
                "logo_uri": {
                    "en-US": "https://static.eduvpn.nl/disco/img/no.png"
                }
            },
            {
                "base_url": "https://nl.eduvpn.org/",
                "display_name": {
                    "da-DK": "Holland",
                    "en-US": "The Netherlands",
                    "nb-NO": "Nederland",
                    "nl-NL": "Nederland"
                },
                "logo_uri": {
                    "en-US": "https://static.eduvpn.nl/disco/img/nl.png"
                }
            },
            {
                ...
            }
        ]
    }


# Organization Hint

**FIXME**: text below is WAAAY too long

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

