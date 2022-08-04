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

### Style

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

### Session Expiry

We have separate documentation for session expiry, look 
[here](SESSION_EXPIRY.md).

### Database

You can switch to using another database if you do not want to use the default 
SQLite. We documented this [separately](DATABASE.md).

### Authentication

We support various user authentication mechanisms. We document all of them 
separately:

* [LDAP](LDAP.md)
* [SAML](SAML.md)
  * [Shibboleth](SHIBBOLETH_SP.md)
  * [php-saml-sp](PHP_SAML_SP.md)
  * [mod_auth_mellon](MOD_AUTH_MELLON.md)
* [Client Certificates](CLIENT_CERT_AUTH.md)
* [RADIUS](RADIUS.md)
* [OpenID Connect](MOD_AUTH_OPENIDC.md)

Please follow the instructions there.

### Access Control

Access to the portal can be restricted in different ways. They are documented
separately:

* [Access Permission List](ACL.md#access-to-the-service) - determine who gets
  access to the service;
* [Admin Permission List](PORTAL_ADMIN.md#permission) - determine who gets 
  admin permissions in the portal, based on an attribute value;
* [Admin User ID List](PORTAL_ADMIN.md#user-id) - determine who gets admin 
  permissions in the portal, based on user ID.

### Portal Language

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

### Show Permissions

Previous server versions would show the user's _permissions_ as conveyed 
through the authentication mechanism, e.g. SAML or LDAP attribute values.

This has been disabled by default now. You can enable it again:

```php
'showPermissions' => true,
```

### Maximum Number of Active Configurations

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

### WireGuard

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

### Session Module

If you are using a HA Portal setup configuration for your portal you should
switch to a different session mechanism. This is documented 
[here](HA_PORTAL.md).