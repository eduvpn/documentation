---
title: Development Setup
description: Setup a Developer Environment
category: dev
---

This document will describe how to set up an Let's Connect! / eduVPN 
development environment for easy development and running it on your development 
system. 

This is **NOT** meant to be used as installation instructions! See the 
[deploy](README.md#deployment) instructions instead!

We assume you will be using Fedora >= 30 for development work, but other 
distributions may also work, but some minor details, regarding installation of 
the required software, will be different.

See [DEVELOPMENT_PRACTICES](DEVELOPMENT_PRACTICES.md) for more information
about guidelines to follow.

# Preparation

Install the required software:

    $ sudo dnf -y install git composer phpunit8 openvpn \
        php-date php-filter php-hash php-json php-mbstring php-pcre php-pdo \
        php-spl php-sodium php-pecl-radius php-ldap php-curl php-gd

Download the `development_setup.sh` script from this repository and run it. It
will by default create a directory `${HOME}/Project/LC-master` under which 
everything will be installed. No `root` is required!

    $ curl -L -O https://raw.githubusercontent.com/eduvpn/documentation/master/development_setup.sh
    $ sh ./development_setup.sh

# Testing

The projects have unit tests included, they can be run from the project folder,
e.g.: 

    $ cd ${HOME}/Projects/LC-master/vpn-user-portal
    $ phpunit8

    $ cd ${HOME}/Projects/LC-master/vpn-server-node
    $ phpunit8

# Using

A "launch" script is included to run the PHP built-in web server to be able
to easily test the portals.

    $ cd ${HOME}/Projects/LC-master
    $ sh ./launch.sh

Now with your browser you can connect to the user portal on 
`http://localhost:8082/`.

You can login with the users `foo` and password `bar` or `admin` with password 
`secret`.

# VPN Configuration

To generate the OpenVPN server configuration files:

    $ cd ${HOME}/Projects/LC-master/vpn-server-node
    $ php bin/server-config.php

The configuration will be stored in the `openvpn-config` folder.
