# Introduction

The eduVPN (mobile) applications use a (central) discovery file that is 
partly described in [INSTANCE_DISCOVERY](../INSTANCE_DISCOVERY.md), but how it 
was signed was not described before.

These are the files located at 
[https://static.eduvpn.nl/disco](https://static.eduvpn.nl/disco).

# Signatures

We use [php-json-signer](https://git.tuxed.net/fkooman/php-json-signer) to sign
the JSON discovery file. This **SHOULD** be done **OFFLINE**! 

There is also an RPM package available from the eduVPN repository on 
[https://repo.letsconnect-vpn.org](https://repo.letsconnect-vpn.org) called 
`php-json-signer`.

# Usage

Sign a discovery file, this will create the file `secure_internet.json.sig` in
the same directory:

    $ php-json-signer --sign secure_internet.json

Verify the signature:

    $ php-json-signer --verify secure_internet.json

To show the public key:

    $ php-json-signer --show
