# Release

This document describes how to create an RPM repository containing all the 
software built from scratch and signed with PGP. This will perform a FULL 
build.

# Preparation

We assume you have a fresh Fedora or CentOS 7 machine, add the following 
software to it:

## CentOS

    $ sudo yum -y install epel-release # only on CentOS
    $ sudo yum -y install fedora-packager rpm-sign nosync

## Fedora

    $ sudo dnf -y install fedora-packager rpm-sign nosync

## Mock

Make sure your current user account is a member of the `mock` group:

    $ sudo usermod -a -G mock myusername

After this, make sure you logout and in again.

Create a Mock configuration file in `${HOME}/.config/mock.cfg`:

    # Speed up package installation in Mock
    config_opts['nosync'] = True

## GPG

Make sure you have a PGP key available. If not, create one. On CentOS:

    $ gpg --gen-key

On Fedora you would use `gpg2`:

    $ gpg2 --gen-key

Add the following to `${HOME}/.rpmmacros`, assuming the email address you used 
is `eduvpn@surfnet.nl`:

    %_signature gpg
    %_gpg_name eduvpn@surfnet.nl
    %_gpg_digest_algo sha256

To export the public key, for use by clients using this repository:

    $ gpg --export -a 'eduvpn@surfnet.nl' > RPM-GPG-KEY-eduVPN

Or on Fedora:

    $ gpg2 --export -a 'eduvpn@surfnet.nl' > RPM-GPG-KEY-eduVPN

## Repository

Clone the `eduVPN/documentation` repository:

    $ git clone https://github.com/eduVPN/documentation.git

# Building

    $ cd documentation
    $ sh release/build.sh

This will put all RPMs and source RPMs in the `${HOME}/repo` directory and 
create a tarball in `${HOME}` as well with the name `rpmRepo-<DATE>.tar.gz`. 
This file will contain all files from `${HOME}/repo`. If you run the release
script multiple times, e.g. run it again after a package update, the new RPM 
and source RPM will be added to the `${HOME}/repo` directory and the tarball
as well. A history of old packages is retained. This way you can rollback to 
an earlier version of a package, e.g.:

    $ sudo yum rollback php-fkooman-oauth2-client

# Configuration

Create the following snippet in `/etc/yum.repos.d/eduVPN.repo` on the machine
where you want to install eduVPN. Make sure the files can be found on the URLs
mentioned below:

    [eduVPN]
    name=eduVPN
    baseurl=https://static.eduvpn.nl/rpm/
    gpgcheck=1
    enabled=1
    gpgkey=https://static.eduvpn.nl/rpm/RPM-GPG-KEY-eduVPN
    skip_if_unavailable=False
	
# Sources

* https://blog.packagecloud.io/eng/2014/11/24/howto-gpg-sign-verify-rpm-packages-yum-repositories/

