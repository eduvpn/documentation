# Upgrade Debian 10 to Debian 11

First, make sure your Debian 10 system is fully up to date and reboot it:

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
[here](https://www.debian.org/releases/bullseye/amd64/release-notes/ch-upgrading.en.html). 

These are the official Debian upgrade instructions. You can and SHOULD follow 
that document and read all sections and perform the steps when necessary. Do 
**not** remove the "non-Debian packages" (4.2.2) as all packages are also 
available on Debian 11 and will be upgraded without trouble. You **do** need to
pay attention to "Changed security archive layout" (5.1.3) as the security 
updates will require a different `deb` line in `/etc/apt/sources.list`.

Pay attention the the cleanup as well (sections 4.7, 4.8). When updating the 
repositories (section 4.3) also make sure you update 
`/etc/apt/sources.list.d/eduVPN_v2.list` and replace `buster` with `bullseye`, 
i.e.:

```
$ echo "deb https://repo.eduvpn.org/v2/deb bullseye main" | sudo tee /etc/apt/sources.list.d/eduVPN_v2.list
```

**NOTE**: if `/etc/apt/sources.list.d/eduVPN_v2.list` does not yet exist, 
create it and remove all other files related to "eduVPN" or "LC" from 
`/etc/apt/sources.list.d` that may have been put there in the past!

After the update is complete, PHP will not be properly configured yet, this is 
because the version changed from 7.3 to 7.4 and is part of a different Apache
configuration. You have to manually re-enable PHP:

```
$ sudo a2enconf php7.4-fpm
```

In case you also modified the PHP configuration options, as suggested e.g. 
[here](DEPLOY_DEBIAN.md#php), you need to reapply those as well and restart 
PHP, to restart PHP:

```
$ sudo systemctl restart php7.4-fpm
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
