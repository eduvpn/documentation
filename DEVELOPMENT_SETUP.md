# Introduction

This document will describe how to set up an eduVPN development environment 
for easy development and running it on your development system. 

This is **NOT** meant to be used as installation instructions! See the 
[deploy](README.md#deployment) instructions instead!

We assume you will be using Fedora >= 26 for development work, but other 
distributions will of course also work, but some minor details, regarding 
installation of the required software, will be different.

See [DEVELOPMENT_PRACTICES](DEVELOPMENT_PRACTICES.md) for more information
about guidelines to follow.

# Preparation

Install the required software:

    $ sudo dnf -y install git composer php-phpunit-PHPUnit openvpn \
        php-libsodium

Some additional PHP extensions may be required, you will see `composer update` 
below complain about any missing PHP extensions. You can install them with 
`sudo dnf -y install php-EXT`.

# Getting the Modules

    $ mkdir -p ${HOME}/Projects/eduVPN
    $ cd ${HOME}/Projects/eduVPN
    $ git clone https://github.com/eduvpn/vpn-server-api.git
    $ git clone https://github.com/eduvpn/vpn-user-portal.git
    $ git clone https://github.com/eduvpn/vpn-admin-portal.git
    $ git clone https://github.com/eduvpn/vpn-server-node.git
    $ git clone https://github.com/eduvpn/vpn-lib-common.git

## vpn-server-api

    $ cd ${HOME}/Projects/eduVPN/vpn-server-api
    $ composer update
    $ mkdir config/default
    $ cp config/config.php.example config/default/config.php
    $ mkdir -p data/default
    $ php bin/init.php

## vpn-user-portal

    $ cd ${HOME}/Projects/eduVPN/vpn-user-portal
    $ composer update
    $ mkdir config/default
    $ cp config/config.php.example config/default/config.php
    $ mkdir -p data/default
    $ php bin/init.php
    $ php bin/add-user.php --user foo --pass bar

Modify `config/default/config.php` and disable `secureCookie` and 
`enableTemplateCache`.

Modify `apiUri` and set it to `http://localhost:8008/api.php`.

## vpn-admin-portal

    $ cd ${HOME}/Projects/eduVPN/vpn-admin-portal
    $ composer update
    $ mkdir config/default
    $ cp config/config.php.example config/default/config.php
    $ mkdir -p data/default
    $ php bin/add-user.php --user foo --pass bar

Modify `config/default/config.php` and disable `secureCookie` and 
`enableTemplateCache`.

Modify `apiUri` and set it to `http://localhost:8008/api.php`.

## vpn-server-node

    $ cd ${HOME}/Projects/eduVPN/vpn-server-node
    $ composer update
    $ mkdir config/default
    $ cp config/config.php.example config/default/config.php
    $ cp config/firewall.php.example config/firewall.php
    $ mkdir -p data/default
    $ mkdir openvpn-config

Modify `config/default/config.php` and set `apiUri` to 
`http://localhost:8008/api.php`.

# Testing

All projects have unit tests included, they can be run from the project folder,
e.g.: 

    $ cd ${HOME}/Projects/eduVPN/vpn-user-portal
    $ phpunit

# Using

Script to launch all services:

    #!/bin/sh
    cd ${HOME}/Projects/eduVPN
    (
	    cd vpn-server-api
	    VPN_INSTANCE_ID=default php -S localhost:8008 -t web &
    )

    (
	    cd vpn-user-portal
	    VPN_INSTANCE_ID=default php -S localhost:8082 -t web &
    )

    (
	    cd vpn-admin-portal
	    VPN_INSTANCE_ID=default php -S localhost:8083 -t web &
    )

Now with your browser you can connect to the user portal on 
`http://localhost:8082/` and to the admin portal on `http://localhost:8083/`.

# VPN Configuration

To generate the firewall and output the data to `stdout`:
    
    $ cd ${HOME}/Projects/eduVPN/vpn-server-node 
    $ php bin/generate-firewall.php

To generate the OpenVPN server configuration files:

    $ cd ${HOME}/Projects/eduVPN/vpn-server-node
    $ php bin/server-config.php --generate

The configuration will be stored in the `openvpn-config` folder.

# Developing

If you want to make changes to `vpn-lib-common`, which is a shared library 
used by all components you can modify it and push the changes. Using 
`composer update` you can retrieve the new version of `vpn-lib-common` in 
the projects. You may need to change `composer.json` and change the version
requirements to a (temporary) branch, e.g `master`. Change this:

    "eduvpn/common": "^1",

Into this:

    "eduvpn/common": "dev-master",

If you work in a fork of `eduvpn/common` you can update the URL referenced in
the `composer.json` before running `composer update`.

# Translations

[Twig](https://twig.symfony.com/) together with 
[gettext](https://secure.php.net/gettext) is used to take care of translations, 
see the 
[documentation](https://twig-extensions.readthedocs.io/en/latest/i18n.html) on
how to update the translation files.
