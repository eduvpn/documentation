# Introduction

Since 2020-05-05 the package `vpn-maint-scripts` is available in the package
repositories and from this day on will be installed automatically on new 
deployments using the `deploy_${DIST}.sh` scripts. If you deployed before this 
moment, you may need to install the package manually first.

This document is for deploys where only 1 server is involved. For multi node 
maintenance instructions, you can go [here](MULTI_NODE.md#maintenance).

## CentOS / Red Hat Enterprise Linux

    $ sudo yum install vpn-maint-scripts

## Fedora

    $ sudo dnf install vpn-maint-scripts

## Debian

    $ sudo apt install vpn-maint-scripts

# Apply Configuration Changes

In order to apply changes, run the following command:

    $ sudo vpn-maint-apply-changes

# Install Updates

In order to install OS updates and VPN server updates, run the following 
command periodically, e.g. every week during a maintainance windows:

    $ sudo vpn-maint-update-system

**NOTE**: you may also need to reboot your server in case the kernel or system
libraries were updated!
