# Instance Discovery

For an application to discover which instances are available to show to the 
user, a JSON document can be retrieved. For example eduVPN has those JSON 
documents available at 
[https://static.eduvpn.nl/disco/](https://static.eduvpn.nl/disco/).

Typically an application will use one or two discovery files for retrieving the
list of instances. It SHOULD be possible to configure additional sources. The 
URL of the discovery file could be used to map it to certain branding and
UI texts in the application.

## Format

The base JSON document looks like this:

    {
        "authorization_type": "distributed",
        "instances": [
            ...
        ]
    }

The `authorization_type` is described in the [Authorization](#authorization) 
section. 

The `instances` key has an array with objects, in the most simple form:

    {
        "base_uri": "https://demo.eduvpn.nl/",
        "display_name": "Demo",
        "logo": "https://static.eduvpn.nl/disco/img/demo.png"
    }

For multi language support, the values of the keys `display_name` and `logo` 
can contain multiple texts and logos depending on the language:

    {
        "base_uri": "https://demo.eduvpn.nl/",
        "display_name": {
            "en-US": "Demo VPN Provider",
            "nl-NL": "Demo VPN-aanbieder"
        },
        "logo": {
            "en-US": "https://static.eduvpn.nl/disco/img/demo.en.png",
            "nl-NL": "https://static.eduvpn.nl/disco/img/demo.nl.png"
        },
        "public_key": "Ch84TZEk4k4bvPexrasAvbXjI5YRPmBcK3sZGar71pg="
    }

Applications MUST check if the value of `display_name` and `logo` is a 
simple string, or an object. In case of an object, the language best matching
the application language SHOULD be chosen. If that language is not available, 
the application SHOULD fallback to `en-US`. If `en-US` is not available, it is
up to the application to pick one it deems best.

The `base_uri` field can be used to perform the API Discovery of the instances 
themselves, see below.

The `public_key` field is used by the VPN instances themselves for 
`distributed` Authorization, this can be ignored by API clients.

## Validation

When downloading the instance discovery file, you also MUST fetch the signature 
file, which is located in the same folder, but has the `.sig` extension, e.g. 
`https://static.eduvpn.nl/disco/secure_internet.json.sig`.

Using [libsodium](https://download.libsodium.org/doc/) you can verify the 
signature using the public key(s) that you hard code in your application. The 
signature file contains the Base64-encoded signature. See 
[this](https://download.libsodium.org/doc/bindings_for_other_languages/) 
document for various language bindings.

The flow:

1. Download `secure_internet.json`;
2. Download `secure_internet.json.sig`;
3. Verify the signature using libsodium and the public key stored in your 
   application
4. If you already have a cached version, verify the `seq` field of the new file
   is higher than the `seq` in the cached copy (see Caching section);
5. Overwrite the cached version if appropriate.

The `signed_at` key is just informative and MUST NOT be relied on to be 
available.

The public key that is currently used is 
`E5On0JTtyUVZmcWd+I/FXRm32nSq8R2ioyW7dcu/U88=`. This is a Base64-encoded 
[Ed25519](https://en.wikipedia.org/wiki/Curve25519) public key.

# Authorization

Every instance in the discovery file runs their own OAuth server, so that would
mean that for each instance a new token needs to be obtained.

However, in order to support sharing access tokens between instances for 
[Guest Usage](GUEST_USAGE.md). We introduce three "types" of authorization:

1. `local`: every instance has their own OAuth server;
2. `distributed`: there is no central OAuth server, tokens from all instances 
   can be used at all (other) instances.
3. `federated`: there is one central OAuth server, all instances accept 
   tokens from this OAuth server **NOT YET USED**;

The `authorization_type` key indicates which type is used. The supported 
values are `local`, `federated` or `distributed` mapping to the three modes
described above.

The entries in the discovery file are bound to the `authorization_type` 
specified in the discovery file.

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

## Federated

**NOT YET USED**

Here there is one central OAuth server that MUST be used. The OAuth server is 
specified in the discovery file in the `authorization_endpoint` and 
`token_endpoint` keys. When API discovery is performed, the keys for 
`authorization_endpoint` and `token_endpoint` for the specific instance from
`info.json` MUST be ignored. Refreshing access tokens MUST also be done at the
central server.

# Caching

There are two types of discovery:

1. Instance Discovery
2. API Discovery

Both are JSON files that can be cached. In addition to this, also the instance 
logos can be cached in the application to speed up displaying the UI. The 
`If-None-Match` or `If-Modified-Since` HTTP header can be used to retrieve 
updates.

The user SHOULD be able to clear all cache in the application to force 
reloading everything, e.g. by restarting the application.

The Instance Discovery files are also signed using public key cryptography, the
signature MUST be verified and the value of the `seq` key of the verified file 
MUST be `>=` the cached copy. It MUST NOT be possible to "rollback", so for the
instances discovery the cached copy MUST be retained.

The API discovery files, i.e. `info.json` does not currently have a signature 
and `seq` key, but MAY in the future.

The VPN configuration MUST NOT be cached and MUST be retrieved every time 
before a new connection is set up with the client.


The same rules for detecting multi language (for `message`) apply as in 
[Instance Discovery](#instance-discovery) apply here.

