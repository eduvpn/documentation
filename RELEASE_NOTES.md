# Release Notes

These are the releases notes of eduVPN / Let's Connect! 3.x. They will be 
updated as needed. It is a big release consisting of many changes.

As this is a new major release, we expect some (minor) issues to still exist 
that we'll run into in the next weeks/months, so it is important to regularly 
update your system using the `vpn-maint-update-system` command.

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

We are reasonably confident we will be able to support RHEL 9 (and its 
derivatives) soon after their release.

**Recommended OS**: Debian 11

We will support future releases of the above operating systems as soon as they 
become available. We will never support "EOL" releases of operating systems, 
and only support operating systems up to 1 year after a new version of that OS 
is available. Example: you MUST upgrade to Debian 12 within one year of its 
release.

## Upgrading

In case you are currently running eduVPN / Let's Connect! 2.x on Debian 11 you 
can use the [upgrade instructions](FROM_2_TO_3.md) to move to 3.x. Please note 
that your users will be forced to reauthorize the official apps and/or download 
a new configuration file from the portal.

However, it is recommended, if at all possible, to perform a fresh installation 
of the 3.x server!

## Issues

If you find any issue, feel free to report it to the 
[mailing list](https://list.surfnet.nl/mailman/listinfo/eduvpn-deploy), or use 
our [issue tracker](https://todo.sr.ht/~eduvpn/server) directly. Please try to 
provide as much information as you can that helps us to reproduce the issue.

If you find issues with our documentation, some parts are not fully updated to
3.x, we'll work with you to update the documentation when necessary so it will
benefit all.

## Client Applications

All the official eduVPN / Let's Connect! applications have been updated to 
support the 3.x server with both OpenVPN and WireGuard. Make sure all your 
clients are updated to their latest available version. For Windows the 3.0 
application needs to be installed, which is the default for new installations, 
but not yet pushed as an update for existing 2.x client installations. This 
will be done in the coming weeks.

## Guest Usage 

If your server is currently running in what we call "Secure Internet" or 
"Guest Usage" mode, i.e. you are an NREN and provide VPN access to your 
institutes' users and users of other NRENs institutes, you MUST NOT upgrade. 
This deployment mode will be supported only from eduVPN 3.1 onward.
