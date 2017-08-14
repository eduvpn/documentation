# Introduction

The eduVPN (mobile) applications use a (central) discovery file that is 
partly described in [API.md](API.md), but how it was signed was not described
before.

# Application

We use [php-json-signer](https://github.com/fkooman/php-json-signer) to sign
the JSON discovery file. This **SHOULD** be done **OFFLINE**! 

There is also an RPM package available from the eduVPN repository on 
[https://repo.eduvpn.org](https://repo.eduvpn.org) called `php-json-signer`.

# Usage

Generate a new public/private key:

    $ php-json-signer-init

Sign a discovery file:

    $ php-json-signer-sign instances.json

Verify the signature:

    $ php-json-signer-verify instances.json

To show the public key:

    $ php-json-signer-show-public-key
