# What to expect in eduVPN / Let's Connect! 3.x?

We expect to release eduVPN / Let's Connect! 3.x in **Q4 of 2021**. This will also
depend on the eduVPN / Let's Connect! client application that will need to 
implement the new [API](API_V3.md).

If you'd like to have something added, removed, changed: please contact us on 
[eduvpn-support@lists.geant.org](mailto:eduvpn-support@lists.geant.org) and 
make your case!

## High Level Changes

- [WireGuard](https://www.wireguard.com/) Support
- Removal of all internal 2FA, 2FA only supported when using external 
  authentication sources
  
## Operator Changes

- Runs on Debian >= 11, Fedora >= 34

## Implementation Changes

- Require at least OpenVPN 2.5
- [OAuth 2.1](https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/) draft 
  implementation for API
- OpenVPN requires now TLS >= 1.3
- EdDSA (Ed25519) X.509 certificates for OpenVPN
- New API (v3) for use by eduVPN / Let's Connect! Applications
- Merge of vpn-user-portal, vpn-server-api and vpn-lib-common in 1 component
- Switch VPN Daemon to use HTTP(S) instead of TCP socket
- Support MySQL/MariaDB for portal data storage instead of only 
  SQLite
- New OAuth Token format (EdDSA JWT, perhaps switch to something else still?)

## Work in Progress

- Support for MySQL/MariaDB + memcached for [HA]((PORTAL_HA.md), works fine for 
  portal, BUT we have to make it work with browser *sessions* as well
- VPN Usage stats need to be completely redone, currently only "VPN client use" 
  is available because that was easy
- Guest Usage has been completely removed, need to think how to get this back
  in a clean way *with* pseudonyms, don't leak local user identity to guest 
  servers! 
- Work on implementing 
  [hardware signing](https://argon.tuxed.net/fkooman/hardware_token_research_proposal.pdf) 
  of discovery files
- Add public CA and public WireGuard key to the discovery files to have an 
  additional trust channel between app and server in addition to Web TLS
- Keep aggregate logs longer than 30 days, i.e. usage statistics
  
## Under Consideration

- Redo internal 2FA, but only per server on/off switch and enrollment only from 
  admin account for LOCAL accounts
- Implement Admin API where certain aspects can be configured through API
- We removed "conditional 2FA" with the PhpSamlSpAuthentication module, it is 
  2FA for all, or for no-one
- IPv4 only, IPv6 only VPN? Probably not!
- "Expire at night" based on the server's timezone (this is currently 
  implemented, but could be removed if we move this to the client...)
