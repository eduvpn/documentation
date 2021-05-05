---
title: Shibboleth SP (CentOS)
description: SAML Authentication using Shibboleth on CentOS
category: authentication
---

This document describes installing Shibboleth on CentOS 7. On CentOS you have
to install Shibboleth V3 packages provided by the Shibboleth project.

To configure a repository for CentOS 7, you must create a file
in the `/etc/yum.repos.d/` directory, for example
`/etc/yum.repos.d/shibboleth.repo`, with the following content:

    [shibboleth]
    name=Shibboleth (CentOS_7)
    # Please report any problems to https://issues.shibboleth.net
    type=rpm-md
    mirrorlist=https://shibboleth.net/cgi-bin/mirrorlist.cgi/CentOS_7
    gpgcheck=1
    gpgkey=https://shibboleth.net/downloads/service-provider/RPMS/repomd.xml.key
    enabled=1

Install Shibboleth :

    $ sudo yum install shibboleth

Then configure the `shibd` daemon to run automatically at start-up:

    $ sudo systemctl enable shibd

## Certificates

The installation generates two certificates (more precisely: two key pairs /
certificates) for two different purposes:

1. Signing of SAML messages (`AuthnRequest`, `LogoutRequest`) sent to the IdP;
2. Used for encryption by the IdP

## Apache configuration

The installation of Shibboleth will install an Apache module name `mod_shib`,
this module has the ability to process both a variety of Apache commands
and rules specified in the SP configuration and make sense of both.

In `/etc/httpd/conf.d/shib.conf` add the following:

    <Location /vpn-user-portal>
        AuthType shibboleth
        ShibRequestSetting requireSession 1
        <RequireAll>
            Require shib-session
            #Require shib-attr entitlement "http://eduvpn.org/role/admin"
            #Require shib-attr unscoped-affiliation staff
        </RequireAll>
    </Location>

    # do not secure API endpoint
    <Location /vpn-user-portal/api.php>
        Require all granted
    </Location>

    # do not secure OAuth endpoint
    <Location /vpn-user-portal/oauth.php>
        Require all granted
    </Location> 

If you have a case where only one attribute needs to match, you can use 
`<RequireAny>` instead of `<RequireAll>`. You will also need to remove the 
`Require shib-session`.

The first location directive within Apache's configuration file specify
to the module to protect by Shibboleth the access to the VPN Portal.

Make sure you restart Apache after changing the configuration:

    $ sudo systemctl restart httpd

Then configure the Apache daemon to run automatically at start-up:

    $ sudo systemctl enable httpd

**NOTE** if you are using IDs such as `entitlement` and `unscoped-affiliation` 
make sure they are correctly enabled/set in 
`/etc/shibboleth/attribute-map.xml`.

## Shibboleth Configuration

Modify `/etc/shibboleth/shibboleth2.xml`:

* Set `entityID` to `https://vpn.example.org/shibboleth` in the
  `<ApplicationDefaults>` element.
* Set `handlerSSL` to `true` and `cookieProps` to `https` in the `<Sessions>`
  element
* Add in the `Sessions` element `handlerURL=”/Shibboleth.sso”`
* Set the `entityID` to the entity ID of your IdP, or configure the
  `discoveryURL` in the `<SSO>` element
* Remove `SAML1` from the `<SSO>` attribute content as we no longer need SAML
  1.0 support
* Set the `path` in the `<MetadataProvider>` element for 
  a simple static metadata file, e.g.: 
  `<MetadataProvider type="XML" validate="false" path="idp.tuxed.net.xml"/>` and 
  put the `idp.tuxed.net.xml` file in `/etc/shibboleth`. Set `validate` to 
  `false` to keep the IdP working in case it has `validUntil` specified in the
  XML


Configuring automatic metadata refresh is outside the scope of this document,
refer to your identity federation documentation.

Example:

    <SPConfig ...>
      ...
      <ApplicationDefaults entityID=" https://vpn.example.org/shibboleth"
        REMOTE_USER="eppn persistent-id targeted-id"
        cipherSuites="HIGH:!MD5:!RC4:!aNULL">

        <!-- Le paramètre handlerURL n'est pas présent par défaut -->
        <Sessions lifetime="28800" timeout="3600" checkAddress="false" relayState="ss:mem"
          handlerSSL="true"
          consistentAddress="true"
          cookieProps="https"
          handlerURL="/Shibboleth.sso" >

          <SSO discoveryProtocol="SAMLDS" discoveryURL="https://myDiscovery example.org">
              SAML2
          </SSO>
          ...
          <!-- Extension service that generates "approximate" metadata based on SP configuration. -->
          <Handler type="MetadataGenerator" Location="/Metadata" signing="false"/>

          <!-- Status reporting service. -->
          <Handler type="Status" Location="/Status" acl="127.0.0.1 ::1 193.49.159.128/26 194.57.5.33"/>
        </Sessions>
        ...
        <Errors supportContact="root@localhost"
          metadata="metadataError_fr.html"
          access="accessError_fr.html"
          ssl="sslError_fr.html"
          localLogout="localLogout_fr.html"
          globalLogout="globalLogout_fr.html"
          helpLocation="/about.html"
          styleSheet="/shibboleth-sp/main.css"/>

        <!-- Meta-données de votre IDP -->
        <MetadataProvider type="XML"
          url="https://url-my-federation.example.org"
          backingFilePath=" url-my-federation.example.org.xml" reloadInterval="7200">
        </MetadataProvider>
        ...
        <!-- Simple file-based resolvers for separate signing/encryption keys. -->
        <CredentialResolver type="File" use="signing"
            key="sp-signing-key.pem" certificate="sp-signing-cert.pem"/>
        <CredentialResolver type="File" use="encryption"
            key="sp-encrypt-key.pem" certificate="sp-encrypt-cert.pem"/>
      </ApplicationDefaults>
      ...
    </SPConfig>

Verify the Shibboleth configuration:

    $ sudo shibd -t
    overall configuration is loadable, check console for non-fatal problems

Restart Shibboleth:

    $ sudo systemctl restart shibd

Next: register your SP in your identity federation, or in your IdP. The
metadata URL is typically `https://vpn.example.org/Shibboleth.sso/Metadata`.

### Portal

In order to configure the VPN portal, modify `/etc/vpn-user-portal/config.php`
and set the `authMethod` and `ShibAuthentication` options:

    ...

    'authMethod' => 'ShibAuthentication',

    ...

    'ShibAuthentication' => [
        'userIdAttribute' => 'persistent-id',
        'permissionAttribute' => 'entitlement',
    ],

    ...

The mentioned attributes `persistent-id` and `entitlement` are configured in
the Shibboleth configuration. Modify/add others as required in
`/etc/shibboleth/attribute-map.xml`. Do not forget to restart Shibboleth if
you make any changes to its configuration.
