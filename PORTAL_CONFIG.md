# Portal Configuration

This document explains all configuration options that do not belong to profile
specific configuration as documented separately in 
[Profile Config](PROFILE_CONFIG.md).

The default _template_ for the configuration file of the VPN user portal can
be found 
[here](https://git.sr.ht/~fkooman/vpn-user-portal/tree/v3/item/config/config.php.example).

It is this template that is used during installation and you can modify as an
admin. It is available under `/etc/vpn-user-portal/config.php`.

Below we'll discuss all the configuration options in their relevant sections. 
As mentioned, the VPN profile configuration is already documented 
[here](PROFILE_CONFIG.md).

## Style

You can _style_ the VPN portal by setting the `styleName` option. Currently, 
two styles are available, `eduVPN` for eduVPN and `LC` for Let's Connect!. 

The styles are not installed by default, but you can install them by 
installing the package `vpn-portal-artwork-eduvpn` / `vpn-portal-artwork-lc` 
on Debian/Ubuntu and `vpn-portal-artwork-eduVPN` / `vpn-portal-artwork-LC` on 
Fedora/EL.

Example:

```php
'styleName' => 'eduVPN',
```

If you want to implement your own (custom) branding, you can look 
[here](CUSTOM_BRANDING.md) on how to do that.

## Session Expiry

We have separate documentation for session expiry, look 
[here](SESSION_EXPIRY.md).

## Database

You can switch to using another database if you do not want to use the default 
SQLite. We documented this [separately](DATABASE.md).

## Authentication

We support various user authentication mechanisms. We document all of them 
separately:

* [Local User Database](DB_AUTH.md) (default)
* [LDAP](LDAP.md)
* [SAML](SAML.md)
    * [Shibboleth](SHIBBOLETH_SP.md)
    * [php-saml-sp](PHP_SAML_SP.md)
    * [mod_auth_mellon](MOD_AUTH_MELLON.md)
* [Client Certificates](CLIENT_CERT_AUTH.md)
* [RADIUS](RADIUS.md)
* [OpenID Connect](MOD_AUTH_OPENIDC.md)

Please follow the instructions there.

## Access Control

Access to the portal can be restricted in different ways. They are documented
separately:

* [Access Permission List](ACL.md#access-to-the-service) - determine who gets
  access to the service;
* [Admin Permission List](PORTAL_ADMIN.md#permission) - determine who gets 
  admin permissions in the portal, based on an attribute value;
* [Admin User ID List](PORTAL_ADMIN.md#user-id) - determine who gets admin 
  permissions in the portal, based on user ID.

## Portal Language

The portal is translated in a wide number of languages. You can set the 
default language of the portal, and the available languages. The user can 
switch languages if more than one is configured.

Example:

```php
'enabledLanguages' => ['nl-NL', 'en-US'],
'defaultLanguage' => 'en-US',
```

If you want to contribute translations, you can find out how to do that 
[here](CONTRIBUTE_TRANSLATIONS.md).

## Show Permissions

Previous server versions would show the user's _permissions_ as conveyed 
through the authentication mechanism, e.g. SAML or LDAP attribute values.

This has been disabled by default now. You can enable it again:

```php
'showPermissions' => true,
```

## Maximum Number of Active Configurations

Here you can configure how many configurations can be active at the same time,
when the user manually downloads configurations through the VPN Portal. The
default is `3`. You can set it to `0` if you want to disable manual VPN 
configuration downloads and want to force the user to use the VPN client 
applications through the API.

Example:

```php
'maxActiveConfigurations' => 5,
```

**NOTE**: this is _independent_ from the maximum number of active 
configurations obtained through the API! See 
[here](#maximum-number-of-active-api-configurations) for restricting the number 
of active configurations through the API.

## Maximum Number of Active API Configurations

Limit the number of active VPN configurations obtained through the API that is
used by the eduVPN/Let's Connect! VPN applications. Effectively this means that 
the user can have this many VPN apps connected simultaneously.

```php
'Api' => [
    'maxActiveConfigurations' => 3,
],
```

The user *can* authorize as many VPN clients as they want, but the number of
active simultaneous connections is limited by this value. If set to 3, and a 
4th client attempts to connect, the client that was connected the longest will 
automatically be disconnected.

## WireGuard

You can configure the WireGuard port over which VPN clients can connect to the
WireGuard service. The default is `51820`. WireGuard only supports UDP so there
is no need to specify the IP protocol.

A good alternative would be to set it to port `443`, which is also used by the
new HTTP over QUIC protocol which may increase the chances the traffic is not
blocked by firewalls.

Example:

```php
'WireGuard' => [
    'listenPort' => 443,
],
```

**NOTE**: make sure you update the [firewall](FIREWALL.md) if you change the 
port!

**NOTE**: there's an issue on EL9 with SELinux when you want to change the 
port. See issue [#123](https://todo.sr.ht/~eduvpn/server/123) for the status.

## Session Module

If you are using a HA Portal setup configuration for your portal you should
switch to a different session mechanism. This is documented 
[here](HA_PORTAL.md).

## Script Connection Hook

**NOTE**: this is a [Preview Feature](PREVIEW_FEATURES.md)! It is NOT yet 
officially supported and meant for testing only!

 Added: 3.0.4 ([#84](https://todo.sr.ht/~eduvpn/server/84))

You can run a script after a VPN client connects and/or disconnects. This is
documented [here](SCRIPT_CONNECTION_HOOK.md).

## Remove Authorization on Disconnect

**NOTE**: this is a [Preview Feature](PREVIEW_FEATURES.md)! It is NOT yet 
officially supported and meant for testing only!

Added: 3.0.5 ([#78](https://todo.sr.ht/~eduvpn/server/78))

The server can delete the OAuth authorization as used for server API access by 
the eduVPN/Let's Connect! applications.

This would force the user to authorize (and thus authenticate) again the next
time a VPN connection is established. This may be particularlly interesting for
organization that have MFA enabled and want to force users to authenticate 
every time they connect to the VPN.

You can enable this in `/etc/vpn-user-portal/config.php`:

```php
'Api' => [
    'deleteAuthorizationOnDisconnect' => true,
],
```

The authorization is ONLY deleted when the user *manually* disconnects, closes 
the VPN application, or reboots the system. System suspend, or (temporary) loss 
of network connectivity will NOT force the user to authorize the application 
again!

### Caveats

* This is restricted to the eduVPN/Let's Connect! VPN clients only, it does not 
  work when users manually download VPN configurations through the portal! If 
  necessary, you can [disable](#maximum-number-of-active-configurations) manual 
  configuration downloads;
* Users could write their own client that implements the API and mimics the 
  official client, but omits the call to `/disconnect`. So this is not 
  "bullet proof". One should also use [Session Expiry](#session-expiry) to 
  limit the duration of a VPN session if that is considered important;
* We have NOT tested this extensively on all VPN clients, this feature depends 
  on the VPN clients properly calling the `/disconnect` API call (at the right
  moment). Please help us test this properly.
