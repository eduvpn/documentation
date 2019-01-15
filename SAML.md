# Introduction

This document describes how to configure SAML authentication for deployed
systems. We assume you used the `deploy_${DIST}.sh` script to deploy the 
software. Below we assume you use `vpn.example`, but modify this domain to your 
own domain name!

## Installation

### CentOS 

First install `mod_auth_mellon`:

    $ sudo yum -y install mod_auth_mellon

### Debian

    $ sudo apt -y install libapache2-mod-auth-mellon

In the examples below you will not use `/etc/httpd` but `/etc/apache2` as the
base path, and for `systemctl` you use `apache2` instead of `httpd`.

## Configuration

Generate a TLS certificate for your SP:

    $ openssl req \
        -nodes \
        -subj "/CN=vpn.example" \
        -x509 \
        -sha256 \
        -newkey rsa:3072 \
        -keyout vpn.example.key \
        -out vpn.example.crt \
        -days 3600

Copy them to `/etc/httpd/saml`:

    $ sudo mkdir /etc/httpd/saml
    $ sudo cp *.crt *.key /etc/httpd/saml

Fetch the IdP metadata from the IdP. For example, for SURFconext you would use 
the following:

    $ curl -o engine.test.surfconext.nl.xml https://engine.test.surfconext.nl/authentication/idp/metadata
    $ curl -o engine.surfconext.nl.xml https://engine.surfconext.nl/authentication/idp/metadata

Now copy the metadata to the right location as well:

    $ sudo cp engine.test.surfconext.nl.xml engine.surfconext.nl.xml /etc/httpd/saml

Modify your `/etc/httpd/conf.d/vpn.example.conf`, and enable the SAML lines 
there. Make sure you modify the lines that refer to certificates and keys.

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

By default the NAME_ID will be used to identify the users, if you want to 
change that change the `attribute` value under `MellonAuthentication`.

**NOTE** if you want to allow access to the admin parts of the portal, you 
MUST also configure the entitlement authorization. 

For example:

    'MellonAuthentication' => [
        // eduPersonTargetedId
        'attribute' => 'MELLON_urn:oid:1_3_6_1_4_1_5923_1_1_1_10',
        'addEntityID' => false,

        // eduPersonEntitlement
        'entitlementAttribute' => 'MELLON_urn:oid:1_3_6_1_4_1_5923_1_1_1_7',
        'entitlementAuthorization' => [
            'https://idp.example.com/saml|urn:example:LC-admin',
        ],
    ],

Also see the example configuration file in 
`/usr/share/doc/vpn-user-portal-VERSION/config.php.example`.

## Discovery

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
[this](https://engine.surfconext.nl/authentication/proxy/idps-metadata) URL. 
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

**NOTE**: if you want to add multiple IdPs that use identifiers that are not 
guaranteed globally unique, you MUST set `addEntityID` to `true` in 
`/etc/vpn-user-portal/config.php`.
