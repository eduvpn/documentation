# Release

This document describes how to create an RPM repository containing all the 
software built from scratch and signed with PGP. This will perform a FULL 
build.

# Preparation

We assume you have a fresh CentOS 7 machine, add the following software to it. 

    $ sudo yum -y install epel-release
    $ sudo yum -y install fedora-packager rpm-sign nosync

Make sure your current user account is a member of the `mock` group:

    $ sudo usermod -a -G mock myusername

After this, make sure you logout and in again.

Make sure you have a PGP key available. If not, create one:

    $ gpg --gen-key

Do **NOT** use a passphrase. Add the following to `${HOME}/.rpmmacros`, 
assuming the email address you used is `eduvpn@surfnet.nl`:

    %_signature gpg
    %_gpg_name eduvpn@surfnet.nl
    %_gpg_digest_algo sha256

Create a Mock configuration file in `${HOME}/.config/mock.cfg`:

    # Automatically Sign Packages
    config_opts['plugin_conf']['sign_enable'] = True
    config_opts['plugin_conf']['sign_opts'] = {}
    config_opts['plugin_conf']['sign_opts']['cmd'] = 'rpmsign'
    config_opts['plugin_conf']['sign_opts']['opts'] = '--addsign %(rpms)s'

    # use YUM (for CentOS 7)
    config_opts['package_manager'] = 'yum'
    
    # Speed up package installation in Mock
    config_opts['nosync'] = True

To export the public key, for use by clients using this repository:

    $ gpg --export -a 'eduvpn@surfnet.nl' > RPM-GPG-KEY-eduVPN

Clone the `eduVPN/documentation` repository:

    $ git clone https://github.com/eduVPN/documentation.git

# Building

    $ cd documentation
    $ sh release/build.sh

# Configuration

Create the following snippet in `/etc/yum.repos.d/eduVPN.repo` on the machine
where you want to install eduVPN. Make sure the files can be found on the URLs
mentioned below:

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

