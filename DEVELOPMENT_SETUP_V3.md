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

We assume you will be using either Fedora >= 33, or Debian >= 10. Other 
distributions will also work, but some minor details, regarding installation of 
the required software, will be different.

**NOTE**: if you try to build a package repository you need to be on the 
respective OS: for DEB packages you need to be on Debian, for Fedora/CentOS 
packages you need to be on Fedora.

# Fedora >= 33

When you are not running Fedora as your desktop OS, it is easiest to install a
VM with a desktop. In addition, install the required software (dependencies):

```
$ sudo dnf -y install golang php-cli git composer php-date php-filter php-hash \
    php-json php-mbstring php-pcre php-pdo php-spl php-sodium php-curl php-gd \
    unzip
```

# Debian >= 11

When you are not running Debian as your desktop OS, it is easiest to install a
VM with a desktop. In addition, install the required software (dependencies):

```
$ sudo apt install curl git build-essential php-gmp php-sqlite3 composer \
    php-curl php-xml php-cli unzip golang-go
```

# Installation

Download the `development_setup_v3.sh` script from this repository and run it. 
It will by default create a directory `${HOME}/Project/eduVPN-v3` under which 
everything will be installed. No `root` is required!

```
$ curl -L -O https://raw.githubusercontent.com/eduvpn/documentation/v3/development_setup_v3.sh
$ sh ./development_setup_v3.sh
```

# Testing

All projects have unit tests included, they can be run from the project folder,
e.g.: 

    $ cd ${HOME}/Projects/eduVPN-v3/vpn-user-portal
    $ vendor/bin/phpunit

# Using

A "launch" script is included to run the PHP built-in web server to be able
to easily test the portals.

    $ cd ${HOME}/Projects/eduVPN-v3
    $ sh ./launch.sh

Now with your browser you can connect to the user portal on 
`http://localhost:8082/`.

You can login with the users `foo` and password `bar` or `admin` with password 
`secret`.

# VPN Configuration

To generate the OpenVPN server configuration files:

    $ cd ${HOME}/Projects/eduVPN-v3/vpn-server-node
    $ php bin/server-config.php

The configuration will be stored in the `openvpn-config` folder.

# Modifying Code

If you want to modify any of your code, it makes sense to switch to using your
own "fork". We'll only consider the eduVPN/LC components here and not the 
underlying dependencies.

For example if you want to modify `vpn-user-portal` you can do the following, 
we assume you already have an empty `vpn-user-portal` repository created on 
GitHub:

```
$ mkdir ${HOME}/tmp && cd ${HOME}/tmp
$ git clone --bare https://git.sr.ht/~fkooman/vpn-user-portal
$ cd vpn-user-portal
$ git push --mirror git@github.com/fkooman/vpn-user-portal
```

You can add GitHub as a remote now to your project checkout of 
`vpn-user-portal`:

```
$ cd ${HOME}/Projects/eduVPN-v3/vpn-user-portal
$ git remote add github git@github.com/fkooman/vpn-user-portal
```

Now when you make changes to the code you can push them to your own repository
"fork"

```
$ git branch my-feature-branch
$ git checkout my-feature-branch
...
$ git commit -a -m 'implement feature X'
$ git push github my-feature-branch
```

If this works properly locally, you can send a "pull request" or 
"merge request" to the upstream project, or even create a package repository
containing your own version of `vpn-user-portal` if necessary! 

When working with RPM packages for CentOS/Fedora you can easily create a 
package from a commit. For DEB packages you need to make a release first. What
I am doing is developing on CentOS/Fedora and only when considered stable I'll
make a release after which I also create Debian packages.

# Creating RPM packages

