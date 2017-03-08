# Release

This document describes how to create an RPM repository containing all the 
software built from scratch and signed with PGP. This will perform a FULL 
build.

# Preparation

We assume you have a fresh CentOS 7 machine, add the following software to it. 

    $ sudo yum -y install epel-release
    $ sudo yum -y install fedora-packager docker

Enable and start Docker:

    $ sudo systemctl enable docker
    $ sudo systemctl start docker

Clone the `eduVPN/specs` and `eduVPN/documentation` repository:

    $ git clone https://github.com/eduVPN/specs.git
    $ git clone https://github.com/eduVPN/documentation.git

# Creating SRPMs

First we need to generate the SRPMs files for the software.

    $ cd $HOME
    $ rpmdev-setuptree
    $ cd $HOME/specs

Copy the auxilary files to `$HOME/rpmbuild/SOURCES`:

    $ cp *.conf *.cron *.patch $HOME/rpmbuild/SOURCES

Download all the sources for the spec files to `$HOME/rpmbuild/SOURCES`, this
will download tarballs from GitHub with the right filename:

    $ for i in $(ls *.spec); do spectool -g -R $i; done

Create all the SRPMs:

    $ for i in $(ls *.spec); do rpmbuild -bs $i; done

Alright, that should be enough to launch our Docker builder!

# Setting up Docker

The `eduVPN/documentation` repository contains a `Dockerfile` for building
RPMs.

    $ cd $HOME/documentation/docker

Create the Docker builder image:

    $ sudo docker build -t eduvpn/builder .

Now we can use this Docker image to build the RPM files. The reason we do this
in this way is that we have a "clean" environment for every package build.

Every package that gets built will be added to the repository available to the
Docker image. This way, all dependencies get pulled in and we can find out if
there are any problems in the build, e.g. missing dependencies.

    $ export PKGS=(php-bacon-bacon-qr-code php-christian-riesen-base32 php-christian-riesen-otp php-paragonie-constant-time-encoding php-fkooman-oauth2-client php-fkooman-oauth2-server php-fkooman-yubitwee vpn-lib-common vpn-admin-portal vpn-server-api vpn-server-node vpn-user-portal)
    $ for i in "${PKGS[@]}"; do sudo docker run --rm -v $HOME/rpmbuild:/in:Z -v $HOME/rpmbuild:/out:Z -i -t eduvpn/builder /build.sh SRPMS/$(basename $(ls $HOME/rpmbuild/SRPMS/$i*.src.rpm)); done

This should build all the packages and also have a fully functional YUM 
repository!

# Signing Packages

TBD.
