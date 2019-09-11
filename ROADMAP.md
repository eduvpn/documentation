---
title: Roadmap
description: Development of Let's Connect! / eduVPN 3.0
---

We expect a release in Q4-2019.

## Server

### MUST 

- merge `vpn-server-api` and `vpn-lib-common` in `vpn-user-portal`;
  - remove internal API, only keep API needed for `vpn-server-node`.
- drop easy-rsa CA backend support, switch to vpn-ca written in Go;
- implement Go daemon for running on `vpn-server-node` dropping the 
  requirement of having a private network between Portal and Node, we aim for
  [Version 1](https://github.com/letsconnectvpn/lc-daemon/blob/master/ROADMAP.md#version-1);
- move bin scripts to libexec, if admin never has to run them, i.e. the scripts
  used by OpenVPN or cron
- never have any of the included (bin/libexec) scripts rewrite the
  configuration file(s)
- expose `info.json` instead as a `.well-known` URL so we can update it on 
  package updates
  - make `info.json` requests a 301 to the `.well-known` URL in the VirtualHost 
    config

### SHOULD

- look into using `tun0`, `tun1`, ... again for TUN devices (BSD compat)
- have a full php-saml-sp audit ([TODO](https://github.com/fkooman/php-saml-sp/blob/master/TODO.md))
- remove as many configuration options as possible, and have sane defaults
- Support AND/OR logic for permission attribute(s)
- Reduce the number of steps in the "deploy" scripts, make it easier to perform
  manual install without needing the deploy script
- Automatically (re)configure OpenVPN processes/restart them when needed with
  a cronjob?
- Create pseudonym for "Guest" usage, now the (local) identifier is directly 
  used in the "Guest" identifier. Do something like `hash(salt+user_id)` 
  instead and simply log it at 'generation time' so we can always find back the
  actual user
- Allow API clients to register themselves and use a secret in the future to
  avoid needing to ask for permission again when the refresh_token expires

### MAY

- use SVG instead of HTML table for stats (?)

## Deployment

I want:

1. install lc-vpn or whatever it is called package
2. restart Apache
3. run some kind of 'apply' script to configure / launch OpenVPN
4. basic VPN is up!

After that you have to tweak the firewall and enable IP forwarding, but that's
it. The rest should be working automatically... I guess one or two firewalld
commands should be enough to enable NAT and open udp/1194 and tcp/1194...
