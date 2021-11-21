---
title: Mellon
description: SAML Authentication using mod_auth_mellon
category: authentication
---

Below we assume you use `vpn.example`, but modify this domain to your own 
domain name!

# Installation

## CentOS 

First install `mod_auth_mellon`:

    $ sudo yum -y install mod_auth_mellon

## Debian

    $ sudo apt -y install libapache2-mod-auth-mellon

In the examples below you will not use `/etc/httpd` but `/etc/apache2` as the
base path, and for `systemctl` you use `apache2` instead of `httpd`.

# Configuration

Generate an SP signing key:

    $ openssl req \
        -nodes \
        -subj "/CN=SAML SP" \
        -x509 \
        -sha256 \
        -newkey rsa:3072 \
        -keyout "sp.key" \
        -out "sp.crt" \
        -days 3650

Copy the files:

    $ sudo mkdir /etc/httpd/saml
    $ sudo cp sp.crt sp.key /etc/httpd/saml

Fetch the IdP metadata from the IdP. For example, for SURFconext you would use 
the following:

    $ curl -o metadata.test.surfconext.nl.xml https://metadata.test.surfconext.nl/idp-metadata.xml
    $ curl -o metadata.surfconext.nl.xml https://metadata.surfconext.nl/idp-metadata.xml

Now copy the metadata as well:

    $ sudo cp metadata.test.surfconext.nl.xml metadata.surfconext.nl.xml /etc/httpd/saml

Modify the `/etc/httpd/conf.d/vpn.example.conf` file, and add the contents as
shown [here](#apache) inside the Apache configuration file in the right 
section.

Restart the web server:

    $ sudo systemctl restart httpd

Now when you visit `https://vpn.example/vpn-user-portal/` you should be 
redirected to the IdP. If this works, you probably need to register your SP
at your IdP. You can use the following URL with metadata:

    https://vpn.example/saml/metadata

You also need to modify the `vpn-user-portal` configuration to specify the 
attribute that should be used to identify the users.

Edit `/etc/vpn-user-portal/config.php` and set:
        
    'authMethod' => 'MellonAuthentication'

By default the `eduPersonTargetedId` attribute will be used to identify users.
You can change the `userIdAttribute` value under the `MellonAuthentication` 
section.

If you also want to use authorization based on an attribute, e.g. 
`eduPersonEntitlement` or `eduPersonAffiliation` you can set the 
`permissionAttribute` as well.

# Apache

## CentOS 

    <VirtualHost *:443>

        ...

        <Location />
            MellonEnable "info"
            MellonSecureCookie On
            MellonIdP "IDP"
            MellonMergeEnvVars On
            MellonSPPrivateKeyFile /etc/httpd/saml/sp.key
            MellonSPCertFile /etc/httpd/saml/sp.crt
            MellonSignatureMethod rsa-sha256
            MellonEndpointPath /saml
            # When using SURFconext as a WAYF, use this line
            #MellonIdPMetadataFile /etc/httpd/saml/metadata.test.surfconext.nl.xml
            MellonIdPMetadataFile /etc/httpd/saml/metadata.surfconext.nl.xml
            # When using a discovery service, use these two lines below 
            # MellonIdPMetadataFile /path/to/metadata.xml
            # MellonDiscoveryUrl "https://disco.example.org/"
        </Location>
        
        <Location /vpn-user-portal>
            MellonEnable "auth"
        </Location>
        
        # disable Mellon for the API
        <Location /vpn-user-portal/api.php>
            MellonEnable "off"
        </Location>
        # disable Mellon for the OAuth Token Endpoint
        <Location /vpn-user-portal/oauth.php>
            MellonEnable "off"
        </Location>
        # disable Mellon for the Node-API
        <Location /vpn-user-portal/node-api.php>
            MellonEnable "off"
        </Location>

        ...

    </VirtualHost>

## Debian

    <VirtualHost *:443>

        ...

        <Location />
            MellonEnable "info"
            MellonSecureCookie On
            MellonIdP "IDP"
            MellonMergeEnvVars On
            MellonSPPrivateKeyFile /etc/apache2/saml/sp.key
            MellonSPCertFile /etc/apache2/saml/sp.crt
            # Some IdPs only accept RSA-SHA256 signatures, but the version of
            # mod_auth_mellon in Debian 9 does not support this yet, you need
            # to use the backport, see: 
            # https://packages.debian.org/stretch-backports/libapache2-mod-auth-mellon 
            #MellonSignatureMethod rsa-sha256
            MellonEndpointPath /saml
            # When using SURFconext as a WAYF, use this line
            MellonIdPMetadataFile /etc/apache2/saml/metadata.test.surfconext.nl.xml
            #MellonIdPMetadataFile /etc/apache2/saml/metadata.surfconext.nl.xml
            # When using a discovery service, use these two lines below 
            # MellonIdPMetadataFile /path/to/metadata.xml
            # MellonDiscoveryUrl "https://disco.example.org/"
        </Location>

        <Location /vpn-user-portal>
            MellonEnable "auth"
        </Location>
        # disable Mellon for the API
        <Location /vpn-user-portal/api.php>
            MellonEnable "off"
        </Location>
        # disable Mellon for the OAuth Token Endpoint
        <Location /vpn-user-portal/oauth.php>
            MellonEnable "off"
        </Location>
        # disable Mellon for the Node-API
        <Location /vpn-user-portal/node-api.php>
            MellonEnable "off"
        </Location>

        ...

    </VirtualHost>
