# Signed API Responses

**NOTE**: this a a PROPOSAL. We'd like to hear feedback on it.

## Problem

Our VPN clients use an OAuth API to talk to the VPN server's web server over 
TLS to obtain VPN configurations.

If a VPN server compromise is detected and the TLS server certificate is 
revoked by the server operator, the VPN clients will never find out as none of 
our clients check whether the TLS certificate has been revoked. This is a 
generic problem for HTTP client libraries on all platforms. Support for 
revocation checking is either incomplete, or missing, or difficult to enable 
conditionally, i.e. not all servers support it, so we need a secure way to 
inform the client it MUST enforce it.

This means that a MITM attack can be performed without the client ever finding 
out that something is wrong, even after the TLS certificate has been revoked.

## Solutions

There are a number of possible solutions we'll discuss in this document:

1. Implement OCSP (Stapling) in the VPN client
2. Enforce DNSSEC in the client when resolving DNS names for connecting to
3. Sign the API responses

## OCSP Stapling

This would be the cleanest solution. On every TLS connection the client will be
sure the TLS certificate has not been revoked, give or take the allowed cache
duration of the OCSP Staple response.

The problem is that OCSP Stapling is very complex to get right, so if the TLS
library used by the application does not support it, it will be impossible, or
verify difficult to implement or get right.

* Android `[1]`
* macOS/iOS `[2]`
* Windows `[3]`
* Linux `[4]`

As we are working on a "common library" for the eduVPN apps, we also 
investigated support for OCSP (Stapling) in Golang. It is currently 
non-existent, so we can't currently rely on this. Perhaps in a few years 
`[5,6]`.

## DNSSEC

DNSSEC has its own problems, particularly that it is not deployed widely
(enough), and protecting against (local) attackers won't work unless the user's 
device also enforces DNSSEC verification on the device itself, or forces the 
use of a trusted DoH or DoT server. This _might_ work in some scenarios, but 
can't be really relied on.

What we _could_ do is implement DoH in the VPN client itself to bypass the 
local DNS resolver. This seems like a can of worms that should be left closed.

## Sign API Responses

For eduVPN specific we have an alternative trust path to learn about the VPN 
servers already `[7]`. We can leverage this channel to handle the 'revocation' 
scenario. The VPN server's OAuth implementation uses public key signatures to
sign OAuth tokens, it could also be used to sign OAuth responses that can then
be verified by the client before connecting to the VPN.

Servers would publish their OAuth public key in the server discovery file. In
case the server is compromised and restored, the new OAuth public key is 
registered in the discovery file and the VPN client would reject configuration
responses with the old public key.

This would make it possible to revoke servers and make sure the client finds 
finds out about it soon after the server compromise is detected and the 
server discovery file is updated to list the new key.

It also allows for an "opt-in" scenario where we deploy it over time after the
server operator wants to enable this.

We wrote a simple patch `[8]` implementing exactly this.

## References

1. https://github.com/eduvpn/android/issues/339
2. https://github.com/eduvpn/apple/issues/410
3. https://github.com/Amebis/eduVPN/issues/168
4. https://github.com/eduvpn/python-eduvpn-client/issues/389
5. https://github.com/golang/go/issues/40017
6. https://github.com/golang/go/issues/22274
7. https://github.com/eduvpn/documentation/blob/v3/SERVER_DISCOVERY.md
8. https://git.sr.ht/~fkooman/vpn-user-portal/commit/971d6e2f0c33c003902d25cfed29c4c567dd71f9
