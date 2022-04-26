Certain users can be "promoted" to admin in the VPN portal. This can be done in
two ways, based on either

1. User ID
2. Permission

The User ID based "admin" authorization is the simplest. However, if the 
admins regularly change, or are already based on a certain role exposed through 
the identity management system, using permissions may make more sense.

### User ID

Modify `/etc/vpn-user-portal/config.php` and add the user IDs to the 
`adminUserIdList`, e.g.:

```
'adminUserIdList' => ['admin', 'john', 'jane'],
```

This is the simplest solution. To view the user ID of your account, you can use 
the "Account" page when logged into the portal.

### Permission

When the "admins" are already decided on through the identity management 
system, e.g. LDAP or SAML, it makes sense to use that "permission" / "role" to 
identify users.

**NOTE**: if multiple (SAML) IdPs are linked to the VPN service, there is no 
way to "scope" the permission to a particular IdP at the moment. So be careful
when using a permission based "admin" as IdPs can potentially set the "admin"
permission for users not allowed to access the admin part of the portal! In 
that case you SHOULD use the User ID admin configuration mentioned above 
instead!

In order to configure the permissions, first the attribute has to be selected 
for this. This can be for example the `eduPersonEntitlement` attribute where 
the administrators get the "admin" entitlement. 

One can set the `permissionAttributeList` under the various authentication 
mechanisms.

For example on [Shibboleth](SHIBBOLETH_SP.md):

```
'permissionAttributeList' => ['entitlement'],
```

Then you have to configure _which_ entitlement will grant administrator access
using the `adminPermissionList` option, for example:

```
'adminPermissionList' => ['http://eduvpn.org/role/admin'],
```

This should make all users that have that particular entitlement value an 
administrator in the portal.
