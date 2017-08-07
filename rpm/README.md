# RPM 

This repository contains all RPM spec files for software that is not part 
of Fedora/EPEL, including dependencies and the VPN software itself.

The repository contains two additional scripts:

* `local_build.sh` to build the package locally;
* `copr_build.sh` to build the package remotely (in COPR);

The resulting packages are available in the COPR repository at 
[https://copr.fedorainfracloud.org/coprs/fkooman/eduvpn-testing/](https://copr.fedorainfracloud.org/coprs/fkooman/eduvpn-testing/).

# Requirements

    $ sudo yum -y install epel-release
    $ sudo yum -y install fedora-packager
    $ rpmdev-setuptree

# Building

**NOTE**: Some of the packages will depend on other packages available in EPEL, 
or on packages in this repository, so you need to install (and build) those 
first.

    $ ./local_build.sh php-fkooman-oauth2-client

## Remote Building

Same rules apply.

    $ ./copr_build.sh php-fkooman-oauth2-client
