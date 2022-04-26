The VPN service supports access control. This allows configuring that users 
require certain "permissions" to access a particular VPN profile. This is 
useful if you have multiple types of users. For example, only employees get 
access to the "Employees" profile, but students do not. You can also require 
certain permissions to be able to use the Portal/API at all.

Currently, the following access control mechanisms are supported:

- SAML (via SAML attribute, e.g. `eduPersonAffiliation` or 
  `eduPersonEntitlement`)
- LDAP (via LDAP attribute, e.g. `memberOf`)

The permissions are _cached_ for up to a configurable period through 
[Session Expiry](SESSION_EXPIRY.md). By default this is 90 days, but can easily 
be modified. This cache is required, because not all authentication backends 
have a way to validate the permissions "out of band", i.e. when the user is not 
actively in the process of authenticating.

# Configuration

The configuration is done in `/etc/vpn-user-portal/config.php`.

## SAML

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

## LDAP

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

## Admin/Portal/API Access

You can restrict access to the Portal/API to certain permissions. For example,
if you only went `employees` to be able to access the VPN service and not 
`students`, you can. in addition to profile restrictions (see next section) 
prevent them from accessing the service at all.

In `/etc/vpn-user-portal/config.php` you can configure it like this:

```
'accessPermissionList' => ['employees'],
```

This requires everyone to have the permission `employees`. If you specify more
than one "permission", the user needs to be member of only one. The permissions
are thus "OR".

In order to provide access to the "Admin" part of the portal, see 
[PORTAL_ADMIN](PORTAL_ADMIN.md).

## Profile Mapping

Add the authorized attribute values to `aclPermissionList` for each of the 
profiles where you want to restrict access, for example:

The values of `aclPermissionList` come from the `permissionAttribute` as 
configured in your authentication module. You can verify which values are 
available for your account by going to the "Account" page in your portal. It 
will be listed under your "User ID". If nothing is shown there, you need to 
either make sure your account has any permissions, or logout and login again.

```
'aclPermissionList' => [
    'http://eduvpn.org/role/admin',
],
```
