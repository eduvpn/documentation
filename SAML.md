---
title: SAML
description: Enable SAML Authentication
category: authentication
---

This document describes how to configure SAML authentication for deployed
systems. We assume you used the `deploy_${DIST}.sh` script to deploy the 
software. 

There are three, yeah I know, options for configuring SAML for your VPN server:

1. Shibboleth on [Debian](SHIBBOLETH_SP.md), [CentOS](SHIBBOLETH_SP_CENTOS.md)
2. [mod_auth_mellon](MOD_AUTH_MELLON.md)
3. [php-saml-sp](PHP_SAML_SP.md) (**NOT** supported!)

They are listed here in order of preference. Do **NOT** use php-saml-sp until 
it received a complete security audit.

In order to make a particular user an "administrator" in the portal, see 
[PORTAL_ADMIN](PORTAL_ADMIN.md).
