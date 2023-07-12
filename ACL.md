# Access Control

The VPN service supports access control, i.e. authorization. You can:

1. Restrict who has access to the server;
2. Restrict who has access to certain VPN profiles;
3. Determine who has admin privileges.

Restricting access to the server and to VPN profiles is documented here. To 
configure who has access to the admin, look [here](PORTAL_ADMIN.md).

There are currently two _sources_ for authorization information:

1. User Authentication
    - LDAP attribute, SAML attributes, OIDC claims, ...
2. Static Permissions
    - Locally assign permissions based on User ID

The information obtained during user authentication (1) is cached for the 
duration of the browser session when using the portal, and for the duration of 
the [Session Expiry](SESSION_EXPIRY.md) when using the API.

The reason for this is that there is not always a way to obtain _fresh_ 
information about the user directly from the authenication source, for example
when using SAML (WebSSO), or it might be "expensive" to do that on every page 
load.

Currently, the static permissions (2) _are_ updated immediately when using the 
portal, but not when using the API.

We are looking at implementing "real time" updating of authorization 
information when using the API for authentication backends that support this
([#131](https://todo.sr.ht/~eduvpn/server/131)).

We are also working on implementing access control based on the user's origin 
IP ([#146](https://todo.sr.ht/~eduvpn/server/146)).

The configuration of access control is done primarily through 
`/etc/vpn-user-portal/config.php`, see below for more details.

## User Authentication

Here you'll find how to obtain authorization information through the various
user authentication mechanisms.

### SAML

We assume [SAML](SAML.md) is already configured and working.

You have to choose a SAML attribute you want to use for determining the 
membership. Typically, that would be `eduPersonEntitlement` or 
`eduPersonAffiliation`, but any SAML attribute will do.

In order to configure this, modify `/etc/vpn-user-portal/config.php` 
and add the attribute to the `permissionAttributeList` list. For example:

```
'ShibAuthModule' => [

    // ...
    
    'permissionAttributeList' => ['entitlement'],
    
    // ...
],
```

In order to test whether everything works fine, you can enable the 
`showPermissions` option in `/etc/vpn-user-portal/config.php` by setting it to 
`true`. This will show the "raw" permissions on the user's "Account" page.

### LDAP

We assume [LDAP](LDAP.md) is already configured and working. 

You have to choose an LDAP attribute you want to use for determining the 
membership. Typically, that would be `memberOf`, but any LDAP attribute will work.

In order to configure this, modify `/etc/vpn-user-portal/config.php` 
and set the `permissionAttributeList` to the name of the attribute:

```
'LdapAuthModule' => [
    
    // ...
    
    'permissionAttributeList' => ['memberOf'],

    // ...
],
```

In order to test whether everything works fine, you can enable the 
`showPermissions` option in `/etc/vpn-user-portal/config.php` by setting it to 
`true`. This will show the "raw" permissions on the user's "Account" page.

## Static

**NOTE**: this has been implemented in vpn-user-portal >= 3.1.8

You can use a (JSON) file where the mapping between permissions and users are 
stored.

This file is stored in `/etc/vpn-user-portal/static_permissions.json` and has 
the following format:

```json
{
    "administrators": [
        "foobar",
        "foobaz"
    ],
    "employees": [
        "foobar",
        "foo",
        "bar",
        "baz"
    ]
}
```

This means that the users `foobar` and `foobaz` get the `administrators` 
permission and the users `foobar`, `foo`, `bar` and `baz` get the `employees`
permission. Note that the user `foobar` has _two_ permissions.

These permissions do not mean anything by themselves, and need to be further 
mapped, e.g. through `accessPermissionList`, `aclPermissionList` or 
`adminPermissionList` in `/etc/vpn-user-portal/config.php`. See below for 
more information.

The existence of this file activates "Static Permissions" for your server. Make 
sure it in the correct format, see the example above.

## Access to the Service

You can restrict access to the Portal/API to certain permissions. For example,
if you only went `employees` to be able to access the VPN service and not 
`students`, you can in addition to profile restrictions (see next section), 
prevent them from accessing the service at all.

In `/etc/vpn-user-portal/config.php` you can configure it like this:

```
'accessPermissionList' => ['employees'],
```

This requires everyone to have the permission `employees`. If you specify more
than one "permission", the user needs to be member of only one. The permissions
are thus "OR".

If you specify `[]`, nobody will get access. If you leave this option away, 
everyone (who can authenticate) gets access (the default).

## Profile Authorization

Add the authorized attribute values to `aclPermissionList` for each of the 
profiles where you want to restrict access, for example:

The values of `aclPermissionList` come from the `permissionAttribute` as 
configured in your authentication module. You can verify which values are 
available for your account by going to the "Account" page in your portal. It 
will be listed under your "User ID". If nothing is shown there, you need to 
either make sure your account has any permissions, or logout and login again.

```
'aclPermissionList' => [
    'employees',
],
```

This requires everyone to have the permission `employees` before being allowed
access to the profile.. If you specify more than one "permission", the user 
needs to be member of only one. The permissions are thus "OR".

## Session Expiry

See [Per User Session Expiry](SESSION_EXPIRY.md#per-user-session-expiry).
