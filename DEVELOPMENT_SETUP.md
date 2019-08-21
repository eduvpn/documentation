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

We assume you will be using either macOS >= 10.14 (Mojave) or Fedora >= 30 for 
development work, but other distributions will of course also work, but some 
minor details, regarding installation of the required software, will be 
different.

See [DEVELOPMENT_PRACTICES](DEVELOPMENT_PRACTICES.md) for more information
about guidelines to follow.

# Fedora

Install the required software (dependencies):

    $ sudo dnf -y install golang php-cli git composer php-date php-filter \
        php-hash php-json php-mbstring php-pcre php-pdo php-spl php-sodium \
        php-curl php-gd

# macOS

We assume a clean macOS 10.14 (Mojave) installation. There is no need to install 
[MacPorts](https://www.macports.org/) or [Homebrew](https://brew.sh/), we 
explain how to get going without using them, but feel free to use them, for 
example to install Composer.

1. install Xcode command line tools, if not already done
2. install [Go](https://golang.org/dl/)
3. install [Composer](https://getcomposer.org/download/)

The easiest way to install the command line tools is simply open the terminal 
on macOS and type `xcode-select --install`. This will ask if you want to 
install the tools. Agree to it.

Make sure you install the Go package for "Apple macOS", e.g. 
`go1.12.9.darwin-amd64.pkg`.

As for Composer, what I did is download the "Latest Snapshot" at the bottom 
of the page, make sure it is downloaded to your "Downloads" folder, otherwise
change the command below, then:

    $ mkdir -p ${HOME}/.local/bin
    $ cp ${HOME}/Downloads/composer.phar ${HOME}/.local/bin/composer
    $ chmod +x ${HOME}/.local/bin/composer
    $ echo 'export PATH=${PATH}:${HOME}/.local/bin' >> ~/.bash_profile

Then restart the terminal and you should be good to go!

# Installation

Download the `development_setup.sh` script from this repository and run it. It
will by default create a directory `${HOME}/Project/LC-v2` under which 
everything will be installed. No `root` is required!

    $ curl -L -O https://raw.githubusercontent.com/eduvpn/documentation/v2/development_setup.sh
    $ sh ./development_setup.sh

# Testing

All projects have unit tests included, they can be run from the project folder,
e.g.: 

    $ cd ${HOME}/Projects/LC-v2/vpn-user-portal
    $ vendor/bin/phpunit

# Using

A "launch" script is included to run the PHP built-in web server to be able
to easily test the portals.

    $ cd ${HOME}/Projects/LC-v2
    $ sh ./launch.sh

Now with your browser you can connect to the user portal on 
`http://localhost:8082/`.

You can login with the users `foo` and password `bar` or `admin` with password 
`secret`.

# VPN Configuration

To generate the firewall and output the data to `stdout`:
    
    $ cd ${HOME}/Projects/LC-v2/vpn-server-node 
    $ php bin/generate-firewall.php

To generate the OpenVPN server configuration files:

    $ cd ${HOME}/Projects/LC-v2/vpn-server-node
    $ php bin/server-config.php

The configuration will be stored in the `openvpn-config` folder.
