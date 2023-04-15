# SELinux

If you used the `deploy_${DIST}.sh` script on CentOS, Red Hat Enterprise Linux 
or Fedora, your VPN server has SELinux fully enabled and configured. If you 
make changes to the configuration, you MAY need to update the SELinux 
configuration.

## OpenVPN 

By default, OpenVPN is not allowed to listen on any other ports than `udp/1194` 
and `tcp/1194`. The `deploy_${DIST}.sh` script added some ports to be able to 
connect to the management ports of the OpenVPN processes and to allow client 
connections on other ports as well.

However, if you want to use more OpenVPN processes, e.g. by listening on 
additional ports, this may not be enough.

To see what is currently configured you can use `semanage`. On a "clean" 
CentOS system you'll see the following:

    $ sudo semanage port -l | grep openvpn
    openvpn_port_t                 tcp      1194
    openvpn_port_t                 udp      1194

On a system that already ran `deploy_${DIST}.sh`, you'll see the following 
output, it has the management ports 11940-12195 and client connection ports 
1195-1263 added:

    openvpn_port_t                 tcp      1195-1263, 11940-12195, 1194
    openvpn_port_t                 udp      1195-1263, 1194

If you want to specify additional ports for OpenVPN to listen on for client 
connections, you can do something similar:

    $ sudo semanage port -a -t openvpn_port_t -p tcp 1264-1327
    $ sudo semanage port -a -t openvpn_port_t -p udp 1264-1327

This will allow OpenVPN to listen on ports `1264-1327` for both TCP and UDP in
addition.
