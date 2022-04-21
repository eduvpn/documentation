---
title: SAML
description: Enable SAML Authentication
category: authentication
---

This document describes how to configure SAML authentication for deployed
systems. We assume you used the `deploy_${DIST}.sh` script to deploy the 
software. 

There are three, yeah I know, options for configuring SAML for your VPN server:

1. [Shibboleth](SHIBBOLETH_SP.md)
2. [php-saml-sp](PHP_SAML_SP.md)
3. [mod_auth_mellon](MOD_AUTH_MELLON.md) (*NOT RECOMMENDED*)

They are listed here in order of preference.

In order to make a particular user an "administrator" in the portal, see 
[PORTAL_ADMIN](PORTAL_ADMIN.md).
