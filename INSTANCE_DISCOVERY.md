---
title: Instance Discovery
description: Obtain a list of VPN server Instances
category: dev
---

Applications can use "Instance Discovery" to obtain a list of known servers to
show in the application instead of asking the user to provide the FQDN of the
VPN server they want to connect to.

This document can be used by application developers implementing the 
[API](API.md).

# Discovery File

For eduVPN the discovery file is available 
[here](https://static.eduvpn.nl/disco/). Discovery files are JSON files 
describing the available VPN servers. The files are accompanied with a file 
containing a signature as well, to make sure they were not tampered with.

## Types

For eduVPN we define two "types" of discovery files. One for "Secure Internet" 
and one for "Institute Access".

The "Secure Internet" list contains VPN servers the user can connect to after 
"authorizing" at one of the listed servers. See [Guest Usage](GUEST_USAGE.md).

The "Institute Access" list contains VPN servers that typically only allow 
users from the organization itself to connect to it. These servers are 
used to protect "private" networks at an organization.

eduVPN applications MUST implement both discovery files and make a clear 
distinction in the UI of the application between them.

## Format

The JSON file looks like this:

    {
        "authorization_type": "...",
        "instances": [
            ...
        ]
    }

The `authorization_type` can be either `local` or `distributed` indicating 
whether or not the OAuth tokens obtained from those servers can be used at 
other VPN servers or not. See [Authorization](#authorization).

The `instances` key has an array with objects, in the most simple form:

    {
        "base_uri": "https://demo.eduvpn.nl/",
        "display_name": "Demo",
        "logo": "https://static.eduvpn.nl/disco/img/demo.png"
    }

The API's [Multi Language Support](API.md#multi-language-support) also applies 
here for both the `display_name` and `logo` fields!

The `base_uri` field can be used to perform the API Discovery of the instances 
themselves, see [API](API.md).

A `public_key` field MAY be specified, but it is NOT used by the application,
it is only used by other VPN servers.

## Validation

When downloading the instance discovery file, the signature MUST be verified as
well. The signature file is located in the same folder, but has the `.sig` 
extension, e.g. `https://static.eduvpn.nl/disco/secure_internet.json.sig`.

These signatures can be verified by e.g. using 
[libsodium](https://download.libsodium.org/doc/). The signature file contains a
Base64 encoded string string. See 
[this](https://download.libsodium.org/doc/bindings_for_other_languages/) 
document for various language bindings.

The flow:

1. Download e.g. `secure_internet.json`;
2. Download matching signature file, e.g. `secure_internet.json.sig`;
3. Verify the signature using libsodium and the public key stored in your 
   application
4. If you already downloaded the file before, verify the `seq` field of the new 
   file is higher than in the current file;
5. Overwrite the file you already have if `seq` was incremented.

The `signed_at` key is just informative and MUST NOT be relied on to be 
available.

The public key that is currently used is 
`E5On0JTtyUVZmcWd+I/FXRm32nSq8R2ioyW7dcu/U88=`. This is a Base64-encoded 
[Ed25519](https://en.wikipedia.org/wiki/Curve25519) public key.

# Authorization

Every VPN server runs their own OAuth server, so that would mean that for each 
instance a new token needs to be obtained. However, in order to support sharing 
access tokens between instances for [Guest Usage](GUEST_USAGE.md). We introduce 
two "types" of authorization:

1. `local`: every instance has their own OAuth server;
2. `distributed`: there is no central OAuth server, tokens from all instances 
   can be used at all (other) instances.

The `authorization_type` key indicates which type is used. The supported 
values are `local` and `distributed` mapping to the two modes described above.

The entries in the discovery file are bound to the `authorization_type` 
specified in the discovery file. So, may sure they are NOT mixed!

## Local

See API Discovery section above for determining the OAuth endpoints. The 
application MUST store the obtained access token and bind it to the instance
the token was obtained from. If a user wants to use multiple VPN instances, a 
token MUST be obtained from all of them individually.

## Distributed

Obtaining an access token from any of the instances listed in the discovery 
file is enough and can then be used at all the instances. Typically the user
has the ability to obtain only an access token at one of the listed instances, 
because only there they have an account, so the user MUST obtain an access 
token at that instance.

This is a bit messy from a UX perspective, as the user does not necessarily 
know for which instance they have an account. In case of eduVPN this will most
likely be the instance operated in their institute's home country. So students
of the University of Amsterdam will have to choose "The Netherlands" first.

When API discovery is performed, the keys for 
`authorization_endpoint` and `token_endpoint` for the specific instance MUST
be ignored. Refreshing access tokens MUST also be done at the original OAuth
server that was used to obtain the access token.

