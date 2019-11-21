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
* The VPN servers themselves are ONLY contacted AFTER the user decides to 
  connect to them, never before. The only connection the app makes by itself 
  is fetching the `server_info_url` file and the `server_group_url` if 
  applicable.
* Do NOT cache any of the JSON files retrieved;
* The file `organization_list.json` is ONLY retrieved when the user needs to 
  choose their organization, so typically only once and then never again;
* `display_name`, `keyword_list` and `logo_uri` ALWAYS contain a map with a 
  language code according to [BCP 47](https://tools.ietf.org/html/rfc5646) and
  their respective value. See the examples below. Note that it is up to the 
  application to pick the best "translation" for the current application 
  language settings. There is no guarantee that any language (always) exists!

# Discovery Files

## Organization file

Proposed URL:

    https://argon.tuxed.net/fkooman/eduVPN/discovery/v2/organization_list.json

Format:

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
                 ...
            }
        ]
    }

The `display_name` is shown to the user in the preferred locale. The 
`display_name` and `keyword_list` can be used to allow the application to 
provide an interface where the user can search for an organization.

The `server_info_url` is the URL that needs to be stored in the application 
AFTER the user chooses an organization. The URL needs to be retrieved on 
every application start. Redirects MUST be followed.

## Server Info URL

Obtain the available servers for an organization by fetching the URL specified
in `server_info_url`, see the previous section.

Example format:

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
                    "en-US": "https://static.eduvpn.nl/disco/img/nl.png"
                },
                "server_group_url": "https://argon.tuxed.net/fkooman/eduVPN/discovery/v2/secure_internet.json"
            },
            {
                "display_name": {
                    "en-US": "Demo"
                },
                "base_url": "https://demo.eduvpn.nl/",
                "logo_uri": {
                    "en-US": "https://static.eduvpn.nl/disco/img/demo.png"
                }
            },
            {
                "display_name": {
                    "en-US": "SURFnet"
                },
                "base_url": "https://surfnet.eduvpn.nl/",
                "logo_uri": {
                    "en-US": "https://static.eduvpn.nl/disco/img/surfnet.png"
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

Format:

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
