# Release

This document describes how to create an RPM repository containing all the 
software built from scratch and signed with PGP. This will perform a FULL 
build.

# Preparation

We assume you have a fresh CentOS 7 machine, add the following software to it. 

    $ sudo yum -y install epel-release
    $ sudo yum -y install fedora-packager rpm-sign

Clone the `eduVPN/documentation` repository:

    $ git clone https://github.com/eduVPN/documentation.git

Make sure you have a PGP key available. If not, create one:

    $ gpg --gen-key

Add the following to `$HOME/.rpmmacros`, assuming the email address you used is
`eduvpn@surfnet.nl`:

    %_signature gpg
    %_gpg_name eduvpn@surfnet.nl
    %_gpg_digest_algo sha256

To export the public key:

    $ gpg --export -a 'eduvpn@surfnet.nl' > RPM-GPG-KEY-eduVPN

# Building

    $ cd documentation
    $ sh release/build.sh

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
	
# Sources

* https://blog.packagecloud.io/eng/2014/11/24/howto-gpg-sign-verify-rpm-packages-yum-repositories/

