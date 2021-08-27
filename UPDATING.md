# Updating

This document will explain how to update your VPN server and how to keep it
up to date.

# Single Server Setup

These instructions are for the case when you have single VPN server that you 
installed using the `deploy_${DIST}.sh` script.

## Manual

Make sure you have the package `vpn-maint-scripts` installed, replace `apt` by 
`yum` (CentOS) or `dnf` (Fedora):

```
$ sudo apt install vpn-maint-scripts
```

Now run the following script:

```
$ sudo vpn-maint-update-system
```

You **MUST** reboot in case system libraries or the kernel are updated. It is
smart to reboot anyway after some updates were installed to make sure 
everything comes back properly.

If this command gives any errors regarding package repositories or keys, look 
[here](REPO.md) to make sure you have the proper repository and keys 
configured.

## Automatic

TBD.

# Multi Node Setup

## Manual

TBD.

## Automatic

TBD.
