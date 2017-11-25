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
        php-date php-filter php-gettext php-hash php-json php-mbstring \
        php-pcre php-pdo php-spl php-libsodium php-ldap php-curl php-gd

Download the `development_setup.sh` script from this repository and run it. It
will by default create a directory `${HOME}/Project/eduVPN` under which 
everything will be installed. No `root` is required!

    $ curl -L -O https://raw.githubusercontent.com/eduvpn/documentation/master/development_setup.sh
    $ sh ./development_setup.sh

# Testing

All projects have unit tests included, they can be run from the project folder,
e.g.: 

    $ cd ${HOME}/Projects/eduVPN/vpn-user-portal
    $ phpunit

# Using

A "launch" script is included to run the PHP built-in web server to be able
to easily test the portals.

    $ cd ${HOME}/Projects/eduVPN
    $ sh ./launch.sh

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
