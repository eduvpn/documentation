# Introduction

This document proposes a new way for eduVPN applications to discover VPN 
servers. 

This document will replace "[Instance Discovery](INSTANCE_DISCOVERY.md)".

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
   server, which does not necessarily map one-to-one to their organization 
   name;
3. There can be no confusion by getting stuck at a login screen where the 
   user can not go any further as they do not have an account at the server;
  * For example, when starting the VPN client first, users could choose any 
    country, but they did only get access once they authorized to their "home" 
    server...

# User Flow

In the app's "first run" scenario:

1. The user opens the application;

2. The user chooses their organization;

3. The app shows the available VPN servers linked to that particular 
   organization, e.g. a VPN server for "Institute Access" and a list of VPN 
   servers around the world that can be used for "Secure Internet".

On subsequent runs, the list of servers is immediately available and 
shows new servers that the user can now access based on their organization that
were added in the meantime. For example, a new country joined the eduVPN 
project and can now be used.

# App Flow

0. Application Starts;
1. Do we have a configured `server_info_url` in the app? Yes: go to 5, No: go 
   to 2;
2. Download `organization_list.json`;
3. Show a list of all organizations from the `organization_list.json` and 
   allow the user to browse and search based on `display_name` and 
   `keyword_list`;
4. Store the `server_info_url` associated with the user's choice from 
   `organization_list.json` in the app's internal storage;
5. Download the URL mentioned in `server_info_url`;
   * If the HTTP response is HTTP 410 (Gone) delete the `server_info_url` and 
     go to step 2;
6. Add all servers that are found in the `server_info_url` document to the list 
   of (pre)configured VPN servers in the application if they are not yet there;
  * Also download the `server_group_url` if any of the listed servers has this 
    key. Those servers will become available once the user authorized at the 
    server that has this key set.
7. Visually mark servers previously configured using the `server_info_url` 
   which are no longer listed in the `server_info_url` document, i.e. by 
   "graying" them out, but still allow the user to use them (and/or hide them);

**FIXME**: the sub item under 5 shows a way how the user's selection can be 
cancelled by the server... Seems quite complicated though, what if the domain 
is no longer there?! Maybe we should just inform the user the file could not be
downloaded, and allow them to choose to select an new organization again? But 
NOT if the network is down? Maybe the 410 (or maybe also 404?) thing is really 
the best? 

# Discovery Files

## Organization file

Example URL:

    https://argon.tuxed.net/fkooman/eduVPN/discovery/v2/organization_list.json

Example Content:

    {
        "organization_list": [
            {
                "display_name": {
                    "nl": "SURFnet bv",
                    "en": "SURFnet bv"
                },
                "keyword_list": {
                    "en": "SURFnet bv SURF konijn surf surfnet powered by",
                    "nl": "SURFnet bv SURF konijn powered by"
                },
                "server_info_url": "https://argon.tuxed.net/fkooman/eduVPN/discovery/v2/aHR0cHM6Ly9pZHAuc3VyZm5ldC5ubA.json"
            },
            {
                "display_name": {
                    "da": "Danmarks Tekniske Universitet",
                    "en": "Technical University of Denmark (DTU)"
                },
                "keyword_list": [],
                "server_info_url": "https://argon.tuxed.net/fkooman/eduVPN/discovery/v2/aHR0cDovL2Jpcmsud2F5Zi5kay9iaXJrLnBocC9zdHMuYWl0LmR0dS5kay9hZGZzL3NlcnZpY2VzL3RydXN0.json"
            }
        ]
    }

The `display_name` is shown to the user in the preferred locale. The 
`display_name` and `keyword_list` are used to allow the application to 
provide an interface where the user can search for an organization without 
needing to browse through the whole list.

The `server_info_url` is the URL that needs to be stored in the application 
AFTER the user chooses an organization.

## Server Info URL

Obtain the available servers for an organization by fetching the URL specified
in `server_info_url`, see the previous section.

