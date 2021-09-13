# Install Updates

This document will explain how to update your VPN server(s). This document is 
split in two parts:

1. Update your single server/VM installation;
2. Update your multi server/VM installation, i.e. a controller with one or more
   nodes.

These instructions apply to the official installation instructions using the 
`deploy_${DIST}.sh` scripts. If you installed the servers in a different way 
then some changes MAY be necessary!

**NOTE**: make sure you installed the `vpn-maint-scripts` package and use the 
correct [repositories](REPO.md).

# Single Server

All that is needed is run the following command:

```
$ sudo vpn-maint-update-system
```

You SHOULD run this in a `tmux` session in case the SSH connection is lost 
during the upgrade process.

In case there are updates to system components/libraries or the kernel you MUST 
reboot the system.

# Multi Server

We will assume that you have one controller and one node. If you have multiple
nodes you can modify the instructions accordingly.

You SHOULD designate a system as your "management host" from which your run the
update script. You can use e.g. your own laptop or a VM running on your system.

This device MUST have SSH access (with SSH public key authentication) to the
controller and node(s).

Make sure you install `tmux` on all machines. This tool is useful when the
connection to your controller and node(s) is lost, e.g. due to network issues 
while running the update process.

On your management host, download the 
[vpn-maint-update-system-multi](https://git.sr.ht/~fkooman/vpn-maint-scripts/tree/main/item/bin/vpn-maint-update-system-multi) script. We are using a script
because we want to first stop the nodes, then update the controller, then 
update the nodes and (re)start the nodes. This in order to make sure all 
clients are disconnected first before stopping the controller. That way we do 
not lose any disconnect events in the log.

Create a file `server.list` that contains your controller and node(s) 
hostname.

```
CONTROLLER="vpn.example.org"
NODES="node1.vpn.example.org node2.vpn.example.org"
```

Now you can run the `vpn-maint-update-system-multi` script:

```
$ sh vpn-maint-update-system-multi
```

The script also takes the `--reboot` flag that reboots all node(s) and 
controller in the right order.
