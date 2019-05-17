---
title: Roadmap
description: Development of Let's Connect! / eduVPN 3.0
---

We expect a release in Q4-2019.

## Server

### Complete

- merge `vpn-server-api` and `vpn-lib-common` in `vpn-user-portal`
- merge parts of `vpn-lib-common` in `vpn-server-node`
- remove `MellonAuthentication` and `ShibAuthentication`, for 3.0 only 
  [php-saml-sp](https://git.tuxed.net/fkooman/php-saml-sp/) will be supported
- Remove internal API, only keep calls relevant for `vpn-server-node`
- Support multiple (SAML/LDAP) attributes for determining permissions / admin
- Never have the included deploy scripts modify and 'reformat' configuration 
  files, it makes it horrible for the admin to modify the file and loses 
  comments
- "Autoconfig" as much as possible, i.e. do not require (optional) 
  configuration parameters to be set, e.g. `Api` section, etc. Have good 
  defaults when config is missing
- Fully remove firewall from VPN, should be done in deploy script, or not at 
  all... as the firewall is 'static' anyway now, i.e. the same for all deploys
  that is totally fine

### In Progress

- Move API discovery to `.well-known` location instead of `info.json` in the 
  web root and ideally part of the software so it can get updates when updating
  the package(s). 
  [Idea](https://gist.github.com/fkooman/b41271a791be83cb4e9f56b82b4bfb42).

### TODO

- Support AND/OR logic for permission attribute(s)
- Find better name for `vpn-user-portal` and `vpn-server-node`, maybe simply
  `portal` and `node`? LC-vpn? lc-vpn? 
- Have a full php-saml-sp audit
- Think about making additional node(s) work independent (for a time) without
  the `portal`
- Drop support for CentOS 7, Debian 9, only support:
  - Debian >= 10 
  - RHEL / CentOS >= 8
- Simplify App API, reduce number of calls
  - 1 for profile/config discovery?
  - 1 to make sure the client is allowed to connect?
  - remove some calls no longer relevant
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
- Move `node` functionality also in portal to have only 1 package
  - optional `node` package when you deploy on multiple machines
- Rework `node` API to make it a lot simpler, i.e. generate server configs
  already in the `portal`, just put it in the right place
- Write a `node` daemon that uses TLS

#### Deployment

I want:

1. install lc-vpn or whatever it is called package
2. restart Apache
3. run some kind of 'apply' script to configure / launch OpenVPN
4. basic VPN is up!

After that you have to tweak the firewall and enable IP forwarding, but that's
it. The rest should be working automatically... I guess one or two firewalld
commands should be enough to enable NAT and open udp/1194 and tcp/1194...

### Maybe

- Support MySQL/MariaDB as database next to SQLite?
- Store the (profile) configuration in a database instead of configuration 
  file?

## Apps

- eduVPN app starts with IdP selector instead of "Secure Internet / 
  Institute Access" buttons, after which the user will see what is available
  for them
