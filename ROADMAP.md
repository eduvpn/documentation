## eduVPN 2.0 (Q1-2019)

- Merge vpn-user-portal and vpn-admin-portal -> vpn-portal
- Use JWT (EdDSA) OAuth tokens
- Integrate php-saml-sp for SAML support

## eduVPN 3.0 (Q4-2019)

- Merge vpn-server-api in vpn-portal (eduVPN 3.0?)
- Remove "multi instance" support (we only want 1 instance per VM)
- Remove "use case" buttons from the apps
  - Allow user to select their IdP in the app, after which only 'relevant' VPN 
    servers are shown
