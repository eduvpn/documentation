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

    $ cd $HOME/documentation/docker

Create the Docker builder image:

    $ sudo docker build -t eduvpn/builder .

Now we can use this Docker image to build the RPM files. The reason we do this
in this way is that we have a "clean" environment for every package build.

Every package that gets built will be added to the repository available to the
Docker image. This way, all dependencies get pulled in and we can find out if
there are any problems in the build, e.g. missing dependencies.

    $ export PKGS=(\
        php-bacon-bacon-qr-code\
        php-christian-riesen-base32\
        php-christian-riesen-otp\
        php-paragonie-constant-time-encoding\
        php-fkooman-oauth2-client\
        php-fkooman-oauth2-server\
        php-fkooman-yubitwee\
        vpn-lib-common\
        vpn-admin-portal\
        vpn-server-api\
        vpn-server-node\
        vpn-user-portal\
      )

    $ for i in "${PKGS[@]}"; do sudo docker run --rm -v $HOME/rpmbuild:/in:Z -v $HOME/rpmbuild:/out:Z -i -t eduvpn/builder /build.sh SRPMS/$(basename $(ls $HOME/rpmbuild/SRPMS/$i*.src.rpm)); done

This should build all the packages and also have a fully functional YUM 
repository in `$HOME/rpmbuild`.

# Signing Packages

Create a GPG signing key:

    $ gpg --gen-key

Export the key, assuming you used `eduvpn@surfnet.nl` as the email address for
the GPG key.

    $ gpg --export -a 'eduvpn@surfnet.nl' > RPM-GPG-KEY-eduvpn

This `RPM-GPG-KEY-eduvpn` needs to be distributed to the nodes that want to 
install the software and imported there:

    $ sudo rpm --import RPM-GPG-KEY-eduvpn

Add the following to `$HOME/.rpmmacros`:

    %_signature gpg
    %{_gpg_name} eduvpn@surfnet.nl
    %{_gpg_digest_algo} sha256

Change owner, Docker made all files owned by the `root` user.

    $ sudo chown -R $(id -u).$(id -g) $HOME/rpmbuild

Sign all packages:

    $ rpm --addsign $HOME/rpmbuild/RPMS/noarch/*

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
    gpgkey=https://static.eduvpn.nl/rpm/RPM-GPG-KEY-eduvpn
    skip_if_unavailable=False

That's all!

# Sources

* https://blog.packagecloud.io/eng/2014/11/24/howto-gpg-sign-verify-rpm-packages-yum-repositories/

