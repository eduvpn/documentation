Below we assume you use `vpn.example`, but modify this domain to your own 
domain name!

This document describes how to use/configure 
[mod_auth_mellon](https://github.com/latchset/mod_auth_mellon).

# Installation

## Fedora / Enterprise Linux

First install `mod_auth_mellon`:

    $ sudo dnf -y install mod_auth_mellon

## Debian  / Ubuntu

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

    'authModule' => 'MellonAuthModule',

You MUST set the `userIdAttribute` value under the `MellonAuthModule` section.

If you also want to use authorization based on an attribute, e.g. 
`eduPersonEntitlement` or `eduPersonAffiliation` you can set the 
`permissionAttributeList` as well.

## Examples

Using `uid`:

```php
'MellonAuthModule' => [
    // uid
    'userIdAttribute' => 'MELLON_urn:oid:0_9_2342_19200300_100_1_1',
    // eduPersonAffiliation
    'permissionAttributeList' => ['MELLON_urn:oid:1_3_6_1_4_1_5923_1_1_1_1']
],
```

Using 
[Pairwise Subject Identifier](https://docs.oasis-open.org/security/saml-subject-id-attr/v1.0/cs01/saml-subject-id-attr-v1.0-cs01.html#_Toc536097230):

```php
'MellonAuthModule' => [
    'userIdAttribute' => 'MELLON_urn:oasis:names:tc:SAML:attribute:pairwise-id',
],
```

If you want to use `eduPersonTargetedId`, which is not really recommended, 
use _pairwise-id_ instead, you can configure it like this:

```php
'MellonAuthModule' => [
    // eduPersonTargetedId
    'userIdAttribute' => 'MELLON_urn:oid:1_3_6_1_4_1_5923_1_1_1_10',
    'nameIdSerialization' => true,
    'spEntityId' => 'https://vpn.example/saml/metadata',
],
```

This will _serialize_ the XML node to a string using the IdP and SP entity ID
together with the eduPersonTargetedId _value_. If you are using the "Name ID", 
very much not recommended, you can set `userIdAttribute` to `MELLON_NAME_ID`.

# Apache

## Fedora / Enterprise Linux

    <VirtualHost *:443>

        ...

        <Location />
            MellonEnable "info"
            MellonSecureCookie On
            MellonIdP "IDP"
            MellonMergeEnvVars On
            # Override the SP's entityID if needed, by default it is 
            # https://vpn.example/saml/metadata
            #MellonSPentityId https://vpn.example/saml
            MellonSPPrivateKeyFile /etc/httpd/saml/sp.key
            MellonSPCertFile /etc/httpd/saml/sp.crt
            MellonSignatureMethod rsa-sha256
            MellonEndpointPath /saml
            # When using SURFconext as a WAYF, use this line
            #MellonIdPMetadataFile /etc/httpd/saml/metadata.test.surfconext.nl.xml
            MellonIdPMetadataFile /etc/httpd/saml/metadata.surfconext.nl.xml
            # When using a discovery service, use these two lines below 
            #MellonIdPMetadataFile /path/to/metadata.xml
            #MellonDiscoveryUrl "https://disco.example.org/"
        </Location>
        
        <Location /vpn-user-portal>
            MellonEnable "auth"
        </Location>
        
    	# do not restrict API Endpoint as used by VPN clients
        <Location /vpn-user-portal/api>
            MellonEnable "off"
        </Location>
		
        # do not secure OAuth Token Endpoint as used by VPN clients
        <Location /vpn-user-portal/oauth/token>
            MellonEnable "off"
        </Location>
		
	    # If you run separete node(s) you MUST allow access to "node-api.php" 
	    # withouh protecting it with Mellon
	    #<Location /vpn-user-portal/node-api.php>
        #    MellonEnable "off"
        #</Location>

        ...

    </VirtualHost>

## Debian / Ubuntu

    <VirtualHost *:443>

        ...

        <Location />
            MellonEnable "info"
            MellonSecureCookie On
            MellonIdP "IDP"
            MellonMergeEnvVars On
            # Override the SP's entityID if needed, by default it is 
            # https://vpn.example/saml/metadata
            #MellonSPentityId https://vpn.example/saml
            MellonSPPrivateKeyFile /etc/apache2/saml/sp.key
            MellonSPCertFile /etc/apache2/saml/sp.crt
            MellonSignatureMethod rsa-sha256
            MellonEndpointPath /saml
            # When using SURFconext as a WAYF, use this line
            MellonIdPMetadataFile /etc/apache2/saml/metadata.test.surfconext.nl.xml
            #MellonIdPMetadataFile /etc/apache2/saml/metadata.surfconext.nl.xml
            # When using a discovery service, use these two lines below 
            #MellonIdPMetadataFile /path/to/metadata.xml
            #MellonDiscoveryUrl "https://disco.example.org/"
        </Location>

        <Location /vpn-user-portal>
            MellonEnable "auth"
        </Location>
        
    	# do not restrict API Endpoint as used by VPN clients
        <Location /vpn-user-portal/api>
            MellonEnable "off"
        </Location>
		
        # do not secure OAuth Token Endpoint as used by VPN clients
        <Location /vpn-user-portal/oauth/token>
            MellonEnable "off"
        </Location>
		
	    # If you run separete node(s) you MUST allow access to "node-api.php" 
	    # withouh protecting it with Mellon
	    #<Location /vpn-user-portal/node-api.php>
        #    MellonEnable "off"
        #</Location>


        ...

    </VirtualHost>
