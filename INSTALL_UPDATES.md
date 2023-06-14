# Installing Updates

This document will explain how to update your VPN server(s). 

These instructions apply to the official installation instructions using the 
`deploy_${DIST}.sh` scripts. If you installed the servers in a different way 
then some changes MAY be necessary!

## Single Server

All that is needed is run the following command on your VPN server:

```
$ sudo vpn-maint-update-system
```

You SHOULD run this in a `tmux` session. This is to prevent trouble when your 
SSH connection is lost during the upgrade process, for example when you 
connected over SSH to the server while the VPN connection to that same server
was up.

**NOTE**: in case there are updates to system components/libraries or the 
kernel you MUST reboot the system.

### Automatic Updates

Create the file `/etc/cron.weekly/vpn-maint-update-system` with the following
content:

```
#!/bin/sh
/usr/sbin/vpn-maint-update-system && /usr/sbin/reboot
```

Make it executable:

```bash
$ sudo chmod +x /etc/cron.weekly/vpn-maint-update-system
```

This is the easiest approach, but not necessarily resulting in the least 
amount of downtime. If you are actively maintaining your server(s) you may be
able to get away with not always rebooting. This just makes sure your server is
always up to date and by always rebooting there is no uncertainty whether or 
not updated system libraries are used, or you are running the latest kernel.

In case of security updates it MAY be necessary to schedule updates sooner than
the weekly update.

## Multi Server

See [vpn-maint-remote](https://git.sr.ht/~fkooman/vpn-maint-remote).
