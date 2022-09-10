This document describes installing Shibboleth on Debian 11.

# Installation

## Debian 11

```
$ sudo apt install libapache2-mod-shib
$ sudo shib-keygen -n sp-encrypt
$ sudo shib-keygen -n sp-signing
```

# Configuration

Modify `/etc/shibboleth/shibboleth2.xml`:

* Set entityID to `https://vpn.example.org/shibboleth` in the
  `<ApplicationDefaults>` element.
* Set `handlerSSL` to `true` and `cookieProps` to `https` in the `<Sessions>`
  element
* Set the `entityID` to the entity ID of your IdP, or configure the
  `discoveryURL` in the `<SSO>` element
* Set the `path` in the `<MetadataProvider>` element for a simple static 
  metadata file, e.g.: 
  `<MetadataProvider type="XML" validate="false" path="idp.tuxed.net.xml"/>` and 
  put the `idp.tuxed.net.xml` file in `/etc/shibboleth`. Set `validate` to 
  `false` to keep the IdP working in case it has `validUntil` specified in the
  XML

Configuring automatic metadata refresh is outside the scope of this document,
refer to your identity federation documentation.

Verify the Shibboleth configuration:

```
$ sudo shibd -t
overall configuration is loadable, check console for non-fatal problems
```

Restart Shibboleth:

```
$ sudo systemctl restart shibd
```

Next: register your SP in your identity federation, or in your IdP. The
metadata URL is typically `https://vpn.example.org/Shibboleth.sso/Metadata`.

### Apache

In `/etc/apache2/sites-available/vpn.example.org.conf` add the following:

```
<VirtualHost *:443>

    ...

    <Location /vpn-user-portal>
        AuthType shibboleth
        ShibRequestSetting requireSession 1
        <RequireAll>
            Require shib-session
            #Require shib-attr entitlement "http://eduvpn.org/role/admin"
            #Require shib-attr unscoped-affiliation staff
        </RequireAll>
    </Location>

    # do not restrict API Endpoint as used by VPN clients
    <Location /vpn-user-portal/api>
        Require all granted
    </Location>

    # do not secure OAuth Token Endpoint as used by VPN clients
    <Location /vpn-user-portal/oauth/token>
        Require all granted
    </Location> 

	# If you run separete node(s) you MUST allow access to "node-api.php" 
	# withouh protecting it with Shibboleth
	#<Location /vpn-user-portal/node-api.php>
	#    Require all granted
	#</Location>

    ...

    </VirtualHost>
```

If you have a case where only one attribute needs to match, you can use 
`<RequireAny>`instead of `<RequireAll>`. You will also need to remove the 
`Require shib-session`. 

Make sure you restart Apache after changing the configuration:

```
$ sudo systemctl restart apache2
```

**NOTE** if you are using IDs such as `entitlement` and `unscoped-affiliation` 
make sure they are correctly enabled/set in 
`/etc/shibboleth/attribute-map.xml`.

### Portal

In order to configure the VPN portal, modify `/etc/vpn-user-portal/config.php`
and set the `authModule` and `ShibAuthModule` options:

```
'authModule' => 'ShibAuthModule',

'ShibAuthModule' => [
    'userIdAttribute' => 'uid',
    'permissionAttributeList' => ['entitlement'],
],
```

The mentioned attributes `persistent-id` and `entitlement` are configured in
the Shibboleth configuration. Modify/add others as required in
`/etc/shibboleth/attribute-map.xml`. Do not forget to restart Shibboleth if
you make any changes to its configuration.
