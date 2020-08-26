---
title: Server Discovery
description: Server Discovery for VPN Applications
category: dev
---

# Server Discovery

**NOTE**: the format of `v2` is stable as of 2020-08-26. Format changes will
only occur in a different directory, e.g. `v3` if necessary in the future.

This document describes how eduVPN applications find out about eduVPN servers.

Two JSON documents are available to facilitate eduVPN server discovery:
 
- Server List: `https://disco.eduvpn.org/v2/server_list.json`
- Organization List: `https://disco.eduvpn.org/v2/organization_list.json`

## Server List

The "Server List" contains a list of _all_ eduVPN servers. In this list we 
distinguish between two _types_ of servers (`server_type`):

- Secure Internet: in case a user has access to _any_ one of the 
  "Secure Internet" servers, the user can use _all_ of them;
- Institute Access: for exclusive use by users belonging to the organization 
  running the service and that can log in to this service.

The "Secure Internet" servers are named after the country they are in, e.g. 
"The Netherlands". The "Institute Access" servers are named after the institute
they belong to, e.g. "Radboud University".

    {
      "server_list": [
        {
          "server_type": "institute_access",
          "base_url": "https://sunset.nuonet.fr/",
          "display_name": "CNOUS",
          "support_contact": [
            "mailto:support-technique-nuo@listes.nuonet.fr"
          ]
        },
        {
          "server_type": "secure_internet",
          "base_url": "https://eduvpn.rash.al/",
          "country_code": "AL",
          "support_contact": [
            "mailto:helpdesk@rash.al"
          ]
        },

        ...

        ...
            
      ]
    }

The application MUST always fetch the `server_list.json` at application start. 
The application MAY refresh the `server_list.json` periodically, e.g. once 
every hour. The reason for this is that the list of servers changes regularly.

The keys `server_type`, `base_url` are required for all server types. The 
`display_name` key is required for the `institute_access` server type. The 
`country_code` key is required for the `secure_internet` server type.

## Organization List

The "Organization List" contains a list of all known organizations and their
mapping to the "Secure Internet" servers. In order to be able to use all 
"Secure Internet" servers, the user needs to know _which_ of the 
"Secure Internet" servers they have access to based on their 
"Home Organization". The "Organization List" contains a mapping between 
organization and "Secure Internet" server through the `secure_internet_home` 
key that points to a `base_uri` of a server entry in the "Server List" of the
key `server_type` with value `secure_internet`:

    {
      "organization_list": [
        {
          "display_name": {
            "nl": "SURFnet bv",
            "en": "SURFnet bv"
          },
          "org_id": "https://idp.surfnet.nl",
          "secure_internet_home": "https://nl.eduvpn.org/",
          "keyword_list": {
            "en": "SURFnet bv SURF konijn surf surfnet powered by",
            "nl": "SURFnet bv SURF konijn powered by"
          }
        },

        ...

        ... 

      ]
    }

The application MUST only download the `organization_list.json` when it is 
needed. It is only needed:

- on "first launch" when offering the search for "Institute Access" and 
  "Organizations";
- when the user tries to add new server AND the user did NOT yet choose an 
  organization before.

The reason for this is that the list can get quit big. We expect it can be up
to 1MB in the future.

The keys `display_name`, `org_id`, `secure_internet_home` are required keys. 
The `keyword_list` is optional.

## Support Contact

The OPTIONAL key `support_contact` contains a list of possible contact options 
to be displayed in the application.

- `mailto:X`
- `https://X`
- `tel:X`

## Keywords

The OPTIONAL key `keyword_list` contains a string, or object containing 
keywords, example:

    "keyword_list": {
      "en": "SURFnet bv SURF konijn surf surfnet powered by",
      "nl": "SURFnet bv SURF konijn powered by"
    }

**NOTE**: the `keyword_list` MUST be supported in `server_list.json` for 
"Institute Access" servers! Currently it is not used, but will be used in the 
near future.

## Language Matching

We assume the OS the user is using has some kind of locale set up. For example
the OS is set to `en-US`, `nl-NL` or `de-DE`. 

The field `keyword_list` (and `display_name` for the organization list and 
server list for server type `institute_access`) are either of type `string` or 
of type `object`. If they are of type `string` the value is used/displayed 
as-is. If they are of type `object` a match is made to pick the "best" 
translation based on the OS language setting.

We use the 
[IETF BCP 47 language tag](https://en.wikipedia.org/wiki/IETF_language_tag). A 
comprehensive "mapping" rules are discussed in 
[section 4](https://tools.ietf.org/html/rfc5646#section-4) of RFC 5646. If your
OS or the standard library of the OS provides support for this use it. If not,
you can implement a subset of this matching yourself.

Start from the OS language setting, e.g. `de-DE`.

1. Try to find the exact match, so search for `de-DE` in this case;
2. Try to find a key that *starts* with the OS language setting, e.g. 
`de-DE-x-foo`;
3. Try to find a key that *starts* with the first part of the OS language, e.g. 
`de-`;
4. Pick one that is deemed best, e.g. `en-US` or `en`, but note that not all 
languages are always available!

### Search

When searching for organizations (and servers) the device locale should not be
used to restrict searches to that particular locale, but search in all locales.

## Country Code

The "Secure Internet" servers from `server_list.json` have a `country_code` 
field. This field MUST be used to find an appropriate translation of the 
country name and flag for display in the UI. If the OS you are writing an 
application for allows you to "internationalize" country codes (or country 
names) this SHOULD be used.

If such functionality is lacking you can use the file 
[here](https://github.com/eduvpn/artwork/blob/master/country_code_to_country_mapping.json).

You can find many country flags for use by your application 
[here](https://github.com/eduvpn/artwork/tree/master/App/Flags). Copy those in
your assets folder, do not fetch them dynamically!

**NOTE**: if you use these assets, they MUST be included in your application. 
It MUST NOT be fetched at application run time! There is no guarantee these
files will remain available at this exact location!

## Signatures

All JSON discovery files have a signature. The signatures are generated with 
[minisign](https://jedisct1.github.io/minisign/):

- Server List: `https://disco.eduvpn.org/v2/server_list.json.minisig`
- Organization List: `https://disco.eduvpn.org/v2/organization_list.json.minisig`

The minisign documentation shows the format of the signatures and public keys.

As of 2020-05-25 the public key used to verify the signatures is this one:

    untrusted comment: minisign public key 19725C6AF525056D
    RWRtBSX1alxyGX+Xn3LuZnWUT0w//B6EmTJvgaAxBMYzlQeI+jdrO6KF

**NOTE**: you MUST allow your application to contain _multiple_ public keys for 
verification. A signature is considered valid if it is correctly signed by one
of the public keys. So your verification algorithm MUST perform proper
signature's public key identification, matching against the list of trusted
public keys and finally validating content integrity. Any error in the process
MUST be shown to the user of the application.

### Rollback Prevention

The JSON files contain a `v` key to contains the 
[Unix time](https://en.wikipedia.org/wiki/Unix_time). The field MUST be used to
prevent "rollback" to older versions.

When downloading a new version, it MUST be ensured that the `v` field of the
new file is `>` the `v` field of the old version. As an example:

    {
      "v": 1594022992,
      "server_list": [
        {
            // ...
        }
      ]
    }

## Authorization

See [API](API.md) for the actual OAuth flow. For "Secure Internet" servers you
also MUST implement 
[SERVER_DISCOVERY_SKIP_WAYF](SERVER_DISCOVERY_SKIP_WAYF.md).
