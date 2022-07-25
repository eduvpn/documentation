# What to expect in eduVPN / Let's Connect! >= 3.1?

If you'd like to have something added, removed, changed or change the priority: 
please contact us on 
[eduvpn-support@lists.geant.org](mailto:eduvpn-support@lists.geant.org) and 
make your case :-)

For our current progress see our 
[issue tracker](https://todo.sr.ht/~eduvpn/server).

# Features

## Must

- Implement Admin API. e.g. for bulk-configuration downloads for managed 
  clients
  - Or expose API endpoint with TLS client certificate support to avoid OAuth
- Restore Graphs for stats
- Guest Usage has been completely removed for now, need to think how and 
  whether to get this back in a clean way *with* pseudonyms, don't leak local 
  user identity to guest servers! We MAY keep it out of 3.x and require servers
  to keep running 2.x until we come up with a better approach...

## Nice to have

- More granular profiles, e.g. give a particular user always the same IP
- Reimplement 2FA, but only for local user accounts
- Add public CA and public WireGuard key(s) to the discovery files to have an 
  additional trust channel between app and server in addition to Web TLS, or 
  perhaps _sign_ the API responses with a public key mentioned in the discovery 
  files...
- Work on implementing 
  [hardware signing](https://argon.tuxed.net/fkooman/hardware_token_research_proposal.pdf) 
  of discovery files
- Browser generated WireGuard private key (in portal so server never knows it)
- Generate QR code in browser instead of on the server
