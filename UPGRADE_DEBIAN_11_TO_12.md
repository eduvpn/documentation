# Upgrade Debian 11 to Debian 12

This document will describe step-by-step how to update your eduVPN / Let's 
Connect! 2.x server from Debian 11 to Debian 12.

Official Debian release upgrade instructions can be found 
[here](https://www.debian.org/releases/bookworm/amd64/release-notes/ch-upgrading.en.html). 
You SHOULD review them carefully.

If you have the opportunity, you SHOULD make a snapshot of your system, e.g. 
through your VM platform so you can rollback immediately if the upgrade doesn't 
work.

## Step by Step

On a typical system, the below instructions will upgrade your server without 
having to read through the release upgrade instructions linked above. Please 
look at every line and make sure you understand it. This ONLY works for systems
that were installed with `deploy_debian.sh` and are fairly standard clean 
Debian installations. If your organization (heavily) modifies standard Debian
you MAY run into trouble! You have been warned! :-)

### Preparation

First, make sure your Debian 11 system is fully up to date and reboot it:

```bash
$ sudo vpn-maint-update-system
$ sudo reboot
```

Make sure everything (portal, apps, connecting to VPN) still works as 
expected before continuing. 

### Upgrade

The below commands SHOULD be enough to fully upgrade your system:

```bash
# change to bookworm repo for all repository configurations that mention 
# "bullseye"
$ sudo find /etc/apt \
    -type f -name '*.list' \
    -exec sed -i 's/bullseye/bookworm/g' {} +

# perform update/upgrade
$ sudo apt update
$ sudo apt full-upgrade

# enable php-fpm 8.2 (upgrade from 7.4 in Debian 11)
$ sudo a2enconf php8.2-fpm
```

In case you modified the PHP configuration options, as recommended 
[here](DEPLOY_DEBIAN.md#php), you need to reapply those as well for PHP 
version 8.2!

Now, reboot your system and make sure everything still works. Then you can 
continue to perform some additional cleanup steps:

```bash
$ sudo apt autoremove
$ apt list "~o"
$ sudo apt purge "~o"
$ apt list "~c"
$ sudo apt purge "~c"
```

To make sure you are running with the latest configuration applied, run this:

```bash
$ sudo vpn-maint-apply-changes
```

After this is complete, you can reboot again. Make sure all comes back as 
expected and your portal and VPN still works.
