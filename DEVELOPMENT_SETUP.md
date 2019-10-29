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

# Updating RPM Packages

The `${HOME}/Projects/LC-v2/rpm` folder has RPM package descriptions, "SPEC" 
files. These can be used to build RPM packages (on Fedora).

Assuming you are developing on component and want to create a new (test) 
package. Do the following:

1. Determine the last "commit" hash of the component you are building. E.g. 
   with `git log -1`;
2. Go to the `rpm` folder of the component, e.g. `rpm/vpn-user-portal`;
3. Make sure you are on the `master` branch: `git checkout master`;
4. "Bump" the SPEC file, e.g. `rpmdev-bumpspec SPECS/vpn-user-portal.spec`;
5. Put the hash in the top as `%global git <HASH>`;
6. Optionally update other parts of the SPEC file;
7. Run `local_build` in order to trigger a local build, to make sure the 
   package is correct and the unit tests properly run.

The `local_build` script looks like this:

    #!/bin/sh
    if [ -d SPECS ]
    then
        # we are in the package root
        spectool -g -R SPECS/*.spec
        cp SOURCES/* "${HOME}/rpmbuild/SOURCES"
        rpmbuild -bs SPECS/*.spec
        rpmbuild -bb SPECS/*.spec    
    elif [ -d ../SPECS ]
    then
        # we are in the SPECS directory already
        spectool -g -R ./*.spec
        cp ../SOURCES/* "${HOME}/rpmbuild/SOURCES"
        rpmbuild -bs ./*.spec
        rpmbuild -bb ./*.spec    
    else 
        echo "ERROR: cannot find SPEC file"
        exit 1
    fi

You can save it under `${HOME}/.local/bin/local_build`. Make sure it is 
executable: `chmod 0755 ${HOME}/.local/bin/local_build`. Run this from the 
package directory, e.g `rpm/vpn-user-portal`.

If you want to have your own builder, please set it up using the "builder" 
project, look [here](https://git.tuxed.net/rpm/builder/about/).

Commit the package changes to master, and run the builder. It should pick up 
your new spec file.

## Issues

* One has to setup their own builder
* There are multiple branches for the RPM packages depending on the version of
  the software, i.e. there is a `v2` and a `master` branch. We need to explain 
  that the `v2` branch is for production packages of LC/eduVPN 2.x.
* We still have to explain how to make a production release, i.e. explain 
  minisign, tags, etc.
