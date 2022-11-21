The VPN service supports access control. You can:

1. Restrict who has access to the server;
2. Restrict who has access to certain VPN profiles;
3. Determine who has admin privileges.

Restricting access to the server and to VPN profiles is documented here. To 
configure who has access to the admin, look [here](PORTAL_ADMIN.md).

Currently, the following access control mechanisms are supported:

- SAML (via SAML attribute, e.g. `eduPersonAffiliation` or 
  `eduPersonEntitlement`)
- LDAP (via LDAP attribute, e.g. `memberOf`)
- Static Permissions (via JSON file)

The permissions are _cached_ for up to a configurable period through 
[Session Expiry](SESSION_EXPIRY.md). By default this is 90 days, but can easily 
be modified. This cache is required, because not all authentication backends 
have a way to reliably validate the permissions "out of band", i.e. when the 
user is not actively in the process of authenticating.

The configuration is done in `/etc/vpn-user-portal/config.php`.

## Methods

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
