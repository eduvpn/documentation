If you used the `deploy_${DIST}.sh` script on CentOS, Red Hat Enterprise Linux 
or Fedora, your VPN server has SELinux fully enabled and configured. If you 
make changes to the configuration, you MAY need to update the SELinux 
configuration.

# OpenVPN 

By default, OpenVPN is not allowed to listen on any other ports than `udp/1194` 
and `tcp/1194`.

If you want to use more OpenVPN processes, e.g. by listening on additional 
ports, this may not be enough.

To see what is currently configured you can use `semanage`. On a _clean_ Fedora 
system you'll see the following:

```bash
$ sudo semanage port -l | grep openvpn
openvpn_port_t                 tcp      1194
openvpn_port_t                 udp      1194
```

If you want to specify additional ports for OpenVPN to listen on for client 
connections, you can do something similar:

```bash
$ sudo semanage port -a -t openvpn_port_t -p tcp 1195-1200
$ sudo semanage port -a -t openvpn_port_t -p udp 1195-1200
```

This will also allow OpenVPN to listen on ports `1195-1200` for both TCP and 
UDP:

```bash
$ sudo semanage port -l | grep openvpn
openvpn_port_t                 tcp      1195-1200, 1194
openvpn_port_t                 udp      1195-1200, 1194
```
