# Introduction

This document describes how to configure SAML authentication for deployed
systems. We assume you used the `deploy.sh` script to deploy the software. 
Below we assume you use `vpn.example`, but modify this domain to your own 
domain name!

## Installation

First install `mod_auth_mellon`:

    $ sudo yum -y install mod_auth_mellon

## Configuration

A convenience script is installed by `mod_auth_mellon` to generate all 
required files to configure the SAML SP:

    $ /usr/libexec/mod_auth_mellon/mellon_create_metadata.sh https://vpn.example/saml https://vpn.example/saml

You can now modify the `https_vpn.example_saml.xml` file. Make sure the 
`<NameIDFormat>` is set to 
`urn:oasis:names:tc:SAML:2.0:nameid-format:persistent` if you want to use the 
NameID as the user ID:

    $ sed -i 's/urn:oasis:names:tc:SAML:2.0:nameid-format:transient/urn:oasis:names:tc:SAML:2.0:nameid-format:persistent/' https_vpn.example_saml.xml

Copy the files:

    $ sudo mkdir /etc/httpd/saml
    $ sudo cp *.cert *.key *.xml /etc/httpd/saml

Fetch the IdP metadata from the IdP. For example, for SURFconext you would use 
the following:

    $ curl -o SURFconext.xml https://engine.surfconext.nl/authentication/idp/metadata

Now copy the metadata as well:

    $ sudo cp SURFconext.xml /etc/httpd/saml

Modify your `/etc/httpd/conf.d/vpn.example.conf`, and enable the SAML lines 
there. Make sure you modify the lines that refer to certificates and keys and
if you want to enable SAML for the admin portal as well.

Restart the web server:

    $ sudo systemctl restart httpd

Now when you visit `https://vpn.example/vpn-user-portal/` you should be 
redirected to the IdP. If this works, you probably need to register your SP
at your IdP. You can use the following URL with metadata:

    https://vpn.example/saml/metadata

You also need to modify the `vpn-user-portal` configuration to specify the 
attribute that should be used to identify the users.

Edit `/etc/vpn-user-portal/default/config.php` and set:
        
    'authMethod' => 'MellonAuthentication'

By default the NAME_ID will be used to identify the users, if you want to 
change that change the `attribute` value under `MellonAuthentication`.

If you want to also have `vpn-admin-portal` be protected by SAML, make sure
you uncomment the `<Location /vpn-admin-portal>` section in 
`/etc/httpd/conf.d/vpn.example.conf` and figure out the attribute values that 
are associated with the administrator(s). 

Also modify `/etc/vpn-admin-portal/default/config.php` in the same way as 
the user portal.

**NOTE** if you want to allow access to the admin portal, you MUST also set 
some mechanism, either through userId or entitlement authorization, see the 
example configuration file in 
`/usr/share/doc/vpn-admin-portal-VERSION/config.php.example`!

## Discovery

If you use only one IdP or an identity federation that provides their own 
WAYF service (the default), you don't need to do anything else. If you want to 
provide your own WAYF, this is also possible with the 
[php-saml-ds](https://github.com/fkooman/php-saml-ds/) software.

You can install the software:

    $ sudo yum -y install php-saml-ds

Modify the configuration in `/etc/php-saml-ds/config.php` and make sure the 
IdP metadata file(s) are placed in `/etc/php-saml-ds/metadata/`. As entityID
of the SP you need to use `https://vpn.example/saml`. Specify the entityIDs
of the IdPs you want to show up in the WAYF in the configuration file under 
`idpList` as well.

Run the file generator:

    $ sudo php-saml-ds-generate

This should download the logos if enabled and create configuration files.

Modify `/etc/httpd/conf.d/vpn.example.conf` by removing or commenting out the 
`MellonIdPMetadataFile` field and enabling the following two and configure 
them like this:

    MellonIdPMetadataFile /var/lib/php-saml-ds/https_vpn.example_saml.xml
    MellonDiscoveryUrl "https://vpn.example/php-saml-ds/index.php"

Restart Apache:

    $ sudo systemctl restart httpd

If you now browse to https://vpn.example/ you will get redirected to the WAYF 
and shown it. If there is only one IdP configured the WAYF will be skipped and
you'll directly end up at the IdP.
