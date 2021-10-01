# What to expect in eduVPN / Let's Connect! 3.x?

We expect to release eduVPN / Let's Connect! 3.x in **Q4 of 2021**. This will also
depend on the eduVPN / Let's Connect! client application that will need to 
implement the new [API](API_V3.md).

If you'd like to have something added, removed, changed: please contact us on 
[eduvpn-support@lists.geant.org](mailto:eduvpn-support@lists.geant.org) and 
make your case!

## High Level Changes

- [WireGuard](WIREGUARD.md) Support
- Removal of all internal 2FA, 2FA only supported when using external 
  authentication sources, e.g. in IdP
  
## Operator Changes

- Runs on Debian >= 11, Fedora >= 34

## Implementation Changes

- Require at least OpenVPN 2.5
- [OAuth 2.1](https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/) draft 
  implementation for API
- OpenVPN requires now TLS >= 1.3
- OpenVPN supports now both AES-256-GCM and CHACHA-POLY1305 data cipher. If the
  server supports hardware accelerated AES, AES is used, otherwise 
  CHACHA-POLY1305.
- EdDSA (Ed25519) X.509 certificates for OpenVPN
- New [API_V3](API_V3.md) for use by eduVPN / Let's Connect! Applications
- Merge of vpn-user-portal, vpn-server-api and vpn-lib-common in 1 component
- Switch 
  [VPN Daemon](https://git.sr.ht/~fkooman/vpn-daemon/tree/v2/item/README.md) to 
  use HTTP(S) instead of TCP socket, implement WireGuard management
- Support PostgreSQL, MySQL/MariaDB for portal data storage instead of only 
  SQLite
- New OAuth Token format (EdDSA JWT, perhaps switch to something else still?)

## Work in Progress

- Support for MySQL/MariaDB + memcached for [HA](PORTAL_HA.md), works fine for 
  portal, BUT we have to make it work with browser *sessions* as well
- VPN Usage stats need to be completely redone, currently only "VPN client use" 
  is available because that was easy
- Guest Usage has been completely removed for now, need to think how and 
  whether to get this back in a clean way *with* pseudonyms, don't leak local 
  user identity to guest servers! 
- Add public CA and public WireGuard key to the discovery files to have an 
  additional trust channel between app and server in addition to Web TLS, or 
  perhaps _sign_ the API responses with a public key mentioned in the discovery 
  files...
- Keep aggregate logs longer than 30 days, i.e. usage statistics
- Allow limiting number of VPN connections per user (and per client).
- Work on implementing 
  [hardware signing](https://argon.tuxed.net/fkooman/hardware_token_research_proposal.pdf) 
  of discovery files
  
## Under Consideration

- Reimplement 2FA, but only for local user accounts and _maybe_ LDAP
- Implement Admin API. e.g. for bulk-configuration downloads for managed 
  clients
- We removed "conditional 2FA" with the `PhpSamlSpAuthentication` module, it is 
  2FA for all, or for none
- IPv4 only, IPv6 only VPN? Probably not!
- "Expire at night" based on the server's timezone (this is currently 
  implemented, but could be removed if we move this to the client...)
