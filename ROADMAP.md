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
  - Removes the need to periodically authenticate to get the latest 
    "attributes/claims" from the IdM
- Add more graphs on "Stats" page
  - Currently only a graph for "client distribution" is available
- Reimplement 2FA, but only for *local* user accounts
