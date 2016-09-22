# Introduction

This document describes how to configure SAML authentication for deployed
systems. We assume you used the `deploy.sh` script to deploy eduvpn. Below we
assume you use `vpn.example`, but modify this domain to your own domain name!

A convenient script is installed by `mod_auth_mellon` to generate all 
required files to configure the SAML SP:

    $ /usr/libexec/mod_auth_mellon/mellon_create_metadata.sh https://vpn.example/saml https://vpn.example/saml

Copy the files:

    $ sudo mkdir /etc/httpd/saml
    $ sudo cp *.cert *.key *.xml /etc/httpd/saml

Fetch the IdP metadata from the IdP. For example, for SURFconext you would use 
the following:

    $ curl -o SURFconext.xml https://engine.surfconext.nl/authentication/idp/metadata

Now copy the metadata as well:

    $ sudo cp SURFconext.xml /etc/httpd/saml

The follow file you place in `/etc/httpd/conf.d/saml.conf`:

    <Location />
        MellonEnable "info"
        MellonSPPrivateKeyFile /etc/httpd/saml/https_vpn.example_saml.key
        MellonSPCertFile /etc/httpd/saml/https_vpn.example_saml.cert
        MellonSPMetadataFile /etc/httpd/saml/https_vpn.example_saml.xml
        MellonIdPMetadataFile /etc/httpd/saml/SURFconext.xml
        MellonEndpointPath /saml
    </Location>

    <Location /portal>
        MellonEnable "auth"
    </Location>

    # Disable Mellon for the API
    <Location /portal/api/config>
        MellonEnable "off"
    </Location>

    #<Location /admin>
    #    MellonEnable "auth"
    #
    #    MellonCond "NAME_ID" "aa3f6fade450f12aa891bf066b86921344e2a1f1" [OR]
    #    MellonCond "NAME_ID" "234"
    #</Location>

Restart the web server:

    $ sudo systemctl restart httpd

Now when you visit `https://vpn.example/portal/` you should be 
redirected to the IdP. If this works, you probably need to register your SP
at your IdP. You can use the following URL with metadata:

    https://vpn.example/saml/metadata

You also need to modify the `vpn-user-portal` configuration to specify the 
attribute that should be used to identify the users.

Edit `/etc/vpn-user-portal/vpn.example/config.yaml` and set:
        
    authMethod: MellonAuthentication

By default the NAME_ID will be used to identify the users, if you want to 
change that change the `attribute` value under `MellonAuthentication`.

If you want to also have `vpn-admin-portal` be protected by SAML, make sure
you uncomment the `<Location /admin>` section above and figure out 
the attribute and values they should have to match with administrators. Also 
modify `/etc/vpn-admin-portal/vpn.example/config.yaml` analogue to the 
modifications for `vpn-user-portal`.

That should be all!
