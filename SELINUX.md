# SELinux

If you used `deploy.sh` your VPN server has SELinux fully enabled and 
configured. If you make changes to the configuration, you may need to update
the SELinux configuration.

# OpenVPN 

By default, OpenVPN is not allowed to listen on any other ports than `udp/1194` 
and `tcp/1194`. The `deploy.sh` script added some ports to be able to connect
to the management ports of the OpenVPN processes.

However, if you want to use more OpenVPN processes, e.g. by listening on 
additional ports, or by adding additional profiles this may not be enough.

To see what is currently configured you can use `semanage`. On a "clean" 
CentOS system you'll see the following:

    $ sudo semanage port -l | grep openvpn
    openvpn_port_t                 tcp      1194
    openvpn_port_t                 udp      1194

On a system that already ran `deploy.sh`, you'll see the following output, it
has the management ports 11940-11955 added:

    openvpn_port_t                 tcp      11940-11955, 1194
    openvpn_port_t                 udp      1194

Every deploy supports 16 profiles, and each profile supports 16 OpenVPN 
processes, fully used this would require 16x16 = 256 management ports, if you
want to configure this:

Delete the existing port definition:

    semanage port -d -t openvpn_port_t -p tcp 11940-11955

Add the new one:

    semanage port -a -t openvpn_port_t -p tcp 11940-12195

If you want to specify additional ports for OpenVPN to listen on for client 
connections, you can do something similar:

    semanage port -a -t openvpn_port_t -p tcp 1195-1201
    semanage port -a -t openvpn_port_t -p udp 1195-1201

This will allow OpenVPN to listen on ports `1194-1201` for both TCP and UDP.
