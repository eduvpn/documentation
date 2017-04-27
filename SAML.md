# Introduction

This document describes how to configure SAML authentication for deployed
systems. We assume you used the `deploy.sh` script to deploy eduvpn. Below we
assume you use `vpn.example`, but modify this domain to your own domain name!

A convenient script is installed by `mod_auth_mellon` to generate all 
required files to configure the SAML SP:

    $ /usr/libexec/mod_auth_mellon/mellon_create_metadata.sh https://vpn.example/saml https://vpn.example/saml

You can now modify the `https_vpn.example_saml.xml` file. Make sure the 
`<NameIDFormat>` is set to 
`urn:oasis:names:tc:SAML:2.0:nameid-format:persistent`.

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
if you want to enable SAML for the admin portal as well, be sure to add some 
user IDs to the `MellonCond` lines.

Restart the web server:

    $ sudo systemctl restart httpd

Now when you visit `https://vpn.example/portal/` you should be 
redirected to the IdP. If this works, you probably need to register your SP
at your IdP. You can use the following URL with metadata:

    https://vpn.example/saml/metadata

You also need to modify the `vpn-user-portal` configuration to specify the 
attribute that should be used to identify the users.

Edit `/etc/vpn-user-portal/vpn.example/config.php` and set:
        
    'authMethod' => 'MellonAuthentication'

By default the NAME_ID will be used to identify the users, if you want to 
change that change the `attribute` value under `MellonAuthentication`.

If you want to also have `vpn-admin-portal` be protected by SAML, make sure
you uncomment the `<Location /admin>` section in 
`/etc/httpd/conf.d/vpn.example.conf` and figure out the attribute values that 
are associated with the administrator(s). 

Also modify `/etc/vpn-admin-portal/vpn.example/config.php` in the same way as 
the user portal.
