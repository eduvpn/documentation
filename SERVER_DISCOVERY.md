# Introduction

This document describes the discovery of VPN servers.

**WORK IN PROGRESS**

Two files are relevant:

- Server List: `https://disco.eduvpn.org/server_list.json`
- Organization List: `https://disco.eduvpn.org/organization_list.json`

The "Server List" file contains a list of _all_ known VPN servers, both 
"Secure Internet" and "Institute Access".

    {
      "v": "2020-05-04T12:04:29+00:00",
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
          "display_name": {
            "en-US": "Albania",
            "sq-AL": "Shqiperi"
          },
          "public_key_list": [
            "Xv3l24gbMX8NtTnFQbWO2fGKPwKuc6EbjQDv8qw2GVk"
          ],
          "support_contact": [
            "mailto:helpdesk@rash.al"
          ]
        },

        ...

        ...
            
      ]
    }

**NOTE**: `public_key_list` is NOT used by applications.

The "Organization List" file contains a mapping between "Organization" and
"Secure Internet" servers, e.g.:

    {
      "v": "2020-04-30T07:25:42+00:00",
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

The key `secure_internet_home` is important for the mapping to a 
"Secure Internet" server. When the user chooses an organization it indicates
which "Secure Internet" server to authorize at. The value of 
`secure_internet_home` matches with a `base_url` in "Server List". The 
`base_url` can only point to servers with `server_type` value equal to 
`secure_internet`.

The app shows:

1. a list of "Institute Access" servers the user can choose directly
2. a list of "Organizations" that will *link* to a server using the 
   `secure_internet_home` key.

In the UI the user can choose a *server* (Institute Access) and and 
*organization* (Secure Internet). The reason for doing this is that we don't
want to user to choose a VPN country server first where as they can get stuck 
if their organization can't be used to login there. 

### Support Contact

The key `support_contact` contains a list of possible contact options to be 
displayed in the application.

- `mailto:X`
- `https://X`
- `tel:X`

### Keywords

The key `keyword_list` contains a string, or object containing keywords, 
example:

    "keyword_list": {
      "en": "SURFnet bv SURF konijn surf surfnet powered by",
      "nl": "SURFnet bv SURF konijn powered by"
    }
They can also be used in "Institute Access" and "Secure Internet" discovery 
files!

### Language Matching

We assume the OS the user is using has some kind of locale set up. For example
the OS is set to `en-US`, `nl-NL` or `de-DE`. 

The fields `display_name` and `keyword_list` are either of type `string` or of
type `object`. If they are of type `string` the value is used/displayed as-is. 
If they are of type `object` a match is made to pick the "best" translation 
based on the OS language setting.

We use the 
[IETF BCP 47 language tag](https://en.wikipedia.org/wiki/IETF_language_tag). A 
comprehensive "mapping" rules are discussed in 
[section 4](https://tools.ietf.org/html/rfc5646#section-4) of RFC 5646. If your
OS or the standard library of the OS provides support for this use it. If not,
you can implement a subset of this matching yourself.

Start from the OS language setting, i.e. `de-DE`.

1. Try to find the exact match, so search for `de-DE` in this case;
2. Try to find a key that *starts* with the OS language setting, e.g. 
`de-DE-x-foo`;
3. Try to find a key that *starts* with the first part of the OS language, e.g. 
`de-`;
4. Pick one that is deemed best, e.g. `en-US` or `en`, but note that not all 
languages are always available!

### Storage Data Model

It is recommended to store all OAuth information, among others, access token 
and refresh     token _per server_ in your data model, no matter whether it is a 
"Secure Internet" or "Institute Access". This 
makes it easy for "Institute Access" and "Alien" servers as each server has 
their own OAuth information. For "Secure Internet" it is a bit more 
complicated.

Based on the discovery using `organization_list.json` you can find out what 
the `secure_internet_home` is for a particular organization. This field 
contains the `base_url` of the "Home" server that will be used for obtaining 
OAuth information.

When the user chooses their organization, the OAuth flow is started with the 
`secure_internet_home` server and stored in the data model. When the 
user wants to use _another_ "Secure Internet" server, the OAuth access token 
already obtained is used at this _other_ "Secure Internet" server. Note that
the refresh token is _always_ used at the `secure_internet_home` server only! 
So whenever a refresh is needed, the home server is used to accomplish this.

### Signatures

The signatures are generated with 
[minisign](https://jedisct1.github.io/minisign/). All JSON discovery files have
a signature file as well:

- Server List: `https://disco.eduvpn.org/server_list.json.minisig`
- Organization List: `https://disco.eduvpn.org/organization_list.json.minisig`

The minisign documentation shows the format of the signatures and public keys.

As of 2020-05-19 the public key used to verify the signatures is this one:

    untrusted comment: minisign public key 8466FFE127BCDC82
    RWSC3Lwn4f9mhG3XIwRUTEIqf7Ucu9+7/Rq+scUMxrjg5/kjskXKOJY/

**NOTE**: this key will change before we go to "production"!

**NOTE**: we only use the minisign signatures in 
[signify](https://man.openbsd.org/signify) compatible mode, so only the second 
line of the signature file is used for the verification.
