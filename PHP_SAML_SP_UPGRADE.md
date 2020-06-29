# Who?

This document is ONLY relevant if you were using the experimental 
`SamlAuthentication` authentication module in your VPN portal. As this module 
is experimental we kept the freedom to break things if necessary without you 
being able to complain about that ;-) However, it is nice to "support" it at 
least a little bit.

# What?

Versions of vpn-user-portal < 2.2.0 supported only the `SamlAuthentication`
method. From 2.2.0 there is support for both `SamlAuthentication` and 
`PhpSamlSpAuthentication`. The former is a "full" SAML SP application, similar 
to simpleSAMLphp in how it functions. From version 2.3.0 support for 
`SamlAuthentication` will be removed, and thus any user of this MUST upgrade to 
`PhpSamlSpAuthentication`. Luckily, this is quite easy! It also makes sense to 
upgrade in window between the 2.2.0 release and the 2.3.0 release as it gives 
you the option and time to switch back if necessary and complain to us.

# How?

Make sure your system is fully up to date by installing and applying all 
updates and reboot. When updating to 2.2.0 everything will keep working as-is, 
don't worry.

Figure out which IdP is currently supported by looking for `idpEntityId` in 
`/etc/vpn-user-portal/config.php` configure that as an entry in 
`/etc/php-saml-sp/config.php` under `idpList`. In case you were using a 
discovery service you would have to check your discovery service configuration 
for which IdPs are supported and include all of them under `idpList` in 
`/etc/php-saml-sp/config.php`. The metadata used before is specified under 
`idpMetadata`. Copy this file to `/etc/php-saml-sp/metadata` (as root):

	# mkdir /etc/php-saml-sp/metadata
	# cp /path/to/idp/metadata.xml /etc/php-saml-sp/metadata

You can set the entity ID of your SP under `entityId` if you want to keep 
using the old one. The default SP entityID for `php-fkooman-saml-sp` was 
`https://vpn.example.org/vpn-user-portal/_saml/metadata`. The default SP 
entity ID of `php-saml-sp` is `https://vpn.example.org/php-saml-sp/metadata`. 
Keeping the entity ID the same is especially important when using 
`eduPersonTargetedID` as the identity depends on the entity ID of the SP.

Once you configured these, your new SP should be up and running. Now you need 
to talk to your IdP(s) to reimport the metadata from 
`https://vpn.example.org/php-saml-sp/metadata`. After that is done your can 
run an authentication test from `https://vpn.example.org/php-saml-sp/`. If it 
doesn't work, review your `/etc/php-saml-sp/config.php` file and make sure 
the metadata is correctly made available under `/etc/php-saml-sp/metadata` as 
XML files, e.g. `idp-1.xml`, `idp-2.xml`, ..., `idp-n.xml`. However, feel free
to name them any way you like, as long as they end in `.xml` it is fine. 
Typically you want to indicate in the name for which IdP it is, though :-)

Once everything works, you can switch `vpn-user-portal` to use `php-saml-sp` 
instead of `php-fkooman-saml-sp`:

Rename `SamlAuthentication` under `/etc/vpn-user-portal/config.php` to 
`PhpSamlSpAuthentication` and set the `authMethod` to 
`PhpSamlSpAuthentication`. 
The following options left over from `SamlAuthentication` are no longer needed 
and can be removed. They are now configured in `php-saml-sp`:

* `spEntityId`
* `idpMetadata`
* `idpEntityId`
* `discoUrl`

The rest stays as is. After making these changes, the VPN portal should be 
using php-saml-sp!

# Cleanup 

After everything works you can now remove the old SAML keys:

    # rm /etc/vpn-user-portal/sp.*
