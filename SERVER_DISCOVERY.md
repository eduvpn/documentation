# Introduction

This document proposes a new way for eduVPN applications to discover VPN 
servers.

This document will replace "[Instance Discovery](INSTANCE_DISCOVERY.md)".

In the current server discovery we ask users first to choose their use-case, 
i.e. "Institute Access" or "Secure Internet". As that may be confusing to (new)
users, we decided to switch to the more common flow where the user is asked for 
their own institute first, e.g. the university they study at. This matches the 
behavior the user is already familiar with from other federated (web) services 
that offer "where are you from" (WAYF).

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
    country, but they only get access once they authorized to their "home" 
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
1. Do we have a configured server info URL in the app? Yes: go to 5, No: go 
   to 2;
2. Download `organization_list.json`;
3. Show a list of all organizations from the `organization_list.json` and 
   allow the user to browse and search based on `display_name` and 
   `keyword_list`;
4. Determine the server list URL from the `server_list` key associated with the 
   user's choice from `organization_list.json`. Store it in the app.
  * Add all (new) servers that are found in the server info URL document to 
    the list of (pre)configured VPN servers in the application, if they are not 
    yet there;
  * Visually mark servers previously configured using the server info URL
    which are no longer listed in the server info URL document, e.g. by 
    "graying" them out, but still allow the user to use them (and/or hide 
    them).

**NOTE**: the server info URL can be constructed as follows: take the discovery
base URL, e.g. `https://disco.eduvpn.org/` and append the `server_list` to it. 
For example, in case the `server_list` is `aHR0cHM6Ly9pZHAuc3VyZm5ldC5ubA.json` 
the server info URL becomes 
`https://disco.eduvpn.org/aHR0cHM6Ly9pZHAuc3VyZm5ldC5ubA.json`.

## Error Handling

* If any of the discovery files, i.e. `organization_list.json`, 
  or the server info URL can't be retrieved use their cached version (if 
  available, never for `organization_list.json`), but visually indicate this to 
  the user with the exact error message, e.g 404, 410, timeout, ...;
* If the signature(s) do not validate, keep using the cached version, but
  visually indicate this to the user;

# Discovery Files

## Organization file

Example URL:

    https://disco.eduvpn.org/organization_list.json

Example Content:
    
    {
      "organization_list": [
        {
          "display_name": {
            "nl": "SURFnet bv",
            "en": "SURFnet bv"
          },
          "org_id": "https://idp.surfnet.nl",
          "server_list": "aHR0cHM6Ly9pZHAuc3VyZm5ldC5ubA.json",
          "keyword_list": {
            "en": "SURFnet bv SURF konijn surf surfnet powered by",
            "nl": "SURFnet bv SURF konijn powered by"
          }
        },
      ]
    }

The `display_name` is shown to the user in the application in their preferred 
locale. The `display_name` (REQUIRED) and `keyword_list` (OPTIONAL) are used 
to allow the application to provide an interface where the user can search for 
an organization without needing to browse through the whole list. It is 
preferred that applications perform a sub-string match on the `display_name` 
and `keyword_list` keys.

The `server_list` field can be used to obtain VPN server list available to that 
organization. Using the example URL above, the server information can be 
obtained at `https://disco.eduvpn.org/aHR0cHM6Ly9pZHAuc3VyZm5ldC5ubA.json`.

## Server Info URL

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
          "peer_list": [
            {
              "base_url": "https://gdpt-eduvpndev1.tnd.aarnet.edu.au/",
              "display_name": {
                "da-DK": "Australien",
                "en-US": "Australia",
                "nb-NO": "Australia",
                "nl-NL": "Australië"
              }
            },
            {
              "base_url": "https://eduvpn.deic.dk/",
              "display_name": {
                "da-DK": "Danmark",
                "en-US": "Denmark",
                "nb-NO": "Danmark",
                "nl-NL": "Denemarken"
              }
            },
            {
                // ...
            }
          ]
        },
        {
          "display_name": {
            "en": "Demo"
          },
          "base_url": "https://demo.eduvpn.nl/"
        },
        {
          "display_name": {
            "en": "SURFnet"
          },
          "base_url": "https://surfnet.eduvpn.nl/"
        }
      ]
    }

Here `peer_list` contains the list of servers that can be used with the token
obtained of for its parent. So in the example above, the OAuth access token 
obtained for `https://nl.eduvpn.org/` can be used at ALL the `peer_list` 
entries. 

