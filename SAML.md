---
title: SAML
description: Enable SAML Authentication
category: howto
---

This document describes how to configure SAML authentication for deployed
systems. We assume you used the `deploy_${DIST}.sh` script to deploy the 
software. Below we assume you use `vpn.example`, but modify this domain to your 
own domain name!

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

# Discovery

If you use only one IdP or a "hub & spoke" identity federation that provides 
their own WAYF service (the default), you don't need to do anything else. 

If you want to use your existing WAYF, you can integrate this directly if it 
supports the 
[Identity Provider Discovery Service Protocol and Profile](https://docs.oasis-open.org/security/saml/Post2.0/sstc-saml-idp-discovery.pdf).

If you don't yet have a WAYF and want to create one for the VPN service, you 
can use [php-saml-ds](https://git.tuxed.net/fkooman/php-saml-ds/) software, it
implements "Identity Provider Discovery Service Protocol and Profile", see 
below on how to configure this with `MellonIdPMetadataFile` and 
`MellonDiscoveryUrl`.

You need to have the metadata for all IdPs. For SURFconext you can use 
[this](https://metadata.surfconext.nl/idps-metadata.xml) URL. 
The URL mentioned above only contains the SURFconext "proxy" IdP information,
that does not contain enough information to create the WAYF.

You can install the software, it is also packaged for CentOS and Debian in the 
eduVPN repository:

    $ sudo yum -y install php-saml-ds

Or on Debian:

    $ sudo apt -y install php-saml-ds
    $ sudo a2enconf php-saml-ds 

Modify the configuration in `/etc/php-saml-ds/config.php` and make sure the 
IdP metadata file(s) are placed in `/etc/php-saml-ds/metadata/`. As entityID
of the SP you need to use `https://vpn.example/saml`. Specify the entityIDs
of the IdPs you want to show up in the WAYF in the configuration file under 
`idpList` as well.

Run the file generator:

    $ sudo php-saml-ds-generate

This should download the logos, if enabled, and create configuration files.

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
            # When using php-saml-ds, use these two lines below 
            # MellonIdPMetadataFile /var/lib/php-saml-ds/https_vpn.example_saml.xml
            # MellonDiscoveryUrl "https://vpn.example/php-saml-ds/index.php"
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
            # When using php-saml-ds, use these two lines below 
            # MellonIdPMetadataFile /var/lib/php-saml-ds/https_vpn.example_saml.xml
            # MellonDiscoveryUrl "https://vpn.example/php-saml-ds/index.php"
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

        ...

    </VirtualHost>
