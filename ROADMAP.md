# Let's Connect! & eduVPN 3.0

We expect a release in Q4-2019.

## Server

- Merge vpn-server-api and vpn-user-portal and call them "controller"
- Remove all SAML authentication backends except 
  [php-saml-sp](https://software.tuxed.net/php-saml-sp/)
  - Have a proper full security audit
- Think about making additional nodes work independent (for a time) without
  the "controller"
- Never have the included scripts modify and 'reformat' configuration files,
  it makes it horrible for the admin to modify the file and loses comments
- Drop support for CentOS 7, Debian 9, only support:
  - Debian >= 10 
  - RHEL / CentOS >= 8

## Apps

- eduVPN app starts with IdP selector instead of "Secure Internet / 
  Institute Access" buttons, after which the user will see what is available
  for them