**NOTE**: only the access token can be used at servers in `peer_list`, the 
refresh token can only be used at `https://nl.eduvpn.org/`.

**NOTE**: the `peer_list` key ALSO contains the parent entry as well! So be 
careful when rendering the UI to not duplicate them. This may change in the 
future!

# Application Data Model

This section proposes an internal data model for the (eduVPN) application. The
focus is to make it as minimal as possible, while retaining full application 
functionality when the discovery files are (temporary) not available.

This data model supports multiple "home" organizations by having multiple 
objects in `app_data`.

This first thing to store is the server info URL. Linked to this are all 
servers (`server_list`) that were retrieved from server info URL.

    {
        "https://disco.eduvpn.org/aHR0cHM6Ly9pZHAuc3VyZm5ldC5ubA.json": {
            "https://nl.eduvpn.org/": {
                "access_token": "${ACCESS_TOKEN}",
                "access_token_expires_at": "2020-03-05T08:00:00+00:00:00",
                "refresh_token": "${REFRESH_TOKEN}",
                "peer_list": [
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
            "https://demo.eduvpn.nl/": {
                "access_token": "${ACCESS_TOKEN}",
                "access_token_expires_at": "2020-03-05T08:00:00+00:00:00",
                "refresh_token": "${REFRESH_TOKEN}",
                "still_in_discovery": true
            },
            "https://surfnet.eduvpn.nl/": {
                "access_token": "${ACCESS_TOKEN}",
                "access_token_expires_at": "2020-03-05T08:00:00+00:00:00",
                "refresh_token": "${REFRESH_TOKEN}",
                "still_in_discovery": true
            }
        }
    }

This is the minimal data model. Together with the downloaded JSON discovery
files one can fully populate the UI. In case the discovery files are 
(temporary) not available, the app will still be fully functional.

The `access_token`, `access_token_expires_at` and `refresh_token` will only 
be added after the user selected this particular server and successfully 
completed the authorization phase.

# Notes

* The app MUST allow for forgetting the chosen organization, which then deletes 
  the server info URL from the app's storage;
* The application sorts VPN servers in descending order of use. Servers never
  or infrequently used drop to the bottom of the list;
* The VPN servers themselves are ONLY contacted AFTER the user decides to 
  connect to them, never before. The only connection the app makes by itself 
  is fetching the server info URL file;
* The contents of server info URL (JSON) MUST be cached;
* The cached JSON documents SHOULD be refreshed periodically, e.g. once per 
  day if the application keeps running;
* The cached JSON documents MUST be refreshed at application start;
* If refreshing the cache fails, the cached version SHOULD be used;
* The file `organization_list.json` is ONLY retrieved when the user needs to 
  choose their organization, so typically only once and then never again, it
  is NOT cached;
* `display_name`, `keyword_list` ALWAYS contain a map with a 
  language code according to [BCP 47](https://tools.ietf.org/html/rfc5646) and
  their respective value. See the examples above. It is up to the application 
  to pick the best "translation" for the current application language settings. 
  There is no guarantee that any language (always) exists!
* When retrieving URLs, *always* follow HTTP redirects, maximum depth 5, if 
  this is configurable;
* When retrieving URLs, *always* make sure HTTPS is used, also in the redirect 
  path! You MUST reject any HTTP URL or redirects to a HTTP URL! The easiest is
  to white list only HTTPS protocol.
* If a VPN server that was previously configured *through* the 
  server info URL is no longer listed there, it MUST be marked as "no longer
  available". NOTE: they MAY come back at some point!

# Signatures

We need signatures over the JSON files. We use 
[minisign](https://jedisct1.github.io/minisign/) and 
[signify](https://man.openbsd.org/signify) compatible signatures. This way we 
can use standard tooling to generate the signatures. Note, only the first two
lines of the signature file are used, and is fully compatible with signify.

The signature of `organization_list.json` is hosted on 
`organization_list.json.sig`. This public key to verify this signature will 
be hard coded in the application doing the verification. This is similar for 
the server info URL. A signature file is also available.

The application MUST verify ALL signatures over ALL files when retrieving them
BEFORE using them.

All discovery files contain the `"v"` key in the root. It is in the format 
`YYYYMMDDXX` where `XX` indicates the version of the day. The first version
of the day is for example `2020041100`. The next version is `2020041101`. When 
downloading a JSON discovery file it MUST be made sure the `"v"` of the new 
file is >= `"v"` of the previous obtained file. The application MUST NOT parse
the `"v"` field, but simply perform a string compare.
