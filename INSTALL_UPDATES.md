# Install Updates

This document will explain how to update your VPN server(s). This document is 
split in two parts:

1. Update your single server/VM installation;
2. Update your multi server/VM installation, i.e. a controller with one or more
   nodes, installed as per the multi node [instructions](MULTI_NODE.md).

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

If you are running a setup with a separate controller and node(s), you will 
need to consider some extra things when installing updates. It is best to stop
the node(s) first, so as the clients are forcefully disconnected that event can
still be properly written to the log.

The instructions below consider one controller `vpn.example.org` and two nodes,
`node-a.vpn.example.org` and `node-b.vpn.example.org`.

The best is to designate a (separate) system as the "management system" from 
which you will run the update command. This can be your own laptop or a VM on 
your laptop dedicated to this. This system MUST be able to access the 
controller and node(s) through SSH without password (public key authentication)
and have _sudo_ permissions to execute the required scripts. This is similar to
the requirement for using e.g. Ansible.

Make sure you also install `tmux` on all machines. This update commands will be
run in `tmux` so there is less of a problem when the connection to your 
controller and node(s) is lost, e.g. due to network issues while running the 
update process. We assume you are familiar with `tmux`, i.e. detach/attach from 
sessions. This knowledge is only necessary in case you actually lose the 
connectivity.

On your management system, download the 
[vpn-maint-update-system-multi](https://git.sr.ht/~fkooman/vpn-maint-scripts/tree/main/item/bin/vpn-maint-update-system-multi)
script.

This script makes sure all steps are executed in the correct order. It also 
allows you to reboot the systems after updating using the `--reboot` flag. 

Create a file `server.list` that contains your controller and node(s) 
hostnames.

```
CONTROLLER="vpn.example.org"
NODES="node-a.vpn.example.org node-b.vpn.example.org"
```

Now you can run the `vpn-maint-update-system-multi` script:

**NOTE**: make sure you are NOT connected to the VPN provided by the server 
you are going to update as you'll lose your connection and the update might not
complete successfully!

```
$ sh vpn-maint-update-system-multi
```

As mentioned, the script also takes the `--reboot` flag that reboots all 
node(s) and controller in the right order, e.g.:

```
$ sh vpn-maint-update-system-multi --reboot
```
