# Release

This document describes how to create an RPM repository containing all the 
software built from scratch and signed with PGP. This will perform a FULL 
build.

# Preparation

We assume you have a fresh CentOS 7 machine, add the following software to it. 

    $ sudo yum -y install epel-release
    $ sudo yum -y install fedora-packager docker rpm-sign

Enable and start Docker:

    $ sudo systemctl enable docker
    $ sudo systemctl start docker

Clone the `eduVPN/documentation` repository:

    $ git clone https://github.com/eduVPN/documentation.git

# Creating SRPMs

First we need to generate the SRPMs files for the software.

    $ cd $HOME
    $ rpmdev-setuptree
    $ cd $HOME/documentation/rpm

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

    $ cd $HOME/documentation/release

Create the Docker builder image:

    $ sudo docker build -t eduvpn/builder .

Now we can use this Docker image to build the RPM files. The reason we do this
in this way is that we have a "clean" environment for every package build.

Every package that gets built will be added to the repository available to the
Docker image. This way, all dependencies get pulled in and we can find out if
there are any problems in the build, e.g. missing dependencies.

    $ export PKGS=(\
        php-bacon-bacon-qr-code\
        php-christian-riesen-otp\
        php-fkooman-oauth2-client\
        php-fkooman-oauth2-server\
        php-fkooman-yubitwee\
        php-fkooman-secookie\
        vpn-lib-common\
        vpn-admin-portal\
        vpn-server-api\
        vpn-server-node\
        vpn-user-portal\
        php-saml-ds\
      )

    $ for i in "${PKGS[@]}"; do sudo docker run --rm -v $HOME/rpmbuild:/rpm:Z -i -t eduvpn/builder /build.sh $(basename $(ls $HOME/rpmbuild/SRPMS/$i*.src.rpm)); done

This should build all the packages and also have a fully functional YUM 
repository in `$HOME/rpmbuild`.

# Signing Packages

Create a GPG signing key:

    $ gpg --gen-key

Export the key, assuming you used `eduvpn@surfnet.nl` as the email address for
the GPG key.

    $ gpg --export -a 'eduvpn@surfnet.nl' > RPM-GPG-KEY-eduVPN

This `RPM-GPG-KEY-eduVPN` needs to be distributed to the nodes that want to 
install the software and imported there:

    $ sudo rpm --import RPM-GPG-KEY-eduVPN

Add the following to `$HOME/.rpmmacros`:

    %_signature gpg
    %_gpg_name eduvpn@surfnet.nl
    %_gpg_digest_algo sha256

Change owner, Docker made all files owned by the `root` user.

    $ sudo chown -R $(id -u).$(id -g) $HOME/rpmbuild

Sign all (S)RPM packages:

    $ rpm --addsign $HOME/rpmbuild/RPMS/noarch/* $HOME/rpmbuild/SRPMS/*

(Re)create the repository data:

    $ createrepo_c $HOME/rpmbuild

Sign the metadata:

    $ gpg --detach-sign --digest-algo sha256 --armor $HOME/rpmbuild/repodata/repomd.xml

That's all! Now copy the `$HOME/rpmbuild` to a web server and create the 
following snippet in `/etc/yum.repos.d/eduVPN.repo`:

    [eduVPN]
    name=eduVPN
    baseurl=https://static.eduvpn.nl/rpm/
    gpgcheck=1
    repo_gpgcheck=1
    enabled=1
    gpgkey=https://static.eduvpn.nl/rpm/RPM-GPG-KEY-eduVPN
    skip_if_unavailable=False

That's all!

# Updating

If a package gets updated, pull the repository and for all changed packages
run the following tools as instructed above, or individually from the `rpm/` 
directory:

* `spectool -g -R file.spec`;
* `rpmbuild -bs file.spec`;

You can then set the `PKGS` variable to only contain the updated package 
names and run the `docker` command again.

Do not forget to sign the repository and metadata again.

# Sources

* https://blog.packagecloud.io/eng/2014/11/24/howto-gpg-sign-verify-rpm-packages-yum-repositories/

