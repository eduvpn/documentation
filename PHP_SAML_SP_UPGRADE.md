# Who?

This document is ONLY relevant if you were using the experimental "php-saml-sp"
authentication module in your VPN portal. As this module was experimental we 
kept the freedom to break things if necessary :-)

# What?

Versions of vpn-user-portal < 2.2.0 supported only the `php-fkooman-saml-sp`
library. From 2.2.0 there is support for both `php-fkooman-saml-sp` and 
`php-saml-sp`. The former is a "full" SAML SP application, similar to 
simpleSAMLphp in how it functions. From version 2.3.0 support for the 
`php-fkooman-saml-sp` is removed, and thus any user of `php-fkooman-saml-sp` 
MUST upgrade to `php-saml-sp`. Luckily, this is quite easy!

# How?

Make sure your system is fully up to date by installing and applying all 
updates and rebooting if necessary.

Switch from `php-fkooman-saml-sp` to `php-saml-sp`. This will NOT break the 
SAML authentication you have currently configured:

On CentOS:

	$ sudo yum swap php-fkooman-saml-sp php-saml-sp

On Fedora:

	$ sudo dnf swap php-fkooman-saml-sp php-saml-sp
	
Make sure you restart Apache at this point:

	$ sudo systemctl restart httpd

Copy your metadata file(s) from `/etc/vpn-user-portal/metadata` to 
`/etc/php-saml-sp/metadata` (as root):

	# mkdir /etc/php-saml-sp/metadata
	# cp /etc/vpn-user-portal/metadata/* /etc/php-saml-sp/metadata
	
Figure out which IdP is currently supported by looking for 
`idpEntityId` in `/etc/vpn-user-portal/config.php` configure
that as an entry in `/etc/php-saml-sp/config.php` under `idpList`. In case 
you were using a discovery service you would have to check your discovery 
service configuration for which IdPs are supported and include all of them 
under `idpList` in `/etc/php-saml-sp/config.php`.

You can set the entity ID of your SP under `entityId` if you want to keep 
using the old one. The default SP entityID for `php-fkooman-saml-sp` was 
`https://vpn.example.org/vpn-user-portal/_saml/metadata`. The default SP 
entity ID of `php-saml-sp` is `https://vpn.example.org/php-saml-sp/metadata`.

Once you configured these, your new SP should be up and running. Now you need 
to talk to your IdP(s) to reimport the metadata from 
`https://vpn.example.org/php-saml-sp/metadata`. After that is done your can 
run an authentication test from `https://vpn.example.org/php-saml-sp/`. If it 
doesn't work, review your `/etc/php-saml-sp/config.php` file and make sure 
the metadata is correctly made available under `/etc/php-saml-sp/metadata` as 
XML files, e.g. `idp-1.xml`, `idp-2.xml`, ..., `idp-n.xml`.

Once everything works, you can switch `vpn-user-portal` to use `php-saml-sp` 
instead of `php-fkooman-saml-sp`:

Rename `SamlAuthentication` under `/etc/vpn-user-portal/config.php` to 
`PhpSamlAuthentication`. Set the `authMethod` to `PhpSamlAuthentication`. The 
following options left over from `php-fkooman-saml-sp` are no longer needed 
and can be removed:

* `spEntityId`
* `idpMetadata`
* `idpEntityId`
* `discoUrl`

The rest stays as is. After making these changes, the VPN portal should be 
using php-saml-sp.