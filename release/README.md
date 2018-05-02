# Release

This document describes how to create an RPM repository containing all the 
software built from scratch and signed with PGP. This will perform a FULL 
build of all packages.

Currently it will build for the following platforms:

* CentOS / Red Hat Enterprise Linux 7
* Fedora 28

# Preparation

We assume you have a fresh install of Fedora >= 27 with the following software 
installed:

## Fedora

    $ sudo dnf -y install fedora-packager rpm-sign nosync dnf-utils

## Mock

Make sure your current user account is a member of the `mock` group:

    $ sudo usermod -a -G mock $(id -un)

After this, make sure you logout and in again.

Create a Mock configuration file in `${HOME}/.config/mock.cfg`:

    # Speed up package installation in Mock
    config_opts['nosync'] = True

## GPG

Make sure you have a PGP key available. If not, create one:

    $ gpg2 --gen-key

Add the following to `${HOME}/.rpmmacros`, assuming the email address you used 
is `eduvpn@surfnet.nl`:

    %_signature gpg
    %_gpg_name software@letsconnect-vpn.org
    %_gpg_digest_algo sha256

To export the public key, for use by clients using this repository:

    $ gpg2 --export -a 'software@letsconnect-vpn.org' > RPM-GPG-KEY-LC

## Repository

Clone the `eduVPN/documentation` repository:

    $ git clone https://github.com/eduVPN/documentation.git

# Building

    $ cd documentation
    $ sh release/build_all.sh

This will put all RPMs and source RPMs in the `${HOME}/repo` directory and 
create a tarball in `${HOME}` as well with the name `rpmRepo-<DATE>.tar.gz`. 
This file will contain all files from `${HOME}/repo`. If you run the release
script multiple times, e.g. run it again after a package update, the new RPM 
and source RPM will be added to the `${HOME}/repo` directory and the tarball
as well. A history of old packages is retained, so it is beneficial to retain
the `${HOME}/repo` folder between builds. This way you can downgrade to an 
earlier version of a package if needed, e.g.:

    $ sudo yum downgrade php-fkooman-oauth2-client

# Updating

If you want to create packages of updated software, just pull the last version
of the repository:

    $ git pull

And then, run the `build_all.sh` script again:

    $ cd documentation
    $ sh release/build_all.sh

This should put any new packages in `${HOME}/repo` as well as put them in the 
generated tarball.

# Configuration

Create the following snippet in `/etc/yum.repos.d/LC.repo` on the machine where 
you want to install Let's Connect. Make sure the files can be found on the URLs 
mentioned below:

## CentOS / Red Hat Enterprise Linux >= 7

    [LC]
    name=Let's Connect Packages (EL $releasever)
    baseurl=https://repo.letsconnect-vpn.org/rpm/release/enterprise/$releasever/$basearch
    gpgcheck=1
    enabled=1
    gpgkey=https://repo.letsconnect-vpn.org/rpm/release/RPM-GPG-KEY-LC
    skip_if_unavailable=False

## Fedora >= 28

    [LC]
    name=Let's Connect Packages (Fedora $releasever) 
    baseurl=https://repo.letsconnect-vpn.org/rpm/release/fedora/$releasever/$basearch
    gpgcheck=1
    enabled=1
    gpgkey=https://repo.letsconnect-vpn.org/rpm/release/RPM-GPG-KEY-LC
    skip_if_unavailable=False
