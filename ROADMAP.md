## eduVPN 2.0 (Q1-2019)

- **DONE** Merge vpn-user-portal and vpn-admin-portal -> vpn-portal
- Use JWT (EdDSA) OAuth tokens
- **DONE** Integrate php-saml-sp for SAML support
- **DONE** Remove "multi instance" support (we only want 1 instance per VM)

## eduVPN 3.0 (Q4-2019)

- Merge vpn-server-api in vpn-portal
- Remove "use case" buttons from the apps
  - Allow user to select their IdP in the app, after which only 'relevant' VPN 
    servers are shown
