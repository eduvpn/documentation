# Release

This document describes how to create an RPM repository containing all the 
software built from scratch and signed with PGP. This will perform a FULL 
build of all packages.

Currently it will build packages for the following platforms on those same
platforms:

* CentOS / Red Hat Enterprise Linux 7
* Fedora `${LATEST}`

This means, if you want to build CentOS 7 packages, you MUST run on CentOS 7. 
If you want to build Fedora packages, you MUST run on Fedora.

Typically you'd want to use VMs for this.

# Preparation

## CentOS

We assume you have a fresh install of CentOS 7 with the following software 
installed:

    $ sudo yum -y install epel-release
    $ sudo yum -y install fedora-packager rpm-sign nosync yum-utils gnupg2

## Fedora

We assume you have a fresh install of Fedora with the following software 
installed:

    $ sudo dnf -y install fedora-packager rpm-sign nosync dnf-utils gnupg2 yum

If you want to perform cross compiles, e.g. for `aarch64`, also install 
`qemu-user-static`

## Mock

Make sure your current user account is a member of the `mock` group:

    $ sudo usermod -a -G mock $(id -un)

## Repository

Clone the `eduVPN/documentation` repository:

    $ git clone https://github.com/eduVPN/documentation.git
	$ cd documentation
	$ git checkout v2

## Setup

Run `release/builder_setup.sh` with the user account you are going to 
build as.

	$ release/builder_setup.sh
	
This will create a GPG key and setup various configuration files. Check 
the file if you are curious, it is very simple!

# Building

    $ cd documentation
    $ release/centos_7_x86_64.sh           # run this on CentOS 7
    $ release/fedora_${VERSION}_x86_64.sh  # run this on Fedora
    $ release/fedora_${VERSION}_aarch64.sh # run this on Fedora

This will put all RPMs and source RPMs in the `${HOME}/repo` directory and 
create a tarball in `${HOME}` as well with the name 
`rpmRepo-<PLATFORM>-<DATE>.tar.gz`. This file will contain all files from 
`${HOME}/repo`. If you run the release script multiple times, e.g. run it 
again after a package update, the new RPM and source RPM will be added to the 
`${HOME}/repo` directory and the tarball as well. A history of old packages is 
retained, so it can be beneficial to retain the `${HOME}/repo` folder between
builds.

# Updating

If you want to create packages of updated software, just pull the last version
of the repository:

    $ git pull

And then, run the build script(s) again, see above. This should add any new 
packages in `${HOME}/repo` as well as put them in the generated tarball.

# Configuration

Create the following snippet in `/etc/yum.repos.d/LC.repo` on the machine where 
you want to install Let's Connect!. Make sure the files can be found on the URLs 
mentioned below:

## CentOS / Red Hat Enterprise Linux >= 7

    [LC]
    name=Let's Connect! Packages (EL $releasever)
    baseurl=https://repo.letsconnect-vpn.org/rpm/release/enterprise/$releasever/$basearch
    gpgcheck=1
    enabled=1
    gpgkey=https://repo.letsconnect-vpn.org/rpm/release/RPM-GPG-KEY-LC

## Fedora

    [LC]
    name=Let's Connect! Packages (Fedora $releasever) 
    baseurl=https://repo.letsconnect-vpn.org/rpm/release/fedora/$releasever/$basearch
    gpgcheck=1
    enabled=1
    gpgkey=https://repo.letsconnect-vpn.org/rpm/release/RPM-GPG-KEY-LC