Example Content:

    {
        "server_list": [
            {
                "display_name": {
                    "da-DK": "Holland",
                    "en-US": "The Netherlands",
                    "nb-NO": "Nederland",
                    "nl-NL": "Nederland"
                },
                "base_url": "https://nl.eduvpn.org/",
                "logo_uri": {
                    "en": "https://static.eduvpn.nl/disco/img/nl.png"
                },
                "server_group_url": "https://argon.tuxed.net/fkooman/eduVPN/discovery/v2/secure_internet.json"
            },
            {
                "display_name": {
                    "en-US": "Demo"
                },
                "base_url": "https://demo.eduvpn.nl/",
                "logo_uri": {
                    "en": "https://static.eduvpn.nl/disco/img/demo.png"
                }
            },
            {
                "display_name": {
                    "en": "SURFnet"
                },
                "base_url": "https://surfnet.eduvpn.nl/",
                "logo_uri": {
                    "en": "https://static.eduvpn.nl/disco/img/surfnet.png"
                }
            }
        ]
    }

The `server_group_url` points to a list of servers that can be used with an 
access token obtained from this server. This is the "Secure Internet" use case 
where users can use VPN servers hosted by other NRENs. For "Institute Access"
servers this key does NOT exist.

## Server Group URL

This URL is obtained from the `server_group_url` key, see previous section.

Example Content:

    {
        "server_list": [
            {
                "display_name": {
                    "da-DK": "Norge",
                    "en-US": "Norway",
                    "nb-NO": "Norge",
                    "nl-NL": "Noorwegen"
                },
                "public_key_list": [
                    "qOLCcqXWZm9nmjsrwiJQxxWD606vDEJ2MIcc85oJmnE"
                ],
                "base_url": "https://guest.eduvpn.no/",
                "logo_uri": {
                    "en-US": "https://static.eduvpn.nl/disco/img/no.png"
                }
            },
            {
                "display_name": {
                    "da-DK": "Holland",
                    "en-US": "The Netherlands",
                    "nb-NO": "Nederland",
                    "nl-NL": "Nederland"
                },
                "public_key_list": [
                    "O53DTgB956magGaWpVCKtdKIMYqywS3FMAC5fHXdFNg"
                ],
                "base_url": "https://nl.eduvpn.org/",
                "logo_uri": {
                    "en-US": "https://static.eduvpn.nl/disco/img/nl.png"
                }
            }
        ]
    }

The `public_key_list` is NOT used by the applications, but only by other 
VPN servers belonging to the same server group.

**FIXME**: maybe we should have a different file for servers... and not mix 
this with client discovery info. There is not really a need to expose all this
info to all servers...

**FIXME**: the key should probably by `server_group_list`, and not 
`server_list`.

# Application Data Model

This section proposes an internal data model for the (eduVPN) application. The
focus is to make it as minimal as possible, while retaining full application 
functionality when the discovery files are (temporary) not available.

This data model supports multiple "home" organizations by having multiple 
objects in `app_data`.

This first thing to store is the `server_info_url`. Linked to this are all 
servers (`server_list`) that were retrieved from `server_info_url` and possibly 
from one or more `server_group_url` entries.

    {
        "app_data": [
            {
                "server_info_url": "https://argon.tuxed.net/fkooman/eduVPN/discovery/v2/aHR0cHM6Ly9pZHAuc3VyZm5ldC5ubA.json",
                "server_list": [
                    {
                        "access_token": "${ACCESS_TOKEN}",
                        "access_token_expires_at": "2020-03-05T08:00:00+00:00:00",
                        "refresh_token": "${REFRESH_TOKEN}",
                        "base_url": "https://nl.eduvpn.org/",
                        "server_group_list": [
                            "https://gdpt-eduvpndev1.tnd.aarnet.edu.au/",
                            "https://eduvpn.deic.dk/",
                            "https://eduvpn1.funet.fi/",
                            "https://eduvpn-poc.renater.fr/",
                            "https://eduvpn1.eduvpn.de/",
                            "https://eduvpn.marwan.ma/",
                            "https://guest.eduvpn.no/",
                            "https://vpn.pern.edu.pk/",
                            "https://eduvpn.ac.lk/",
                            "https://nl.eduvpn.org/",
                            "https://eduvpn.renu.ac.ug/",
                            "https://eduvpn.uran.ua/"
                        ],
                        "still_in_discovery": true
                    },
                    {
                        "access_token": "${ACCESS_TOKEN}",
                        "access_token_expires_at": "2020-03-05T08:00:00+00:00:00",
                        "refresh_token": "${REFRESH_TOKEN}",
                        "base_url": "https://demo.eduvpn.nl/",
                        "still_in_discovery": true
                    },
                    {
                        "access_token": "${ACCESS_TOKEN}",
                        "access_token_expires_at": "2020-03-05T08:00:00+00:00:00",
                        "refresh_token": "${REFRESH_TOKEN}",
                        "base_url": "https://surfnet.eduvpn.nl/",
                        "still_in_discovery": true
                    }
                ]
            }
        ]
    }

