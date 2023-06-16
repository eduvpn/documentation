# Upgrade Debian 11 to Debian 12

First, make sure your Debian 11 system is fully up to date and reboot it:

```
$ sudo vpn-maint-update-system
$ sudo reboot
```

Now test that everything still works properly, to make sure that you start from
a working "base".

**NOTE**: if you have the opportunity, please make a snapshot of your system, 
e.g. through your VM platform so you can rollback immediately if the upgrade
doesn't work.
 
Follow the instructions 
[here](https://www.debian.org/releases/bookworm/amd64/release-notes/ch-upgrading.en.html). 

These are the official Debian upgrade instructions. You can and SHOULD follow 
that document and read all sections and perform the steps when necessary. Do 
**not** remove the "non-Debian packages" (4.2.6) as all packages are also 
available on Debian 12 and will be upgraded without trouble.

Pay attention the the cleanup as well (sections 4.7, 4.8). When updating the 
repositories (section 4.3) also make sure you update 
`/etc/apt/sources.list.d/eduVPN_v2.list` and replace `bullseye` with 
`bookworm`, i.e.:

```
$ echo "deb https://repo.eduvpn.org/v2/deb bookworm main" | sudo tee /etc/apt/sources.list.d/eduVPN_v2.list
```

**NOTE**: if `/etc/apt/sources.list.d/eduVPN_v2.list` does not yet exist, 
create it and remove all other files related to "eduVPN" or "LC" from 
`/etc/apt/sources.list.d` that may have been put there in the past!

After the update is complete, PHP will not be properly configured yet, this is 
because the version changed from 7.4 to 8.2 and is part of a different Apache
configuration. You have to manually re-enable PHP:

```
$ sudo a2enconf php8.2-fpm
```

In case you also modified the PHP configuration options, as suggested e.g. 
[here](DEPLOY_DEBIAN.md#php), you need to reapply those as well and restart 
PHP, to restart PHP:

```
$ sudo systemctl restart php8.2-fpm
```

Restart Apache:

```
$ sudo systemctl restart apache2
```

Run the following scripts to make sure all is in order:

```
$ sudo vpn-maint-apply-changes
$ sudo vpn-maint-update-system
```

This should all run without any error and without asking any questions! Reboot 
your server after this and make sure everything still works. Try logging in to 
the portal, connect with a VPN client.

## Step by Step

On a typical system, the below instructions will upgrade your server without 
having to read through all the instructions listed above. Please look at every 
line and make sure you understand it. This ONLY works for systems
that were installed with `deploy_debian.sh` and are fairly standard clean 
Debian installations. If your organization (heavily) modifies standard Debian
you MAY run into trouble! You've been warned! :-)

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
# change to bookworm repo
$ sudo find /etc/apt \
    -type f -name '*.list' \
    -exec sed -i 's/bullseye/bookworm/g' {} +

# perform update/upgrade
$ sudo apt update
$ sudo apt full-upgrade

# enable php-fpm 8.2 (upgrade from 7.4 in Debian 11)
$ sudo a2enconf php8.2-fpm
```

Now, reboot your system and make sure everything still works. Then you can 
continue to perform some additional cleanup steps:

```bash
$ sudo apt autoremove
$ apt list "~o"
$ sudo apt purge "~o"
$ apt list "~c"
$ sudo apt purge "~c"
```

After this is complete, you can reboot again. Make sure all comes back as 
expected and your VPN still works.
