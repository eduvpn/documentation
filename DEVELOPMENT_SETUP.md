# Introduction

This document will describe how to set up an eduVPN development environment 
for easy development and running it on your development system. 

This is **NOT** meant to be used as installation instructions! See the 
[deploy](README.md#deployment) instructions instead!

We assume you will be using Fedora >= 28 for development work, but other 
distributions will of course also work, but some minor details, regarding 
installation of the required software, will be different.

See [DEVELOPMENT_PRACTICES](DEVELOPMENT_PRACTICES.md) for more information
about guidelines to follow.

# Preparation

Install the required software:

    $ sudo dnf -y install git composer phpunit7 openvpn \
        php-date php-filter php-gettext php-hash php-json php-mbstring \
        php-pcre php-pdo php-spl php-sodium php-pecl-radius php-ldap php-curl \
        php-gd

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
    $ php bin/server-config.php

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

# Making a Release

## Setup

We want to use `tar.xz` archives, and not `zip` or `tar.gz`, for this to work
we need to add a little snippet to `${HOME}/.gitconfig`:

    [tar "tar.xz"]
            command = xz -c

Now, with that out of the way, you can put the following POSIX shell script in
`${HOME}/.local/bin/make_release`. Make sure you make it "executable" with 
`chmod 0755 ${HOME}/.local/bin/make_release`:

    #!/bin/sh
    PROJECT_NAME=$(basename "${PWD}")
    PROJECT_VERSION=${1}

    if [ -z "${1}" ]
    then
        # we take the last "tag" of the Git repository as version
        PROJECT_VERSION=$(git describe --abbrev=0 --tags)
        echo Version: "${PROJECT_VERSION}"
    fi

    git archive --prefix "${PROJECT_NAME}-${PROJECT_VERSION}/" "${PROJECT_VERSION}" -o "${PROJECT_NAME}-${PROJECT_VERSION}.tar.xz"
    gpg2 --armor --detach-sign --yes "${PROJECT_NAME}-${PROJECT_VERSION}.tar.xz"

## Creating a Release

Now, from your checked out repository you can run `make_release` and it will 
create (by default) a signed archive of the last (annotated) tag of the 
project. If you want to create a release of a specific tag, provide it as the 
first argument to `make_release`:

    $ mkdir tmp && cd tmp
    $ git clone https://git.tuxed.net/fkooman/php-yubitwee
    $ cd php-yubitwee
    $ make_release
    Version: 1.1.4

The following files are created:

    $ ls -l php-yubitwee-*
    -rw-rw-r--. 1 fkooman fkooman 8240 Jun  8 17:18 php-yubitwee-1.1.4.tar.xz
    -rw-rw-r--. 1 fkooman fkooman  833 Jun  8 17:18 php-yubitwee-1.1.4.tar.xz.asc

You can verify the signature:

    $ gpg2 --verify php-yubitwee-1.1.4.tar.xz.asc
    gpg: assuming signed data in 'php-yubitwee-1.1.4.tar.xz'
    gpg: Signature made Fri 08 Jun 2018 05:18:37 PM CEST
    gpg:                using RSA key 6237BAF1418A907DAA98EAA79C5EDD645A571EB2
    gpg: Good signature from "François Kooman <fkooman@tuxed.net>" [ultimate]