This is the minimal data model. Together with the downloaded JSON discovery
files one can fully populate the UI. In case the discovery files are 
(temporary) not available, the app will still be fully functional.

The `access_token`, `access_token_expires_at` and `refresh_token` will only 
be added after the user selected this particular server and successfully 
completed the authorization phase.

**FIXME**: should we instead actually "merge" the retrieved JSON documents in 
the app data model?

# Notes

* The app MUST allow for forgetting the chosen organization, which then deletes 
  the `server_info_url` from the app's internal storage;
* The application sorts VPN servers in descending order of use. Servers never
  or infrequently used drop to the bottom of the list;
* The VPN servers themselves are ONLY contacted AFTER the user decides to 
  connect to them, never before. The only connection the app makes by itself 
  is fetching the `server_info_url` file and the `server_group_url` if 
  applicable;
* Retrieved JSON files SHOULD be cached, EXCEPT `organization_list.json`, but 
  MUST be retrieved again at every application (re)start;
* The `logo_uri` contents SHOULD be cached and MAY periodically be checked 
  for changes;
* The file `organization_list.json` is ONLY retrieved when the user needs to 
  choose their organization, so typically only once and then never again;
* `display_name`, `keyword_list` and `logo_uri` ALWAYS contain a map with a 
  language code according to [BCP 47](https://tools.ietf.org/html/rfc5646) and
  their respective value. See the examples below. It is up to the application 
  to pick the best "translation" for the current application language settings. 
  There is no guarantee that any language (always) exists!
* When retrieving URLs, *always* follow HTTP redirects, maximum depth 5, if 
  this is configurable;
* When retrieving URLs, *always* make sure HTTPS is used, also in the redirect 
  path! You MUST reject any HTTP URL or redirects to a HTTP URL! The easiest is
  to white list only HTTPS protocol.
* If a VPN server that was previously configured *through* the 
  `server_info_url` is no longer listed there, it MUST be marked as "no longer
  available". Manually added servers are NEVER deleted.
  
**FIXME**: how to do cache busting for `logo_uri` URLs? Just use a different 
name when the logo changes?

# Signatures

We need signatures over the JSON files. We use 
[minisign](https://jedisct1.github.io/minisign/) and 
[signify](https://man.openbsd.org/signify) compatible signatures. This way we 
can use standard tooling to generate the signatures.

The signature of `organization_list.json` is hosted on 
`organization_list.json.sig`. This public key to verify this signature will be 
hard coded in the application doing the verification.

The individual `server_info_url` URLs, as pointed to from 
`organization_list.json`, also host an `${server_info_url}.sig` file that is 
used to verify the signatures. The public key for this signature is available
in the `server_info_url_public_key` field.

The same holds for the `server_group_url`. It also has a 
`server_group_url_public_key` field containing the public key to verify 
`${server_group_url}.sig`.

The application MUST verify ALL signatures over ALL files when retrieving them
BEFORE using them.

**FIXME**: apps MUST also store the public key for the `server_info_url` 
entries, maybe "encode" it as part of the fragment?

**FIXME** we need to record the time stamp (or sequence) to make sure it is not 
possible to do rollback.
