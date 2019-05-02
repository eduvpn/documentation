# Let's Connect! & eduVPN 3.0

We expect a release in Q4-2019.

## Server

### Complete

- merge `vpn-server-api` and `vpn-lib-common` in `vpn-user-portal`
- merge parts of `vpn-lib-common` in `vpn-server-node`
- remove `MellonAuthentication` and `ShibAuthentication`, for 3.0 only 
  [php-saml-sp](https://git.tuxed.net/fkooman/php-saml-sp/) will be supported
- Remove internal API, only keep calls relevant for `vpn-server-node`
- Support multiple (SAML/LDAP) attributes for determining permissions / admin

### In Progress

- ...

### TODO

- Support AND/OR logic for permission attribute(s)
- Find better name for `vpn-user-portal` and `vpn-server-node`, maybe simply
  `portal` and `node`?
- Have a full php-saml-sp audit
- Think about making additional node(s) work independent (for a time) without
  the `portal`
- Never have the included deploy scripts modify and 'reformat' configuration 
  files, it makes it horrible for the admin to modify the file and loses 
  comments
- Drop support for CentOS 7, Debian 9, only support:
  - Debian >= 10 
  - RHEL / CentOS >= 8
- Simplify App API, reduce number of calls
  - 1 for profile/config discovery?
  - 1 to make sure the client is allowed to connect?
  - remove some calls no longer relevant
- Move API discovery to `.well-known` location instead of `info.json` in the 
  web root and ideally part of the software so it can get updates when updating
  the package(s)
- Move network (sysctl) configuration to the `node` package
- Reduce the number of steps in the "deploy" scripts, make it easier to perform
  manual install without needing the deploy script
- Automatically (re)configure OpenVPN processes/restart them when needed with
  a cronjob?
- Create pseudonym for "Guest" usage, now the (local) identifier is directly 
  used in the "Guest" identifier. Do something like `hash(salt+user_id)` 
  instead and simply log it at 'generation time' so we can always find back the
  actual user
- Allow API clients to register themselves and use a secret in the future to
  avoid needing to ask for permission again when the refresh_tokenex expires

### Maybe

- Support MySQL/MariaDB as database next to SQLite?
- Store the (profile) configuration in a database instead of configuration 
  file?

## Apps

- eduVPN app starts with IdP selector instead of "Secure Internet / 
  Institute Access" buttons, after which the user will see what is available
  for them