First install all requirements on your Fedora system as described 
[here](https://git.sr.ht/~fkooman/builder.rpm).

So we assume you have your own fork of `vpn-user-portal` as shown above. Now 
how to create an RPM package for it in your own development repository?

The `vpn-user-portal` package also has an RPM package repository, we assume you 
already have an empty `vpn-user-portal.rpm` repository created on GitHub::

```
$ mkdir ${HOME}/tmp && cd ${HOME}/tmp
$ git clone --bare https://git.sr.ht/~fkooman/vpn-user-portal.rpm
$ cd vpn-user-portal.rpm
$ git push --mirror git@github.com/fkooman/vpn-user-portal.rpm
```

Add the new remote to `rpm/vpn-user-portal.rpm`:

```
$ cd ${HOME}/Projects/eduVPN-v3/rpm/vpn-user-portal.rpm
$ git remote add github git@github.com/fkooman/vpn-user-portal.rpm
```

Now you can modify the SPEC file under 
`vpn-user-portal.rpm/SPECS/vpn-user-portal.spec` to point to your Git 
repository and commit. 

Modify the following lines, point `%global git` to your Git commit:

```
%global git 925933279f8f4b99e242d4c154be7c6c55aa91e6

Version:    2.4.8
Release:    0.1%{?dist}

...

Source0: https://github.com/fkooman/vpn-user-portal/archive/%{git}.tar.gz

...

%changelog
* Tue Feb 09 2021 François Kooman <fkooman@tuxed.net> - 2.4.8-0.1
- update to development package
```

Set `Version` to one higher than the current version.
The `0.1` in the `Release` field indicates it is a pre-release version. Also 
update the `%changelog` entry.

You can try to build this package locally:

```
$ rpmdev-setuptree
$ cd ${HOME}/Projects/eduVPN-v3/rpm/vpn-user-portal.rpm
$ spectool -g -R SPECS/vpn-user-portal.spec
$ cp SOURCES/* ${HOME}/rpmbuild/SOURCES
$ rpmbuild -bs SPECS/vpn-user-portal.spec
$ rpmbuild -bb SPECS/vpn-user-portal.spec
```

Then you can commit your changes:

```
$ git commit -a -m 'update to development package'
$ git push github
```

Once this is complete, you can continue and create your own package repository 
by following the instructions [here](https://git.sr.ht/~fkooman/builder.rpm). 
Make sure you update `REPO_URL_BRANCH_LIST` and point it to your fork of the 
`vpn-user-portal.rpm` package.

If all goes well, you'll end up with your own RPM repository with your fork
of the package in it!

# Software Releases

The following script is used to make official releases of the components as 
`tar.xz`. It signs the source code with both PGP (for the Debian packages) and
with [Minisign](https://jedisct1.github.io/minisign/) for Fedora/CentOS. 
Please setup your own PGP and Minisign keys before running this script.

`${HOME}/.local/bin/make_release`:

```
#!/bin/sh
PROJECT_NAME=$(basename "${PWD}")
PROJECT_VERSION=${1}
RELEASE_DIR="${PWD}/release"

if [ -z "${1}" ]
then
    # we take the last "tag" of the Git repository as version
    PROJECT_VERSION=$(git describe --abbrev=0 --tags)
    echo Version: "${PROJECT_VERSION}"
fi

mkdir -p "${RELEASE_DIR}"
if [ -f "${RELEASE_DIR}/${PROJECT_NAME}-${PROJECT_VERSION}.tar.xz" ]
then
    echo "Version ${PROJECT_VERSION} already has a release!"
    exit 1
fi

git archive --prefix "${PROJECT_NAME}-${PROJECT_VERSION}/" "${PROJECT_VERSION}" -o "${RELEASE_DIR}/${PROJECT_NAME}-${PROJECT_VERSION}.tar.xz"
gpg2 --armor --detach-sign "${RELEASE_DIR}/${PROJECT_NAME}-${PROJECT_VERSION}.tar.xz"
minisign -Sm "${RELEASE_DIR}/${PROJECT_NAME}-${PROJECT_VERSION}.tar.xz"
```

Make the script executable:

    $ chmod +x ${HOME}/.local/bin/make_release

In order to upload the release, I'm using the `sr.ht` API. I am storing this
file under `${HOME}/.local/bin/sr.ht_upload_release`. You'll need to update the
locations. For other source hosting platforms it will be different.

```
#!/bin/sh
#POST /api/:username/repos/:name/artifacts/:ref
#
#Attaches a file artifact to the specified ref.
#
#Note: this endpoint does not accept JSON. Submit your request as multipart/form-data, with a single field: "file".

V=$(git describe --abbrev=0 --tags)
B=$(cat ${HOME}/.config/sr.ht/api.key)
R=$(basename $(pwd))

for F in release/*${V}*; do
	curl -H "Authorization: Bearer ${B}" -F "file=@${F}" "https://git.sr.ht/api/~fkooman/repos/${R}/artifacts/${V}"
done
```

# Creating DEB packages

Debian packages currently only work from proper releases. Updating the Debian 
packages is described [here](https://git.sr.ht/~fkooman/builder.deb). You can
also use your own `vpn-user-portal.deb` fork to get going. Follow the 
instructions there.
