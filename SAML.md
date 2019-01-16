# Introduction

This document describes how to configure SAML authentication for deployed
systems. We assume you used the `deploy_${DIST}.sh` script to deploy the 
software. Below we assume you use `vpn.example`, but modify this domain to your 
own domain name!

## Configuration

Generate a TLS certificate for your SP:

    $ openssl req \
        -nodes \
        -subj "/CN=vpn.example" \
        -x509 \
        -sha256 \
        -newkey rsa:3072 \
        -keyout sp.key \
        -out sp.crt \
        -days 3600

Copy them to `/etc/vpn-user-portal`:

    $ sudo cp *.crt *.key /etc/vpn-user-portal

Fetch the IdP metadata from the IdP. For example, for SURFconext you would use 
the following:

    $ curl -o engine.test.surfconext.nl.xml https://engine.test.surfconext.nl/authentication/idp/metadata
    $ curl -o engine.surfconext.nl.xml https://engine.surfconext.nl/authentication/idp/metadata

Now copy the metadata to the right location as well:

    $ sudo cp engine.test.surfconext.nl.xml engine.surfconext.nl.xml /etc/vpn-user-portal

Edit `/etc/vpn-user-portal/config.php` and set:
        
    'authMethod' => 'SamlAuthentication'

By default the `eduPersonTargetedId` (`urn:oid:1.3.6.1.4.1.5923.1.1.1.10`) 
attribute will be used to uniquely identify the users. See the configuration
template below to set other supported options. Make sure to set the 
`idpEntityId` and `idpMetadata` parameters.

    // SAML
    'SamlAuthentication' => [
        // 'OID for eduPersonTargetedID
        'attribute' => 'urn:oid:1.3.6.1.4.1.5923.1.1.1.10',
        // OID for eduPersonPrincipalName
        //'attribute' => 'urn:oid:1.3.6.1.4.1.5923.1.1.1.6',

        // add the entityID of the IdP to the user ID. This MUST be enabled
        // if multiple IdPs are used *and* the attribute used for the user ID
        // is not enforced to be unique among the different IdPs
        'addEntityId' => false,

        // ** AUTHORIZATION | ENTITLEMENT **
        // OID for eduPersonEntitlement
        //'entitlementAttribute' => 'urn:oid:1.3.6.1.4.1.5923.1.1.1.7',
        // OID for eduPersonAffiliation
        //'entitlementAttribute' => 'urn:oid:1.3.6.1.4.1.5923.1.1.1.1',

        // override the SP entityId
        //'spEntityId' => 'https://vpn.example.org/saml',

        // set a fixed IdP for use with this service, it MUST be available in
        // the IdP metadata file
        'idpEntityId' => 'https://idp.example.org/saml',

        // set a URL that performs IdP discovery, all IdPs listed in the 
        // discovery service MUST also be available in the IdP metadata file
        //'discoUrl' => 'http://disco.example.org/index.php',

        // (Aggregate) SAML metadata file containing the IdP metadata of IdPs 
        // that are allowed to access this service
        'idpMetadata' => '/path/to/idp/metadata.xml',

        // Create a mapping between "entitlement values" and their required 
        // AuthnContext. Users getting a certain "entitlement" can have a 
        // "higher" LoA
        //'entitlementAuthnContextMapping' => [
        //    'urn:example:LC-admin' => ['urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport'],
        //],
    ],

**NOTE** if you want to allow access to the admin parts of the portal, you 
MUST also configure the entitlement authorization as shown in the configuration 
template above.

Now when you visit `https://vpn.example/vpn-user-portal/` you should be 
redirected to the IdP. If this works, you probably need to register your SP
at your IdP. You can use the following URL with metadata:

    https://vpn.example/vpn-user-portal/_saml/metadata

## Discovery

If you use only one IdP or a "hub & spoke" identity federation that provides 
their own WAYF service (the default), you don't need to do anything else. 

If you want to use your existing WAYF, you can integrate this directly if it 
supports the 
[Identity Provider Discovery Service Protocol and Profile](https://docs.oasis-open.org/security/saml/Post2.0/sstc-saml-idp-discovery.pdf).

If you don't yet have a WAYF and want to create one for the VPN service, you 
can use [php-saml-ds](https://git.tuxed.net/fkooman/php-saml-ds/) software, it
implements "Identity Provider Discovery Service Protocol and Profile", see 
below on how to configure this with `discoUrl`.

You need to have the metadata for all IdPs. For SURFconext you can use 
[this](https://engine.surfconext.nl/authentication/proxy/idps-metadata) URL. 
The URL mentioned previously only contains the SURFconext "proxy" IdP 
information, that does not contain enough information to create the WAYF.

You can install the software, it is also packaged for CentOS and Debian in the 
eduVPN repository:

    $ sudo yum -y install php-saml-ds

Or on Debian:

    $ sudo apt -y install php-saml-ds
    $ sudo a2enconf php-saml-ds 

Modify the configuration in `/etc/php-saml-ds/config.php` and make sure the 
IdP metadata file(s) are placed in `/etc/php-saml-ds/metadata/`. As entityID
of the SP you need to use `https://vpn.example/vpn-user-portal/_saml/metadata`. 
Specify the entityIDs of the IdPs you want to show up in the WAYF in the 
configuration file under `idpList` as well.

Run the file generator:

    $ sudo php-saml-ds-generate

This should download the logos, when enabled, and create configuration files.

Modify `/etc/vpn-user-portal/config.php` and set the following under the 
`SamlAuthentication`:

        'discoUrl' => 'https://vpn.example/php-saml-ds/index.php',
        'idpMetadata' => '/var/lib/php-saml-ds/https_vpn.example_saml.xml',

Restart Apache:

    $ sudo systemctl restart httpd

If you now browse to https://vpn.example/ you will get redirected to the WAYF 
and shown it. If there is only one IdP configured the WAYF will be skipped and
you'll directly end up at the IdP.

**NOTE**: if you want to add multiple IdPs that use identifiers that are not 
guaranteed globally unique, you MUST set `addEntityId` to `true` in 
`/etc/vpn-user-portal/config.php`.
