---
title: OIDC
description: Enable OpenID Connect Authentication
category: howto
---

This document describes how to configure OpenID Connect (OIDC) authentication for deployed
systems. We assume you used the `deploy_${DIST}.sh` script to deploy the 
software. 

There is currently only one option for configuring OIDC for your VPN server:

1. [mod_auth_openidc](MOD_AUTH_OPENIDC.md)

See this module's [wiki](https://github.com/zmartzone/mod_auth_openidc/wiki) for information on how to install and configure this module.

In order to make a particular user an "administrator" in the portal, see 
[PORTAL_ADMIN](PORTAL_ADMIN.md).
