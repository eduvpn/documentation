# Roadmap

This document describes the roadmap

## What to expect in eduVPN / Let's Connect!

If you'd like to have something added, removed, changed or change the priority: 
please contact us on 
[eduvpn-support@lists.geant.org](mailto:eduvpn-support@lists.geant.org) and 
make your case :-)

For our current progress see our 
[issue tracker](https://todo.sr.ht/~eduvpn/server).

## Big Things

Possibly only in 4.x as they are "breaking" changes, or complicated to add 
(reliably) to currently installed servers:

- Drop OpenVPN support
- Store all server/profile configuration in the database
- Allow “User Defined” VPNs
  – e.g. private networks for your own devices/servers (possibly P2P)

## Smaller Things

These may be implemented already in 3.x as they are not necessarily "breaking":

- Also provide client configuration file as JSON(?)
  - allows client to build their own config file locally with optional tweaks
    _without_ parsing WireGuard or OpenVPN configuration files
- Add WireGuard+TCP support
- "Real Time" Authorization with LDAP, OIDC backends 
  ([#131](https://todo.sr.ht/~eduvpn/server/131))
  - Removes the need to periodically authenticate to get the latest 
    "attributes/claims" from the IdM
  - Think about adding _hybrid_ authentication/authorization, e.g. have SAML 
    WebSSO for authentication, and LDAP for _authorization_
- Add more graphs on "Stats" page ([#11](https://todo.sr.ht/~eduvpn/server/11))
  - Currently only a graph for "client distribution" is available
- Reimplement 2FA, but only for *local* user accounts 
  ([#14](https://todo.sr.ht/~eduvpn/server/14))
- Allow profiles to be configured as "split tunnel" by default, e.g. 
  `defaultGateway` is set to `false` with `routeList` set, but allow the VPN 
  client to override this to send _all_ traffic over the VPN, currently some
  servers duplicate a VPN profile (one with split tunnel, one with default 
  gateway)
