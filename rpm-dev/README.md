# RPM 

This repository contains all RPM spec files for software that is not part 
of Fedora/EPEL, including dependencies and the VPN software itself.

If you want to build eduVPN from source for deploying it and not for 
development, you can check [this](../release/README.md) document.

The repository contains two additional scripts:

* `local_build.sh` to build the package locally;
* `copr_build.sh` to build the package remotely (in COPR);

The resulting packages are available in the COPR repository at 
[https://copr.fedorainfracloud.org/coprs/fkooman/lc-dev/](https://copr.fedorainfracloud.org/coprs/fkooman/lc-dev/).

# Requirements

    $ sudo yum -y install epel-release
    $ sudo yum -y install fedora-packager
    $ rpmdev-setuptree

# Building

**NOTE**: Some of the packages will depend on other packages available in EPEL, 
or on packages in this repository, so you need to install (and build) those 
first.

    $ ./local_build.sh php-fkooman-oauth2-server

## Remote Building

Same rules apply.

    $ ./copr_build.sh php-fkooman-oauth2-server
