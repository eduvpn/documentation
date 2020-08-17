# Migrating from Debian 9 to Debian 10

We split the migration from Debian 9 to Debian 10 in two parts:

1. Switch to new package repository;
2. Upgrade to Debian 10

We split this procedure in two parts as it becomes much easier and you are not
fighting two battles at the same time.

The new repository contains packages for both Debian 9 and Debian 10, they are 
based on the same package descriptions. A little care has to be taken when 
upgrading to the new repository as they use the proper Debian way to handle 
configuration files and various other aspects that were hacked around in the
old (Debian 9 only) packages.

## To New Package Repository

You can very easily upgrade your existing Debian 9 server to use the new 
repository, but care has to be taken.

First you have to remove `vpn-daemon` if it was installed on your Debian 9 
system, to check whether it was installed:

    $ dpkg -l vpn-daemon

If it shows that the package is installed, remove it and clean up the user that
was created by the old package install:

    $ sudo apt remove vpn-daemon
    $ sudo userdel vpn-daemon

Now you can switch to the new repository. Remove the file `/etc/apt/sources.list.d/LC.list`:

    $ sudo rm /etc/apt/sources.list.d/LC.list

Add the new repository file:

    $ echo "deb https://repo.eduvpn.org/v2/deb stretch main" | sudo tee /etc/apt/sources.list.d/eduVPN.list
    
Add the new PGP key:

    $ curl https://repo.eduvpn.org/v2/deb/debian.key | sudo apt-key add

Now you can update your system. All eduVPN packages will be replaced by the 
version from the new Debian 9 repository:

    $ sudo apt update
    $ sudo -s
    # DEBIAN_FRONTEND=noninteractive apt dist-upgrade

In case `vpn-daemon` was installed before, you can now reinstall it again:

    $ sudo apt install vpn-daemon

And optional enable it one boot and start it immediately:

    $ sudo systemctl enable --now vpn-daemon

## To Debian 10

This is a little more complicated.
