# Update OpenVPN

**NOTE**: we recommend to upgrade to Debian 11 instead of using the OpenVPN 
backport!

This document will show you how to update OpenVPN on your Debian 10 server
to the version from the 
[buster-backports](https://packages.debian.org/buster-backports/openvpn) 
repository. It contains 
[OpenVPN 2.5](https://github.com/OpenVPN/openvpn/blob/release/2.5/Changes.rst#overview-of-changes-in-250) 
instead of OpenVPN 2.4, which is part of `buster`.

**NOTE**: there is NO real need to do this and we consider this experimental!

## Enable Backports

First enable [backports](https://backports.debian.org/), we summerize the 
instructions as per the site linked to:

Add this line to `/etc/apt/sources.list`:

    deb http://deb.debian.org/debian buster-backports main
    
Run:

    $ sudo apt update

## Install OpenVPN from Backports

Install OpenVPN from backports:

    $ sudo apt install openvpn/buster-backports

We need to restart OpenVPN as the package update will not do that. The easiest
way to do this is to "apply changes":

    $ sudo vpn-maint-apply-changes
    
Now you should be running OpenVPN 2.5.
