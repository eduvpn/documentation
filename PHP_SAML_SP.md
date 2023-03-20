# SAML (php-saml-sp)

Very simple, secure SAML SP written in PHP.

## Why

This application was written to be (a lot) simpler to use and configure than 
simpleSAMLphp and only work as a SAML SP supporting only secure cryptographic 
algorithms, see the project [site](https://www.php-saml-sp.eu/) for more 
information.

## Installation

Enable the repository for your platform as instructed 
[here](https://www.php-saml-sp.eu/). Make sure you use the repository for `v2`!

### Fedora

    $ sudo dnf -y install php-saml-sp
    $ sudo systemctl restart httpd

### Debian

    $ sudo apt -y install php-saml-sp
    $ sudo a2enconf php-saml-sp
    $ sudo systemctl restart apache2

## Configuring the SP

See `/etc/php-saml-sp/config.php`. 

The metadata URL is `https://vpn.example.org/php-saml-sp/metadata`. The 
entityID is the same (by default). You can override this by setting `entityId` 
to a value of your choice, e.g. `https://vpn.example.org/saml` to be vendor 
neutral in case you want to switch later. Choosing something stable here is 
important when you use for example `eduPersonTargetedID` as that identifier
is typically bound to the SP entityID.

Copy the IdP(s) metadata to `/etc/php-saml-sp/metadata`. Make sure the metadata
files have the `.xml` extension and are valid XML.

Make sure you at least configure `idpList` in `/etc/php-saml-sp/config.php` 
with the list of IdPs that have access to this SP. If you don't do this, all 
IdPs found in the metadata will be allowed access.

To test your SP/IdP configuration, go to `https://vpn.example.org/php-saml-sp/` 
and use the "Test" button.

You can look 
[here](https://git.sr.ht/~fkooman/php-saml-sp/tree/main/item/METADATA.md) if 
you want all details on how to (properly) configure IdP metadata, including 
dynamic refresh.

## Configuring the VPN Service

The configuration is done through `/etc/vpn-user-portal/config.php`.

Set the `authModule` option:

```
'authModule' => 'PhpSamlSpAuthModule',
```

Now the `PhpSamlSpAuthModule` specific options can be set as well:

```
'PhpSamlSpAuthModule' => [
    'userIdAttribute' => 'eduPersonTargetedID',
    //'userIdAttribute' => 'eduPersonPrincipalName',

    //'permissionAttributeList' => [
    //      'eduPersonEntitlement',
    //      'eduPersonAffiliation',
    //],

    // AuthnContext required for *all* users
    //'authnContext' => ['urn:oasis:names:tc:SAML:2.0:ac:classes:TimesyncToken'],
],
```

The `permissionAttributeList` option contains attribute(s) that will be used
for _authorization_ in the VPN server, see [ACL](ACL.md) for more information.


The `authnContext` will request the specified AuthnContext of the IdP, this is 
to trigger for example MFA/2FA. It integrates with 
[SURFsecureID](https://wiki.surfnet.nl/display/SsID/SURFsecureID) as well. 
Setting `authnContext` means this context will be required for ALL users.
