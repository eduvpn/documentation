# Release Notes

These are the releases notes of eduVPN / Let's Connect! 3.x. They will be 
updated as needed. It is a big release consisting of many changes.

As this is a new major release, we expect some (minor) issues to still exist 
that we'll run into in the next weeks/months, so it is important to regularly 
update your system using the `vpn-maint-update-system` command. If you are 
currently deploying eduVPN / Let's Connect! in production, we highly recommend 
that you first install 3.x on a test system before planning an upgrade or new 
installation.

## New Features

- Use [WireGuard](https://www.wireguard.com/) in addition to OpenVPN for VPN 
  connections
- Support [High Availability](HA.md) deployments (memcached, PostgreSQL)
- Allow limits on number of (concurrent) connections per user
- Support [OpenID Connect](MOD_AUTH_OPENIDC.md) for user authentication

## Other Changes

- [APIv3](API.md) (also implemented in eduVPN / Let's Connect! 2.x servers) 
  that greatly simplifies the API and also supports WireGuard;
- [RADIUS](RADIUS.md) is only still supported on Debian 11 as the module for 
  RADIUS support no longer works with PHP >= 8;
- Usage statistics are retained for longer than 30 days;
- Remove 2FA/MFA support, 2FA is supported by leveraging an identity provider

## Security

- TLS >= 1.3 only for OpenVPN
- Ed25519 key/certificate for OpenVPN
- Tighten OAuth security by implementing OAuth 2.1 draft specification

## Operating System Support

We support installation of the VPN server software on the following operating 
systems:

- [Debian 11](DEPLOY_DEBIAN.md)
- [Ubuntu 22.04](DEPLOY_DEBIAN.md)
- [Fedora 36](DEPLOY_FEDORA.md)

We are reasonably confident we will be able to support Red Hat Enterprise Linux 
9 (and its derivatives like Rocky Linux and Alma Linux) soon after their 
release.

**Recommended OS**: Debian 11

We will support future releases of the above operating systems as soon as they 
become available. We will never support "EOL" releases of operating systems, 
and only commit to support operating systems up to 1 year after a new version 
of that OS is available. Example: you MUST upgrade to Debian 12 within one year 
of its release.

## Upgrading

In case you are currently running eduVPN / Let's Connect! 2.x on Debian 11 you 
can use the [Upgrade Instructions](FROM_2_TO_3.md) to move to 3.x. Please note 
that your users will be forced to reauthorize the official apps and/or download 
a new configuration file from the portal.

However, it is HIGHLY RECOMMENDED, if at all possible, to perform a fresh 
installation of the 3.x server!

## Issues

If you find any issue, feel free to report it to the 
[mailing list](https://list.surfnet.nl/mailman/listinfo/eduvpn-deploy), or 
directly use our [issue tracker](https://todo.sr.ht/~eduvpn/server) directly. 
Please try to provide as much information as you can that helps us to reproduce 
the issue.

If you find issues with our documentation, some parts are not fully updated for
3.x yet, we'll work with you to update the documentation when necessary so it 
will benefit all.

## Client Applications

All the official eduVPN / Let's Connect! applications have been updated to 
support the 3.x server with both OpenVPN and WireGuard. Make sure all your 
clients are updated to their latest available version. 

**NOTE** for Windows, when using the eduVPN application, the 3.0 application 
needs to be installed, which is the default for new installations, but not yet 
offered as an  update for existing 2.x client installations. This will be done 
in the coming weeks. For Let's Connect! the existing 2.x clients installations 
will offer an update to 3.0.

Full list of the available applications:

* [eduVPN](https://app.eduvpn.org/)
* [Let's Connect!](https://app.letsconnect-vpn.org/)

## Guest Usage 

If your server is currently running in what we call "Secure Internet" or 
"Guest Usage" mode, i.e. you are an NREN and provide VPN access to your 
institutes' users and users of other NRENs institutes, you MUST NOT upgrade / 
install 3.x yet. This deployment mode will be supported only from eduVPN 3.1 
onward.

## Known Issues

We are aware of the following issues with 3.x:

* VPN clients (all platforms) will always appear "Connected" when using 
  WireGuard, even if there is no VPN traffic (possible).
* Windows clients need version 3.0 of the VPN Client. Existing installations
  are (not yet) offered an updated to 3.0. Users MUST install 3.0 manually if 
  they have an existing installation of the Windows client. New installations 
  of the client will always be 3.0.
  
## Changes

The table below lists the changes to the release notes.

| Date       | Note                      |
| ---------- | ------------------------- |
| 2022-05-24 | Initial 3.x Release Notes | 
